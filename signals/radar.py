from gnuradio.gr import top_block
from signals.detail import detail
from abc import abstractmethod
import numpy as np
import matplotlib.pyplot as plt
from gnuradio import gr, blocks

class RadarTransmitter(gr.hier_block2):
    """
    A class used for propagating signals from a waveform object through a GNU
    Radio flowgraph

    Parameters
    ----------
      - waveform: The waveform object to transmit
                  TODO: Allow this to be an array of samples
      - name: The name of the hierarchicial block
              Default: 'RadarTransmitter'
      - TODO: Add a pulse repetition frequency (PRF) parameter
    """

    def __init__(self, waveform, name='RadarTransmitter', nSamps=100):
        gr.hier_block2.__init__(self, name,
                                gr.io_signature(0, 0, 0),
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))
        src = blocks.vector_source_c(waveform.sample(), True)
        head = blocks.head(gr.sizeof_gr_complex, nSamps)
        self.connect(src, head, self)


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

    @abstractmethod
    def sample(self):
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
                  TODO: Would be ideal to move this to the sample() method
    """

    def __init__(self, bandwidth, pulsewidth, sampRate):
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
        """
        Generate a sampled version of this waveform

        Parameters
        ----------
          - self: The LFM object to generate
        """
        data = np.zeros((round(self.sampRate*self.pulsewidth)),
                        dtype=np.complex64)
        Ts = 1 / self.sampRate
        t = np.arange(0, self.pulsewidth-Ts, Ts)
        phase = -self.bandwidth/2*t + self.bandwidth / \
            (2*self.pulsewidth)*(t**2)
        data = np.exp(1j*phase)
        return data


if __name__ == '__main__':
    bandwidth = 1e6
    pulsewidth = 100e-6
    sampRate = 1e6
    lfm = LinearFMWaveform(bandwidth, pulsewidth, sampRate)
    # Generate the flowgraph
    tb = gr.top_block()
    tx = lfm.transmitter(name='RadarTransmitter',nSamps=int(sampRate*pulsewidth))
    # tx = RadarTransmitter(lfm,nSamps=int(sampRate*pulsewidth))
    sink = blocks.vector_sink_c()
    tb.connect(tx,sink)
    tb.run()
    plt.plot(np.real(sink.data()))
    plt.show()
    
