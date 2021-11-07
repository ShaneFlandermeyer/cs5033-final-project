from signals.detail import detail
from abc import abstractmethod
import numpy as np
import matplotlib.pyplot as plt

class Waveform():
    """
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


class LinearFMWaveform(Waveform):
    """
    Parameters
    ----------
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
        data = np.zeros((round(self.sampRate*self.pulsewidth)), dtype=np.complex64)
        Ts = 1 / self.sampRate
        t = np.arange(0, self.pulsewidth-Ts, Ts)
        phase = -self.bandwidth/2*t + self.bandwidth / \
            (2*self.pulsewidth)*(t**2)
        data = np.exp(1j*phase)
        return data


if __name__ == '__main__':
    lfm = LinearFMWaveform(1e6, 100e-6, 1e6)
    plt.plot(np.real(lfm.sample()))
    plt.show()
