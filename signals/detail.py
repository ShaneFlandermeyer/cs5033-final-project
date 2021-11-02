class detail():
    """
    """
    DETAIL_KEY = "signal:detail"
    TYPE_KEY = "type"
    MODULATION_KEY = "class"
    CARRIER_VARIANT_KEY = "carrier_variant"
    SYMBOL_VARIANT_KEY = "symbol_variant"
    ORDER_KEY = "order"
    DUPLEXING_KEY = "duplexing"
    MULTIPLEXING_KEY = "multiplexing"
    MULTIPLE_ACCESS_KEY = "multiple_access"
    SPREADING_KEY = "spreading"
    BANDIWDTH_KEY = "bandwidth"
    CHANNEL_KEY = "channel"
    CLASS_VARIANT_KEY = "class_variant"
    def __init__(self):
        self.type = ""
        self.modulation = ""
        self.carrier_variant = ""
        self.symbol_variant = ""
        self.order = 0
        self.duplexing = ""
        self.multiplexing = ""
        self.multiple_access = ""
        self.spreading = ""
        self.bandwidth = 0.0
        self.channel = 0
        self.class_variant = ""

    def dict(self):
        """
        Convert the supplied metadata to a dictionary of dictionaries
        TODO: There's probably a smarter way to do this
        """
        d = {self.DETAIL_KEY:[]}
        d[self.DETAIL_KEY].append({self.TYPE_KEY:self.type})
        d[self.DETAIL_KEY].append({self.MODULATION_KEY:self.modulation})
        d[self.DETAIL_KEY].append({self.CARRIER_VARIANT_KEY:self.carrier_variant})
        d[self.DETAIL_KEY].append({self.SYMBOL_VARIANT_KEY:self.symbol_variant})
        d[self.DETAIL_KEY].append({self.ORDER_KEY:self.order})
        d[self.DETAIL_KEY].append({self.DUPLEXING_KEY:self.duplexing})
        d[self.DETAIL_KEY].append({self.MULTIPLEXING_KEY:self.multiplexing})
        d[self.DETAIL_KEY].append({self.MULTIPLE_ACCESS_KEY:self.multiple_access})
        d[self.DETAIL_KEY].append({self.SPREADING_KEY:self.spreading})
        d[self.DETAIL_KEY].append({self.BANDIWDTH_KEY:self.bandwidth})
        d[self.DETAIL_KEY].append({self.CHANNEL_KEY:self.channel})
        d[self.DETAIL_KEY].append({self.CLASS_VARIANT_KEY:self.class_variant})

        return d

if __name__ == '__main__':
    d = detail()
    print(d.dict())
