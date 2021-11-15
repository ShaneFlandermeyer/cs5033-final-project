from gnuradio import gr, blocks, analog, channels


class Channel(gr.hier_block2):
    def __init__(self, sampRate, nSinusoids, doppFreq, losModel, kFactor,
                 delays, mags, nTapsMultipath, noisePower, seed, name='Channel'):
        gr.hier_block2.__init__(self, name,
                                gr.io_signature(1, 1, gr.sizeof_gr_complex),
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))
        noiseAmplitude = 10**(noisePower/20)
        adder = blocks.add_cc()
        noiseSource = analog.noise_source_c(
            analog.GR_GAUSSIAN, noiseAmplitude, seed)
        fading_model = channels.selective_fading_model(
            nSinusoids, doppFreq/sampRate, losModel, kFactor, seed, delays, mags, nTapsMultipath)
        self.connect(self, fading_model)
        self.connect(fading_model, (adder, 0))
        self.connect(noiseSource, (adder, 1))
        self.connect(adder, self)


if __name__ == '__main__':
    # channels.selective_fading_model( 8, 10.0/samp_rate, False, 4.0, 0, (0.0,0.1,1.3), (1,0.99,0.97), 8 )
    Channel(20e6, 8, 1, True, 4.0, (0.0, 0.1, 1.3), (1, 0.99, 0.97), 8, 13, 0)
