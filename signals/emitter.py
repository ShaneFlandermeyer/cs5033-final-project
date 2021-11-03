class emitter():
    """
    Store metadata needed to describe various RF emitter hardware
    https://github.com/gnuradio/SigMF/blob/sigmf-v1.x/extensions/signal.sigmf-ext.md#the-type-field
    """
    EMITTER_KEY = 'signal:emitter'
    SEID_KEY = 'seid'
    MANUFACTURER_KEY = 'manufacturer'
    POWER_TX_KEY = 'power_tx'
    POWER_EIRP_KEY = 'power_eirp'
    GEOLOCATION_KEY = 'geolocation'
    def __init__(self):
      self.seid = None
      self.manufacturer = None
      self.power_tx = None
      self.power_eirp = None
      self.geolocation = None

    def dict(self):
        """
        Convert the supplied metadata to a dictionary of dictionaries

        INPUTS:
        -------
        - self: The emitter object

        OUTPUTS:
        --------
        - d: A dictionary of metadata
        
        """
        d = vars(self)
        # If any of the values are None, remove them from the dictionary
        for key,value in d.copy().items():
            if value is None:
                del d[key]
        return d
