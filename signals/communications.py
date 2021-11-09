from gnuradio import channels, gr, blocks, analog, digital
from signals.detail import detail
from abc import abstractmethod


class CommunicationsTransmitter(gr.hier_block2):
    """
    A class used for propagating communications signals through a Python-based
    GNU Radio flowgraph
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
        # TODO: This should probably be done in the waveform classes
        self.modulator = digital.generic_mod(
            constellation=waveform.constellation,
            differential=False,
            samples_per_symbol=2,
            pre_diff_code=True,
            excess_bw=0.35,
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
    """
    DETAIL_KEY = "signal:detail"

    def __init__(self):
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
    Object representing a general phase shift keying (PSK) constellation. The
    modulation order can be any power of 2
    """

    def __init__(self, order, **kwargs):
        CommunicationsWaveform.__init__(self, **kwargs)
        # Metadata
        self.detail.type = "digital"
        self.detail.modulation = "psk"
        self.detail.order = order
        # Constellation object
        if order == 2:
            self.label = "BPSK"
            self.constellation = digital.constellation_bpsk()
        elif order == 4:
            self.label = "QPSK"
            self.constellation = digital.constellation_qpsk()
        elif order == 8:
            self.label = "8PSK"
            self.constellation = digital.constellation_8psk()
        else:
            raise ValueError(
                "Object currently only supports BPSK, QPSK, and 8PSK")


class qam(CommunicationsWaveform):
    """
    Object representing a quadratum amplitude modulation (QAM) constellation.
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


class bpsk(CommunicationsWaveform):
    """
    Object representing a binary phase shift keying (BPSK) constellation.
    """

    def __init__(self, **kwargs):
        psk.__init__(self, order=2, **kwargs)
        self.label = "BPSK"


class qpsk(CommunicationsWaveform):
    def __init__(self, **kwargs):
        """
        Object representing a quadrature phase shift keying (QPSK) constellation.
        """
        psk.__init__(self, order=4, **kwargs)
        self.label = "QPSK"
