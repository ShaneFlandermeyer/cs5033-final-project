from gnuradio import channels, gr, blocks, analog, digital
from signals.detail import detail
from abc import abstractmethod


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

        Parameters:
        -----------
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
