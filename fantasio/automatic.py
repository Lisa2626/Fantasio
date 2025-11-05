#IF YOU ONLY DID THE INTERACTIVE WINDOW ONCE BUT YOU WANT TO NORM ALL THE OTHERS WITH THE SAME PARAMETERS

import os
import argparse
import numpy as np
from astropy.io import fits
from scipy.interpolate import splrep, splev
from glob import glob

# ------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------#
def process_data(obsWl, obsFlux, obsI_fit, parameters_table):
    obswave_order_list = []
    obsflux_order_list = []
    obswave_order_list.append(obsWl.tolist())  # Convert original data 2D to list of 49 1D
    obsflux_order_list.append(obsFlux.tolist())

    obsWl_order_list = []
    obsI_order_list = []

    nan_positions_obsI = np.isnan(obsI_fit)
    obsWl_order = np.full_like(obsI_fit, np.nan)
    obsWl_order[~nan_positions_obsI] = obsWl[~nan_positions_obsI]
    obsI_order = np.full_like(obsI_fit, np.nan)
    obsI_order[~nan_positions_obsI] = obsFlux[~nan_positions_obsI]

    obsWl_order_list.append(obsWl.tolist())  # Convert original data 2D to list of 49 1D
    obsI_order_list.append(obsFlux.tolist())

    obsWla = []
    obsIaa = []

    for i in range(49):
        nan_positions_obsI = np.isnan(obsI_order[i])

        if len(obsWl_order[i]) == 0 or len(obsI_order[i]) == 0:
            obsWla.append(np.full_like(obsFlux[i], np.nan))  # Remplit de NaN
            obsIaa.append(np.full_like(obsFlux[i], np.nan))  # Remplit de NaN
            continue

        obsWll = np.array(obsWl_order[i])[~nan_positions_obsI]
        obsIl = np.array(obsI_order[i])[~nan_positions_obsI]

        obsWla.append(obsWll)
        obsIaa.append(obsIl)

    obsI_norm = []
    wave = []

    for i in range(49):

        if len(obsWla[i]) == 0 or np.all(np.isnan(obsWla[i])):
            obsI_norm.append(np.full_like(obsFlux[i], np.nan))  # Remplit avec NaN
            #wave.append(np.full_like(obsFlux[i], np.nan))
            wave.append(obsWl[i])  # Garder la longueur d'onde originale
            continue

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

            if len(obsWl_clipped) == 0:  # Sécurité en cas de clipping trop sévère
                obsI_norm.append(np.full_like(obsFlux[i], np.nan))
                wave.append(obsWl[i])
                continue

            tck_clipped = splrep(obsWl_clipped, obsI_clipped, k=k, t=knots[1:-1])
            fitIvals = splev(obsWl_clipped, tck_clipped)

            obsWl_order, obsI_order = obsWl_clipped, obsI_clipped

        fit = splev(obsWl[i], tck_clipped)

        test2 = obsFlux[i] / fit

        test2 = np.where((test2 >= 0) & (test2 <= 10), test2, np.nan)

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

                obsI_norm = {'A': None, 'B': None, 'AB': None}
                obsI_fit = {'A': None, 'B': None, 'AB': None}
                parameters_table = {'A': None, 'B': None, 'AB': None}
                cont = {'A': None, 'B': None, 'AB': None}

                def get_fit_and_params(prefix):
                    del_i_key = f'DEL_I_ARRAY_{prefix}'
                    params_key = f'PARAMETERS_{prefix}'
                    cont_key = f'CONT_{prefix}'

                    if del_i_key in hdul_modified and params_key in hdul_modified:
                        return hdul_modified[del_i_key].data, hdul_modified[params_key].data, hdul_modified[cont_key].data

                    for fallback in ['A', 'B', 'AB']:
                        del_i_fb = f'DEL_I_ARRAY_{fallback}'
                        params_fb = f'PARAMETERS_{fallback}'
                        cont_fb = f'CONT_{fallback}'
                        if del_i_fb in hdul_modified and params_fb in hdul_modified:
                            return hdul_modified[del_i_fb].data, hdul_modified[params_fb].data, hdul_modified[cont_fb].data

                    return None, None, None

                for comp in ['A', 'B', 'AB']:
                    wave_key = f'Wave{comp}'
                    flux_key = f'Flux{comp}'
                    blaze_key = f'Blaze{comp}'

                    if wave_key in hdu and flux_key in hdu and blaze_key in hdu:
                        obsWl = hdu[wave_key].data
                        obsFlux = hdu[flux_key].data / hdu[blaze_key].data
                        fit, params, cont_val = get_fit_and_params(comp)
                        if fit is not None and params is not None:
                            obsI_norm[comp] = process_data(obsWl, obsFlux, fit, params)
                            obsI_fit[comp] = fit
                            parameters_table[comp] = params
                            cont[comp] = cont_val

                output_filename = os.path.splitext(os.path.basename(observationName))[0] + '_norm.fits'
                output_path = os.path.join(output_directory, output_filename)

                with fits.open(observationName, mode='readonly') as hdul_original:
                    hdul_new = fits.HDUList(hdul_original)

                    for comp, norm_data in obsI_norm.items():
                        if norm_data is not None:
                            hdul_new.append(fits.ImageHDU(norm_data, name=f'NORM{comp}'))
                            hdul_new.append(fits.ImageHDU(obsI_fit[comp], name=f'DEL_I_ARRAY_{comp}'))
                            hdul_new.append(fits.BinTableHDU.from_columns(fits.ColDefs(parameters_table[comp]), name=f'PARAMETERS_{comp}'))
                            hdul_new.append(fits.ImageHDU(cont[comp], name=f'CONT_{comp}'))

                    hdul_new.writeto(output_path, overwrite=True)

        except FileNotFoundError as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()

# ------------------------------------------------------------------------------#


