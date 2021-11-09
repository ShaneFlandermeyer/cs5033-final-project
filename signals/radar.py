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

    def __init__(self, waveform, name='RadarTransmitter', repeat=False, nSamps=None):
      gr.hier_block2.__init__(self, name,
                              gr.io_signature(0, 0, 0),
                              gr.io_signature(1, 1, gr.sizeof_gr_complex))
      self.data = waveform.sample()
      self.repeat = repeat
      self.src = blocks.vector_source_c(self.data, repeat)
      if nSamps is None:
        self.head = None
        self.connect(self.src,self)
      else:
        self.head = blocks.head(gr.sizeof_gr_complex, nSamps)
        self.connect(self.src, self.head, self)

    def set_data(self,data):
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
    # TODO: For now, assuming these object are immutable
    Parameters
    ----------

    """
    DETAIL_KEY="signal:detail"

    def __init__(self):
        self.detail=detail()
        self.label=''

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
                  TODO: Would be ideal to move this to the sample() method
    """

    def __init__(self, bandwidth, pulsewidth, sampRate, **kwargs):
        super().__init__()
        # Define metadata
        self.detail.type='analog'
        self.detail.modulation='fm'
        self.detail.bandwidth=bandwidth
        self.label='LFM'
        # Define actual waveform data
        self.bandwidth=bandwidth
        self.pulsewidth=pulsewidth
        self.sampRate=sampRate

    def sample(self):
        data=np.zeros((round(self.sampRate*self.pulsewidth)),
                        dtype=np.complex64)
        Ts=1 / self.sampRate
        t=np.arange(0, self.pulsewidth-Ts, Ts)
        phase=-self.bandwidth/2*t + self.bandwidth / \
            (2*self.pulsewidth)*(t**2)
        data=np.exp(1j*phase)
        return data


class SquareWaveform(RadarWaveform):
    """
    Defines a square waveform

    Parameters
    ----------
      - pulsewidth: The time duration of the waveform (s)
      - sampRate: The sampling rate of the waveform (Hz)
    """

    def __init__(self, pulsewidth, sampRate,**kwargs):
        super().__init__()
        # Define metadata
        self.detail.type='digital'
        self.detail.modulation='ask'
        self.label='Square'
        # Define waveform parameters
        self.pulsewidth=pulsewidth
        self.sampRate=sampRate
        self.bandwidth=1 / self.pulsewidth

    def sample(self):
        nSamps=round(self.sampRate*self.pulsewidth)
        return np.ones((nSamps,), dtype=np.complex64)


if __name__ == '__main__':
    bandwidth=1e6
    pulsewidth=100e-6
    sampRate=1e6
    wave=LinearFMWaveform(bandwidth, pulsewidth, sampRate)
    # Generate the flowgraph
    tb=gr.top_block()
    tx=wave.transmitter()
    sink=blocks.vector_sink_c()
    tb.connect(tx, sink)
    tb.run()
    wave.sampRate *= 2
    tx.set_data(wave.sample())
    sink.reset()
    tb.run()
    result = sink.data()
    plt.plot(result)
    plt.show()
