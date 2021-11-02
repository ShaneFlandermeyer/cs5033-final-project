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


class bpsk(Signal):
    def __init__(self):
        Signal.__init__(self)
        # Metadata
        self.detail.type = "digital"
        self.detail.modulation = "psk"
        self.detail.order = 2
        # Constellation
        self.constellation = digital.constellation_bpsk()


class qpsk(Signal):
    def __init__(self):
        Signal.__init__(self)
        # Metadata
        self.detail.type = "digital"
        self.detail.modulation = "psk"
        self.detail.order = 4
        # Constellation object
        self.constellation = digital.constellation_qpsk()

class psk(Signal):
    """
    Object representing a general phase shift keying (PSK) constellation
    """
    def __init__(self,order):
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
        elif order == 16:
            self.constellation = digital.constellation_16psk()
        elif order == 32:
            self.constellation = digital.constellation_32psk()
        elif order == 64:
            self.constellation = digital.constellation_64psk()
        else:
            # TODO: Should this raise an error or do something different?
            raise ValueError("Invalid order for PSK constellation")


# TODO: I don't like using this
modulations = {
    "digital": [bpsk, qpsk]
}
