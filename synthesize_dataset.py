# %%
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from gnuradio import channels, gr, blocks, analog, digital
import datetime as dt
import random
import time
import sigmf
from sigmf import SigMFFile, sigmffile, utils
from signals.communications import *
from signals.radar import *
from tqdm import tqdm

# %% [markdown]
# ## Wishlist
# - Implement loop over different SNR values
# - Create a new channel model block
# - Parallelize everything

# %% [markdown]
# ## Data Processing Parameters

# %%
# Number of vectors per modulation class
nVecClass = 1
# Number of samples per class vector
nSampsVec = 128
# Loop through all the waveform types defined in this list
np.random.seed(0)
# waveforms = [LinearFMWaveform, SquareWaveform, bpsk, qpsk, qam(16)]
waveforms = [LinearFMWaveform]
# SNRs to simulate
snrs = np.arange(-20, 20, 2)
nClasses = len(waveforms)
nSampsTotal = nSampsVec*nVecClass*nClasses*len(snrs)
data = np.zeros((nSampsTotal,), dtype=np.complex64)
nSampsProduced = 0

# %% [markdown]
# ## Global Variables

# %%
# Modulation parameters
sampRate = 20e6
# Metadata setup
dataDir = 'data/'
filename = 'dataset'
# Create directory if it doesn't exist
Path(dataDir).mkdir(parents=True, exist_ok=True)
# Open and close the data file to create it if it doesn't exist. This is
# necessary for the SigMFFile object below
datafile = open(dataDir+filename+'.sigmf-data', 'w+')
datafile.close()
meta = SigMFFile(
    data_file=dataDir+filename+'.sigmf-data',
    global_info={
        # TODO: Determine the data type key programatically from the data array
        SigMFFile.DATATYPE_KEY: 'cf32_le',
        SigMFFile.SAMPLE_RATE_KEY: sampRate,
        SigMFFile.AUTHOR_KEY: 'Shane Flandermeyer, shane.flandermeyer@ou.edu',
        SigMFFile.DESCRIPTION_KEY: 'Synthetic RF dataset for machine learning',
        SigMFFile.VERSION_KEY: sigmf.__version__,
    }
)
# Channel parameters
# Signal-to-noise ration (dB)
# These values are uniformly distributed between -20 and 20
snr = np.random.rand(nVecClass)*40-20
noise_voltage = 10**(-snr/20)
# Maximum doppler frequency used in channel fading simulation
doppFreq = 1
# Fractional sample delays in the power delay profile
delays = [0.0, 0.9, 1.7]
# Magnitudes corresponding to the delays above
mags = [1, 0.8, 0.3]
# Length of the filter to interpolate the power delay profile over
nTaps = 8
# If true, the channel described by the parameters above will be simulatred
useChannelModel = True
# Waveform parameters
minBandwidth = 1e6
maxBandwidth = 100e6
minPulsewidth = 1e-6
maxPulsewidth = 100e-6
bandwidth = minBandwidth + \
    np.random.rand(nVecClass)*(maxBandwidth-minBandwidth)
pulsewidth = minPulsewidth + \
    np.random.rand(nVecClass)*(maxPulsewidth-minPulsewidth)

# %% [markdown]
# ## Main Simulation Loop

# %%
for snr in snrs:
    noise_voltage = 10**(-snr/20)
    channel = channels.dynamic_channel_model(
        sampRate, 0.01, 50, .01, 0.5e3, 8, doppFreq, True, 4, delays, mags, nTaps, noise_voltage, 0x1337)
    for wave in tqdm(waveforms):
        # Flowgraph
        tb = gr.top_block()
        # Create signal object and associated transmitter
        if callable(wave):
            sig = wave(bandwidth=bandwidth[0],
                       pulsewidth=pulsewidth[0], sampRate=sampRate)
        else:
            sig = wave
        tx = sig.transmitter(repeat=False)
        sink = blocks.vector_sink_c()
        # Create the flowgraph
        if useChannelModel:
            tb.connect(tx, channel, sink)
        else:
            tb.connect(tx, sink)
        # Generate nVecClass vectors of nSampsVec samples each
        for iVec in range(nVecClass):
            if isinstance(sig, RadarWaveform):
                # Create signal object and associated transmitter
                sig.bandwidth = bandwidth[iVec]
                sig.pulsewidth = pulsewidth[iVec]
                tx.set_data(sig.sample())
            # Run the simulation
            tb.run()
            # Choose a random subset of the data to add to the dataset. This ensures
            # that the model will get a broader variety of signals than if we saved
            # a fixed part of each signal
            startIdx = np.random.randint(0, len(sink.data())-nSampsVec)
            result = np.array(
                sink.data()[startIdx:startIdx+nSampsVec], dtype=np.complex64)
            # Save off the data and corresponding metadata
            # TODO: This gets slow when we try to generate lots of data
            detail = sig.detail
            sig.detail.snr = str(snr)
            metaDict = {
                SigMFFile.LABEL_KEY: sig.label,
                # TODO: This is horrible from a metadata perspective, but for
                # now the SNR will live in the comment field
                SigMFFile.DATETIME_KEY: dt.datetime.utcnow().isoformat()+'Z'}
            metaDict[sig.DETAIL_KEY] = detail.dict()
            meta.add_annotation(nSampsProduced, len(result), metadata=metaDict)
            # Normalize the energy to stay consistent with different modulations
            energy = np.sum(np.abs(result)**2)
            data[nSampsProduced:nSampsProduced+nSampsVec] = result/energy
            nSampsProduced += nSampsVec

# Check for mistakes and write to file
data.tofile(dataDir+filename+'.sigmf-data')
assert meta.validate()
# Write metadata to file
meta.tofile(dataDir+filename)
