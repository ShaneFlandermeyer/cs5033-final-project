class detail():
    """
    Store metadata needed to describe various signals using the SigMF signal
    extension
    https://github.com/gnuradio/SigMF/blob/sigmf-v1.x/extensions/signal.sigmf-ext.md#the-type-field
    TODO: This is currently only really useful for communications signals
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
    # TODO: This is not a part of the signal extension spec
    NOISE_VOLTAGE_KEY = "noise_voltage"
    def __init__(self):
        self.type = None
        self.modulation = None
        self.carrier_variant = None
        self.symbol_variant = None
        self.order = None
        self.duplexing = None
        self.multiplexing = None
        self.multiple_access = None
        self.spreading = None
        self.bandwidth = None
        self.channel = None
        self.class_variant = None
        self.noise_voltage = None

    def dict(self):
        """
        Convert the supplied metadata to a dictionary of dictionaries
        """
        d = vars(self)
        # If any of the values are None, remove them from the dictionary
        for key,value in d.copy().items():
            if value is None:
                del d[key]
        
        # Had to make 'modulation' the class variable storing the signal class
        # (analog/digital) because class is a keyword in python
        if 'modulation' in d:
            d[self.CLASS_KEY] = d.pop('modulation')
        return d

if __name__ == '__main__':
    d = detail()
    print(d.dict())
