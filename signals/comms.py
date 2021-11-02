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


modulations = {
    "digital": [bpsk, qpsk]
}
