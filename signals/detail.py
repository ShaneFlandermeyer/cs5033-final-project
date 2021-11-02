class detail():
    """
    """
    DETAIL_KEY = "signal:detail"
    TYPE_KEY = "type"
    CLASS_KEY = "class"
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
        """
        d = {self.DETAIL_KEY:vars(self)}
        # Had to make 'modulation' the class variable storing the signal class
        # (analog/digital) because class is a keyword in python
        d[self.DETAIL_KEY][self.CLASS_KEY] = d[self.DETAIL_KEY].pop("modulation")
        return d

if __name__ == '__main__':
    d = detail()
    print(d.dict())
