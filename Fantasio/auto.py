#NORM THE EXTENSION FINDED IN THE FILE, IF A, NORM A ...

import os
import argparse
import numpy as np
from astropy.io import fits
from scipy.interpolate import splrep, splev
from glob import glob

# ------------------------------------------------------------------------------#
def process_data(obsWl, obsFlux, obsI_fit, parameters_table):

    obswave_order_list = []
    obsflux_order_list = []
    obswave_order_list.append(obsWl.tolist())  # Convert original data 2d to list of 49 1d
    obsflux_order_list.append(obsFlux.tolist())

    obsWl_order_list = []
    obsI_order_list = []

    nan_positions_obsI = np.isnan(obsI_fit)
    obsWl_order = np.full_like(obsI_fit, np.nan)
    obsWl_order[~nan_positions_obsI] = obsWl[~nan_positions_obsI]
    obsI_order = np.full_like(obsI_fit, np.nan)
    obsI_order[~nan_positions_obsI] = obsFlux[~nan_positions_obsI]
    obsWl_order_list.append(obsWl.tolist())  # Convert original data 2d to list of 49 1d
    obsI_order_list.append(obsFlux.tolist())
    obsWla = []
    obsIaa = []

    for i in range(49):
        nan_positions_obsI = np.isnan(obsI_order[i])
        obsWll = np.array(obsWl_order[i])[~nan_positions_obsI]
        obsIl = np.array(obsI_order[i])[~nan_positions_obsI]
        obsWla.append(obsWll)
        obsIaa.append(obsIl)

    obsI_norm = []
    wave = []

    for i in range(49):

        k = parameters_table[i]['k']
        sigma_above = parameters_table[i]['sigma_above']
        sigma_below = parameters_table[i]['sigma_below']
        t = parameters_table[i]['t']
        num_iterations = parameters_table[i]['num_iterations']

        for iteration in range(num_iterations):
            knots = np.linspace(obsWla[i][0], obsWla[i][-1], t + 2)
            knots = knots[1:-1]

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

        test2 = obsFlux[i] / fit

        obsI_norm.append(test2)
        wave.append(obsWl[i])


    return np.vstack(obsI_norm)

def main():
    parser = argparse.ArgumentParser(description="Normalize flux in automatic mode.")
    parser.add_argument('observationName', nargs='?', type=str, help='Path to the directory containing FITS files to normalize')
    parser.add_argument('modified_filename', nargs='?', type=str, help='Path to the already NORM FITS file')
    parser.add_argument('output_directory', nargs='?', type=str, help="Path to the directory to save norm.fits files.")
    args = parser.parse_args()

    if args.observationName is None or args.modified_filename is None:
        observation_directory = input("Path to the directory containing FITS files to normalize: ")
        modified_filename = input("Path to the NORM parameters FITS file: ")
    else:
        observation_directory = args.observationName
        modified_filename = args.modified_filename

    if args.output_directory is None:
        output_directory = input("Path to save the norm files: ")
    else:
        output_directory = args.output_directory

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    observation_files = glob(os.path.join(observation_directory, '*t.fits'))

    for observationName in observation_files:
        print("Processing file:", observationName)
        try:
            with fits.open(observationName) as hdu, fits.open(modified_filename) as hdul_modified:
                obsI_norm_A = obsI_norm_B = obsI_norm_AB = None

                if 'WaveA' in hdu and 'FluxA' in hdu and 'BlazeA' in hdu and 'DEL_I_ARRAY_A' in hdul_modified and 'PARAMETERS_A' in hdul_modified:
                    obsWl_A = hdu['WaveA'].data
                    obsFlux_A = hdu['FluxA'].data / hdu['BlazeA'].data
                    obsI_fit_A = hdul_modified['DEL_I_ARRAY_A'].data
                    parameters_table_A = hdul_modified['PARAMETERS_A'].data
                    obsI_norm_A = process_data(obsWl_A, obsFlux_A, obsI_fit_A, parameters_table_A)

                if 'WaveB' in hdu and 'FluxB' in hdu and 'BlazeB' in hdu and 'DEL_I_ARRAY_B' in hdul_modified and 'PARAMETERS_B' in hdul_modified:
                    obsWl_B = hdu['WaveB'].data
                    obsFlux_B = hdu['FluxB'].data / hdu['BlazeB'].data
                    obsI_fit_B = hdul_modified['DEL_I_ARRAY_B'].data
                    parameters_table_B = hdul_modified['PARAMETERS_B'].data
                    obsI_norm_B = process_data(obsWl_B, obsFlux_B, obsI_fit_B, parameters_table_B)

                if 'WaveAB' in hdu and 'FluxAB' in hdu and 'BlazeAB' in hdu and 'DEL_I_ARRAY_AB' in hdul_modified and 'PARAMETERS_AB' in hdul_modified:
                    obsWl_AB = hdu['WaveAB'].data
                    obsFlux_AB = hdu['FluxAB'].data / hdu['BlazeAB'].data
                    obsI_fit_AB = hdul_modified['DEL_I_ARRAY_AB'].data
                    parameters_table_AB = hdul_modified['PARAMETERS_AB'].data
                    obsI_norm_AB = process_data(obsWl_AB, obsFlux_AB, obsI_fit_AB, parameters_table_AB)

                output_filename = os.path.splitext(os.path.basename(observationName))[0] + '_norm.fits'
                output_path = os.path.join(output_directory, output_filename)

                with fits.open(observationName, mode='readonly') as hdul_original:
                    hdul_new = fits.HDUList(hdul_original)

                    if obsI_norm_A is not None:
                        hdul_new.append(fits.ImageHDU(obsI_norm_A, name='NORMA'))
                        hdul_new.append(fits.ImageHDU(obsI_fit_A, name='DEL_I_ARRAY_A'))
                        hdul_new.append(fits.BinTableHDU.from_columns(fits.ColDefs(parameters_table_A), name='PARAMETERS_A'))

                    if obsI_norm_B is not None:
                        hdul_new.append(fits.ImageHDU(obsI_norm_B, name='NORMB'))
                        hdul_new.append(fits.ImageHDU(obsI_fit_B, name='DEL_I_ARRAY_B'))
                        hdul_new.append(fits.BinTableHDU.from_columns(fits.ColDefs(parameters_table_B), name='PARAMETERS_B'))

                    if obsI_norm_AB is not None:
                        hdul_new.append(fits.ImageHDU(obsI_norm_AB, name='NORMAB'))
                        hdul_new.append(fits.ImageHDU(obsI_fit_AB, name='DEL_I_ARRAY_AB'))
                        hdul_new.append(fits.BinTableHDU.from_columns(fits.ColDefs(parameters_table_AB), name='PARAMETERS_AB'))

                    hdul_new.writeto(output_path, overwrite=True)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()

# ------------------------------------------------------------------------------#

