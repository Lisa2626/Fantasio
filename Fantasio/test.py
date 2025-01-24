import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import matplotlib
import pandas as pd
matplotlib.use('Qt5Agg')

modified_filename = 'Fantasio/2812667t.fits'
hdul_modified = fits.open(modified_filename)

obsWl = hdul_modified['WaveAB'].data
obsIa = hdul_modified['FluxAB'].data

print(obsWl)
print(obsIa)
