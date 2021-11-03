from gnuradio import channels, gr, blocks, analog, digital
from signals.detail import detail


class Signal():

    """
    Define metadata and constellation types for various digital communications
    signals 

    Parameters
    ----------
    """
    DETAIL_KEY = "signal:detail"

    def __init__(self):
        self.detail = detail()


class psk(Signal):
    """
    Object representing a general phase shift keying (PSK) constellation. The
    modulation order can be any power of 2
    """

    def __init__(self, order):
        Signal.__init__(self)
        # Metadata
        self.detail.type = "digital"
        self.detail.modulation = "psk"
        self.detail.order = order
        # Constellation object
        if order == 2:
            self.constellation = digital.constellation_bpsk()
        elif order == 4:
            self.constellation = digital.constellation_qpsk()
        elif order == 8:
            self.constellation = digital.constellation_8psk()
        else:
            raise ValueError("Object currently only supports BPSK, QPSK, and 8PSK")


class bpsk(Signal):
    """
    Object representing a binary phase shift keying (BPSK) constellation.
    """

    def __init__(self):
        psk.__init__(self,order=2)


class qpsk(Signal):
    def __init__(self):
        """
        Object representing a quadrature phase shift keying (QPSK) constellation.
        """
        psk.__init__(self,order=4)
