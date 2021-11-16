import numpy as np
from abc import abstractmethod
from gnuradio import gr, blocks, analog, digital
from signals.detail import detail

###############################################################################
# Radar Waveforms
###############################################################################


class RadarTransmitter(gr.hier_block2):
    """
    A class used for propagating signals from a waveform object through a GNU
    Radio flowgraph

    Parameters
    ----------
      - waveform: The waveform object to transmit
      - name: The name of the hierarchicial block
              Default: 'RadarTransmitter'
      - repeat: If true, the waveform is transmitted repeatedly until the
        flowgraph is stopped (either manually or by some other block)
    """

    def __init__(self, waveform, name='RadarTransmitter', repeat=False, nSamps=None):
        gr.hier_block2.__init__(self, name,
                                gr.io_signature(0, 0, 0),
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))
        # Data samples to transmit
        self.data = waveform.sample()
        self.repeat = repeat
        self.src = blocks.vector_source_c(self.data, repeat)
        if nSamps is None:
          # Transmit continuously
            self.head = None
            self.connect(self.src, self)
        else:
          # Stop transmitting after nSamps samples
            self.head = blocks.head(gr.sizeof_gr_complex, nSamps)
            self.connect(self.src, self.head, self)

    def set_data(self, data):
        """
        Change the transmitted data without creating a new object

        Parameters
        ----------
        - data: The new data vector to transmit
        """
        self.data = data
        self.src.set_data(data)

    def reset(self):
        """
        Reset the counter on the internal head block
        """
        if self.head is not None:
            self.head.reset()


class RadarWaveform():
    """
    An abstract parent class for all radar waveform objects
    Parameters
    ----------

    """
    DETAIL_KEY = "signal:detail"

    def __init__(self):
        self.detail = detail()
        self.label = ''

    @ abstractmethod
    def sample(self):
        """
        Generate a sampled version of this waveform

        Parameters
        ----------
          - self: The waveform object to be generated
        """
        pass

    def transmitter(self, **kwargs):
        """
        Return a RadarTransmitter object that will transmit this waveform

        Parameters:
        -----------
          - name: A string giving the name of the transmitter block
          - nSamps: The number of samples to transmit
        """
        return RadarTransmitter(self, **kwargs)


class LinearFMWaveform(RadarWaveform):
    """
    A class defining a linear frequency-modulated (LFM) waveform.

    Parameters
    ----------
      - bandwidth: The sweep bandwidth of the waveform (Hz)
      - pulsewidth: The time duration of the waveform (s)
      - sampRate: The sample rate of the waveform (Hz)
    """

    def __init__(self, bandwidth, pulsewidth, sampRate, **kwargs):
        super().__init__()
        # Define metadata
        self.detail.type = 'analog'
        self.detail.modulation = 'fm'
        self.detail.bandwidth = bandwidth
        self.label = 'LFM'
        # Define actual waveform data
        self.bandwidth = bandwidth
        self.pulsewidth = pulsewidth
        self.sampRate = sampRate

    def sample(self):
        data = np.zeros((round(self.sampRate*self.pulsewidth)),
                        dtype=np.complex64)
        Ts = 1 / self.sampRate
        t = np.arange(0, self.pulsewidth-Ts, Ts)
        phase = -self.bandwidth/2*t + self.bandwidth / \
            (2*self.pulsewidth)*(t**2)
        data = np.exp(1j*phase)
        return data


class SquareWaveform(RadarWaveform):
    """
    Defines a square waveform

    Parameters
    ----------
      - pulsewidth: The time duration of the waveform (s)
      - sampRate: The sampling rate of the waveform (Hz)
    """

    def __init__(self, pulsewidth, sampRate, **kwargs):
        super().__init__()
        # Define metadata
        self.detail.type = 'digital'
        self.detail.modulation = 'ask'
        self.label = 'Square'
        # Define waveform parameters
        self.pulsewidth = pulsewidth
        self.sampRate = sampRate
        self.bandwidth = 1 / self.pulsewidth

    def sample(self):
        nSamps = round(self.sampRate*self.pulsewidth)
        return np.ones((nSamps,), dtype=np.complex64)

###############################################################################
# Communications waveforms
###############################################################################


class CommunicationsTransmitter(gr.hier_block2):
    """
    A class used for propagating communications signals through a Python-based
    GNU Radio flowgraph

    Parameters:
    -----------
        - waveform: The CommunicationsWaveform object to transmit
        - src: The data bits to modulate
        - repeat: If true, repeats the waveform until the flowgraph is stopped
        - name: The name of the transmitter object
    """

    def __init__(self, waveform, src=None, repeat=False, name='CommunicationsTransmitter', **kwargs):
        gr.hier_block2.__init__(self, name,
                                gr.io_signature(0, 0, 0),
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))
        if src is None:
            # Modulate random bits
            self.data = analog.random_uniform_source_b(0, 256, 0)
        else:
            # Use a user-defined source block
            self.data = src
        # Create a modulator object from the waveform constellation
        self.modulator = digital.generic_mod(
            constellation=waveform.constellation,
            differential=waveform.differential,
            samples_per_symbol=waveform.sampsPerSym,
            pre_diff_code=True,
            excess_bw=waveform.excessBandwidth,
            verbose=False,
            log=False,
            truncate=False)
        # TODO: This should be based on the object parameters
        self.head = blocks.head(gr.sizeof_gr_complex, 8192)
        self.connect(self.data, self.modulator, self.head, self)

    def reset(self):
        """
        Reset the counter on the internal head block
        """
        self.head.reset()


class CommunicationsWaveform():
    """
    Define metadata and constellation types for various digital communications
    signals 

    Parameters
    ----------
        - differential: If true, the signal uses differential encoding
        - sps: Samples per symbol (should be >= 2, but this isn't enforced)
        - excessBandwidth: The bandwidth of the root-raised cosine filter beyond the Nyquist bandwidth
    """
    DETAIL_KEY = "signal:detail"

    def __init__(self, differential=False, sps=2, excessBandwidth=0.35, **kwargs):
        self.differential = differential
        self.sampsPerSym = sps
        self.excessBandwidth = excessBandwidth
        self.detail = detail()

    def transmitter(self, **kwargs):
        """
        Return a CommunicationsTransmitter object that will transmit this waveform
        """
        return CommunicationsTransmitter(self, **kwargs)


class psk(CommunicationsWaveform):
    """
    Object representing a general phase shift keying (PSK) constellation. 

    Parameters
    ----------
        - order: The order of the PSK constellation. This must be a power of 2
    """

    def __init__(self, order, **kwargs):
        CommunicationsWaveform.__init__(self, **kwargs)
        # Metadata
        self.detail.type = "digital"
        self.detail.modulation = "psk"
        self.detail.order = order


class qam(CommunicationsWaveform):
    """
    Object representing a quadratum amplitude modulation (QAM) constellation.

    Parameters
    ----------
        - order: The order of the QAM constellation. This must be a power of 2
    """

    def __init__(self, order, **kwargs):
        CommunicationsWaveform.__init__(self, **kwargs)
        # Metadata
        self.detail.type = "digital"
        self.detail.modulation = "qam"
        self.detail.order = order
        if order == 16:
            self.label = "16QAM"
            self.constellation = digital.constellation_16qam()


class bpsk(psk):
    """
    Object representing a binary phase shift keying (BPSK) constellation. 
    """

    def __init__(self, **kwargs):
        psk.__init__(self, order=2, **kwargs)
        self.label = "BPSK"
        self.constellation = digital.constellation_bpsk()


class qpsk(CommunicationsWaveform):
    def __init__(self, **kwargs):
        """
        Object representing a quadrature phase shift keying (QPSK) constellation.
        """
        psk.__init__(self, order=4, **kwargs)
        self.label = "QPSK"
        self.constellation = digital.constellation_qpsk()
