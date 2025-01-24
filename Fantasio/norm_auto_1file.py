import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import matplotlib
import os
import numpy as np
from scipy.interpolate import splrep, splev
import pandas as pd
import argparse
matplotlib.use('Qt5Agg')

def main():
    parser = argparse.ArgumentParser(description="Normalize flux in automatic mode.")
    parser.add_argument('observationName', nargs='?', type=str, help='Path to the FITS file to normalize')
    parser.add_argument('modified_filename', nargs='?', type=str, help='Path to the already NORM FITS file')
    parser.add_argument('output_directory', nargs='?', type=str,
                        help="Chemin vers le nouveau dossier pour enregistrer le fichier FITS.")
    args = parser.parse_args()

    if args.observationName is None and args.modified_filename is None:
        observationName = input("Path to the FITS file to normalize: ")
        modified_filename = input("Path to the NORM parameters FITS file: ")
    else:
        if args.observationName is None or args.modified_filename is None:
            print("Please provide both the path to the observation FITS file and the path to the NORM FITS file.")
            exit()
        observationName = args.observationName
        modified_filename = args.modified_filename

    try:
        hdu = fits.open(observationName)
        hdul_modified = fits.open(modified_filename)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit()

    if args.output_directory is None:
        output_directory = input("Path to save the norm file : ")
    else:
        output_directory = args.output_directory

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Charger le fichier FITS modifié
    # modified_filename = '2812667tA_norm.fits'
    # hdul_modified = fits.open(modified_filename)
    # Charger le fits file to normalize
    # observationName = '2812667t.fits'
    # hdu = fits.open(observationName)

    # Lire les données à partir des extensions
    obsWl = hdu['WaveA'].data
    obsIa = hdu['FluxA'].data / hdu['BlazeA'].data

    obsI_order_2d = hdul_modified['2D_FLUX_ARRAY'].data
    obsWl_fit = hdul_modified['DEL_WAVE_ARRAY'].data  # wv for calcul fit
    obsI_fit = hdul_modified['DEL_I_ARRAY'].data  # flux of the fit

    parameters_table = hdul_modified[-1]  # recup last ligne, find the name for later
    parameters = pd.DataFrame(parameters_table.data)

    hdul_modified.close()  # close file

    obswave_order_list = []
    obsflux_order_list = []

    obswave_order_list.append(obsWl.tolist())  # Convert original data 2d to list of 49 1d
    obsflux_order_list.append(obsIa.tolist())

    a = obswave_order_list[0]
    b = obsflux_order_list[0]

    obsWl_order_list = []
    obsI_order_list = []
    obsI_fit_list = []

    nan_positions_obsI = np.isnan(obsI_fit)

    obsWl_order = np.full_like(obsI_fit, np.nan)
    obsWl_order[~nan_positions_obsI] = obsWl[~nan_positions_obsI]

    obsI_order = np.full_like(obsI_fit, np.nan)
    obsI_order[~nan_positions_obsI] = obsIa[~nan_positions_obsI]

    obsWl_order_list.append(obsWl.tolist())  # Convert original data 2d to list of 49 1d
    obsI_order_list.append(obsIa.tolist())

    obsWla = []
    obsIaa = []

    # remove nan

    for i in range(49):
        nan_positions_obsI = np.isnan(obsI_order[i])
        obsWll = np.array(obsWl_order[i])[~nan_positions_obsI]
        obsIl = np.array(obsI_order[i])[~nan_positions_obsI]

        obsWla.append(obsWll)
        obsIaa.append(obsIl)

    norm = []
    test = []
    wave = []

    for i in range(49):

        # read DataFrame parameters corresponding to each orders
        k = parameters.loc[i, 'k']
        sigma_above = parameters.loc[i, 'sigma_above']
        sigma_below = parameters.loc[i, 'sigma_below']
        t = parameters.loc[i, 't']
        num_iterations = parameters.loc[i, 'num_iterations']

        for iteration in range(num_iterations):
            knots = np.linspace(obsWla[i][0], obsWla[i][-1], t + 2)
            knots = knots[1:-1]  # Remove the first and last elements

            tck = splrep(obsWla[i], obsIaa[i], k=k, t=knots[1:-1])
            fitIval = splev(obsWla[i], tck)

            residuals = obsIaa[i] - fitIval
            std = np.std(residuals)
            mask_clipped = (residuals < sigma_above * std) & (residuals > -sigma_below * std)

            obsWl_clipped, obsI_clipped = obsWla[i][mask_clipped], obsIaa[i][mask_clipped]

            tck_clipped = splrep(obsWl_clipped, obsI_clipped, k=k, t=knots[1:-1])
            fitIvals = splev(obsWl_clipped, tck_clipped)

            obsWl_order, obsI_order = obsWl_clipped, obsI_clipped

        fit = splev(obsWl[i], tck_clipped)

        test2 = obsIa[i] / fit

        test.append(test2)
        wave.append(obsWl[i])

    #plt.plot(obsWl[44], obsI_order_2d[44])
    #plt.show()

    #plt.plot(wave[44], test[44])
    #plt.show()

    #Save in a new file
    output_filename = os.path.join(output_directory, observationName + "_norm.fits")

    obsI_norm = np.vstack(test)  #2D array for norm
    new_hdu = fits.ImageHDU(obsI_norm, name='2D_FLUX_ARRAY')  # create a new HDU (Header Data Unit) for the 2D array
    new_hdul = fits.HDUList()

    with fits.open(observationName) as original_hdul:
        for hdu in original_hdul:
            new_hdul.append(hdu.copy())

    new_hdul.append(new_hdu)
    new_hdul.writeto(output_filename, overwrite=True)

if __name__ == "__main__":
    main()






