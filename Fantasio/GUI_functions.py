# Helper functions for continuum normalization fitting

import numpy as np
import matplotlib
import os
import pandas as pd
import astropy.io.fits as fits
from scipy.interpolate import splrep, splev
import matplotlib.pyplot as plt
from tkinter import Scale
import tkinter as tk
from tkinter import IntVar, DoubleVar, Checkbutton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
matplotlib.use("TkAgg")

# Read .FITS file observation, extract Wl and I for each order
def readFitsFile(observationName, choice='AB', choices='AB', trimMax=-1.):
    if not os.path.exists(observationName):
        print("Error: File does not exist")
        return None, None, None

    hdu = fits.open(observationName)

    obsWl_order_list = []
    obsI_order_list = []

    if choice == 'A':
        obsWl = hdu['WaveA'].data
        Wl = hdu['WaveA'].data
        obsI = hdu['FluxA'].data / hdu['BlazeA'].data
    elif choice == 'B':
        obsWl = hdu['WaveB'].data
        Wl = hdu['WaveB'].data
        obsI = hdu['FluxB'].data / hdu['BlazeB'].data
    elif choice == 'AB':
        obsWl = hdu['WaveAB'].data
        Wl = hdu['WaveAB'].data
        obsI = hdu['FluxAB'].data / hdu['BlazeAB'].data
    else:
        print("Error: Invalid choice")
        return None

    if choices == 'A':
        obsI_fit = hdu['DEL_I_ARRAY_A'].data
    elif choices == 'B':
        obsI_fit = hdu['DEL_I_ARRAY_B'].data
    elif choices == 'AB':
        obsI_fit = hdu['DEL_I_ARRAY_AB'].data
    else:
        print("Error: Invalid choice")
        return None

    nan_positions_obsI = np.isnan(obsI)

    obsWl_order = np.full_like(obsI_fit, np.nan)
    obsWl_order[~nan_positions_obsI] = obsWl[~nan_positions_obsI]

    obsI_order = np.full_like(obsI_fit, np.nan)
    obsI_order[~nan_positions_obsI] = obsI[~nan_positions_obsI]

    obsWl_order_list.append(obsWl_order.tolist())  # Convert to list
    obsI_order_list.append(obsI_order.tolist())  # Convert to list

    obsSig = np.std(obsI) * np.ones(obsI.shape)

    inSpec = [obsWl, obsI, obsSig]

    # Weak protection against small/bad values in I or sigma
    meanIapprox = np.nanmean(obsI)
    indNotNaN = ~np.isnan(obsI)
    indUse = indNotNaN & (obsI > 1e-10 * meanIapprox) & (obsSig > 1e-10 * meanIapprox)
    for i in range(1, len(inSpec)):
        inSpec[i][np.logical_not(indUse)] = 0.0
    obsSig[np.logical_not(indUse)] = 1e10

    # Optionally protect against very large values too
    if trimMax > 0.:
        meanIapprox = np.nanmean(obsI)
        indNotNaN & (inSpec[1] < trimMax * meanIapprox)
        for i in range(1, len(inSpec)):
            inSpec[i][np.logical_not(indUse)] = 0.0
        obsSig[np.logical_not(indUse)] = 1e10

    return obsWl_order, obsI_order, obsI_fit, Wl

def readParams(observationName, obsI_fit, choices='A'):

    if not os.path.exists(observationName):
        print("Error: File does not exist")
        return None, None, None

    hdu = fits.open(observationName)

    if choices == 'A':
        parameters_tables = hdu['PARAMETERS_A'].data
        parameters_table = pd.DataFrame(parameters_tables)
    elif choices == 'B':
        parameters_tables = hdu['PARAMETERS_B'].data
        parameters_table = pd.DataFrame(parameters_tables)
    elif choices == 'AB':
        parameters_tables = hdu['PARAMETERS_AB'].data
        parameters_table = pd.DataFrame(parameters_tables)
    else:
        print("Error: Invalid choice")
        return None

    param_dict = {'obsI_fit': obsI_fit, 'parameters_table': parameters_table}

    return param_dict

def remove_nan_rows(obsWl_order, obsI_order, obsI_fit):
    obsWl = []
    obsI = []

    for i in range(49):
        # do not take the nan value of the obsI list
        nan_positions_obsI = np.isnan(obsI_fit[i])

        # select non NaN elements in each list
        obsWll = np.array(obsWl_order[i])[~nan_positions_obsI]
        obsIl = np.array(obsI_order[i])[~nan_positions_obsI]

        obsWl.append(obsWll)
        obsI.append(obsIl)

    return obsWl, obsI



# Fit and sigma clipping for each order of the spectrum, init params for interactive window
def fit_order(obsWl, obsI, Wl, obsWl_order, obsI_order, param_dict, k, t):
    fit_dict = {}  #dictionnaire with lists
    fitIvals_list = []
    obsWl_order_list = []
    obsI_order_list = []
    obsWl_list = []
    obsI_list = []
    Wl_list = []
    test_list = []
    fit_list = []
    wave_list = []
    norm = []
    obsI_fit = param_dict['obsI_fit']
    parameters_table = param_dict['parameters_table']
    fit_dict['del_state'] = {'min_x': None, 'max_x': None, 'min_y': None, 'max_y': None}

    for i in range(len(obsWl_order)):
        obsWl_list.append(obsWl_order[i])  # full the lists
        obsI_list.append(obsI_order[i])
        Wl_list.append(Wl[i])

        knots = list(np.linspace(int(obsWl[i][0]), int(obsWl[i][-1]), int(t) + 2))

        tck = splrep(obsWl[i], obsI[i], k=k, t=knots[1:-1])
        fitIval = splev(obsWl[i], tck)

        normalisation = obsI[i] / fitIval

        obsWl_order_list.append(obsWl[i])  # full the lists
        obsI_order_list.append(obsI[i])
        fitIvals_list.append(fitIval)
        norm.append(normalisation)

    fit_dict[f'obsWl_order'] = obsWl_order_list   #add the list of list for each order to the dict, 0 to 48
    fit_dict[f'obsI_order'] = obsI_order_list
    fit_dict[f'fitIvals'] = fitIvals_list
    fit_dict[f'obsWl'] = obsWl_list  #spectrum without fit and sigma with nan
    fit_dict[f'Wl'] = Wl_list  #wavelengh without nan
    fit_dict[f'obsI'] = obsI_list
    fit_dict[f'result'] = test_list
    fit_dict[f'wave'] = wave_list
    fit_dict[f'norm'] = norm
    fit_dict[f'fit'] = fit_list
    fit_dict['obsI_fit'] = obsI_fit
    fit_dict['parameters_table'] = parameters_table

    return fit_dict

# Plot all spectrum with each fitting order
def plot(fit_dict):
    obs_data_list = fit_dict.get('obsWl_order', [])
    order_I_list = fit_dict.get('obsI_order', [])
    order_fitIvals_list = fit_dict.get('fitIvals', [])
    obsWl = fit_dict.get('obsWl', [])
    obsI = fit_dict.get('obsI', [])

    for i, (order_data, order_I, order_fitIvals, obsWl, obsI) in enumerate(zip(obs_data_list, order_I_list, order_fitIvals_list, obsWl, obsI)):
        obsWl_order = order_data
        obsI_order = order_I
        fitIvals = order_fitIvals

        plt.plot(obsWl_order, obsI_order, label='Données ordre {}'.format(i + 1))
        plt.plot(obsWl, obsI, label='Spectrum')
        plt.plot(obsWl_order, fitIvals, label=f'Ajustement polynomial', color='green')

        #plt.legend()
        plt.title('')
        plt.xlabel('Wl [nm]')
        plt.ylabel('Flux I')
        plt.show()

    return


# Interactive window GUIs
fig = Figure(figsize=(12, 7), dpi=100)
ax = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2, sharex=ax)

# 2 windows, one for the fit and the other with norm spectrum
def plot_single_order(obsWl_order, obsI_order, fitIvals, fit_dict, tck_clipped, order_num, obsWl_order_a, obsI_order_a, show_base_spectrum, order_num_var):
    ax.clear()
    ax2.clear()
    current_order_num = order_num_var.get()
    Wl = fit_dict['Wl'][current_order_num]
    obsI = fit_dict['obsI'][current_order_num]
    if show_base_spectrum:
        ax.plot(Wl, obsI, label='All spectrum', color='black')
    ax.plot(obsWl_order, obsI_order, label=f'Data order {order_num}', color='blue', marker='*', linestyle='None', alpha = 0.8)
    ax.plot(obsWl_order, fitIvals, label=f'Spline fit', color='red')
    ax.set_xlabel('Wavelength [nm]', fontsize=12)
    ax.set_ylabel('Flux', fontsize=12)

    #ax.legend(fontsize='large')
    #ax.tick_params(axis='both', which='major', labelsize=10)

    # All spectrum
    test = splev(Wl, tck_clipped)  #Norm, all spectrum divided by fit model
    norm = obsI / test
    ax2.plot(Wl, norm, 'k', linewidth=1.0, alpha=0.8)

    ax2.set_xlabel('Wavelength [nm]', fontsize=12)
    ax2.set_ylabel('Norm. Flux', fontsize=12)

    ax2.axhline(y=1.0, ls='--', color='red', linewidth=1.0)

    ax.legend()

# Spline method and sigma clipping with changing parameters
def fit_and_plot(obsWl_order, obsI_order, k, t, sigma_above, sigma_below, num_iterations):

    for iteration in range(num_iterations):
        num_knots = t
        knots = list(np.linspace(int(obsWl_order[0]), int(obsWl_order[-1]), int(num_knots) + 2))
        tck = splrep(obsWl_order, obsI_order, k=k, t=knots[1:-1])
        fitIval = splev(obsWl_order, tck)

        residuals = obsI_order - fitIval
        std = np.std(residuals)
        mask_clipped = (residuals < sigma_above * std) & (residuals > -sigma_below * std)

        obsWl_clipped, obsI_clipped = obsWl_order[mask_clipped], obsI_order[mask_clipped]

        tck_clipped = splrep(obsWl_clipped, obsI_clipped, k=k, t=knots[1:-1])
        fitIvals = splev(obsWl_clipped, tck_clipped)

        test2 = obsI_clipped / fitIvals

        obsWl_order, obsI_order = obsWl_clipped, obsI_clipped

    return obsWl_order, obsI_order, fitIvals, test2, tck_clipped

# Function to actualise the spectrum while changing the parameters through sliders
def on_param_change(canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                    k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict):
    current_order_num = order_num_var.get()

    if current_order_num < orders:
        k_value = k_var.get()
        t_value = t_var.get()
        sigma_above_value = sigma_above_var.get()
        sigma_below_value = sigma_below_var.get()
        num_iterations_value = num_iterations_var.get()

        if 'parameters' not in fit_dict:
            fit_dict['parameters'] = [{}for _ in range(orders)]
            fit_dict['obsWl_order'] = [[]for _ in range(orders)]
            fit_dict['obsI_order'] = [[] for _ in range(orders)]
            fit_dict['norm'] = [[] for _ in range(orders)]
            fit_dict['test'] = [[] for _ in range(orders)]
            fit_dict['result'] = [[] for _ in range(orders)]

        obsWl_order, obsI_order, fitIvals, test2, tck_clipped = fit_and_plot(
            obs_data_list[current_order_num],
            order_I_list[current_order_num],
            k_value,
            t_value,
            sigma_above_value,
            sigma_below_value,
            num_iterations_value
        )

        fit_dict['wave'].append(obs_data_list)  # to be delected?

        Wl = fit_dict['Wl'][current_order_num]
        obsI = fit_dict['obsI'][current_order_num]

        test = splev(Wl, tck_clipped)  # Norm, all spectrum divided by fit model
        norm = obsI / test

        # save values in fit_dict
        fit_dict['obsWl_order'][current_order_num] = [obsWl_order]
        fit_dict['obsI_order'][current_order_num] = [obsI_order]
        fit_dict['result'][current_order_num] = [test]
        fit_dict['norm'][current_order_num] = [norm]
        fit_dict['test'][current_order_num] = [tck_clipped]

        # save parameters values (last one)
        fit_dict['parameters'][current_order_num] = {
            'k': k_value,
            't': t_value,
            'sigma_above': sigma_above_value,
            'sigma_below': sigma_below_value,
            'num_iterations': num_iterations_value
        }

        show_base_spectrum = show_base_spectrum_var.get()
        plot_single_order(obsWl_order, obsI_order, fitIvals, fit_dict, tck_clipped, current_order_num + 1,
                          obs_data_list[current_order_num], order_I_list[current_order_num], show_base_spectrum, order_num_var)

        canvas.draw()


# Store parameters to keep them when using next and previous buttom
def restore_params(order_num, k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, fit_dict):
    params_list = fit_dict.get('parameters_table')
    if params_list is not None and not params_list.empty:
        window_params = params_list.iloc[order_num]
    else:
        print("Error: parameters table is empty")
        return

    k_value = window_params.get('k')
    t_value = window_params.get('t')
    sigma_above_value = window_params.get('sigma_above')
    sigma_below_value = window_params.get('sigma_below')
    num_iterations_value = window_params.get('num_iterations')

    if k_value is not None:
        k_var.set(k_value)
    if t_value is not None:
        t_var.set(t_value)
    if sigma_above_value is not None:
        sigma_above_var.set(sigma_above_value)
    if sigma_below_value is not None:
        sigma_below_var.set(sigma_below_value)
    if num_iterations_value is not None:
        num_iterations_var.set(num_iterations_value)


# Previous button to go back to previous order
def previous(canvas, root, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                    k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict):
    current_order_num = order_num_var.get()
    if current_order_num > 0:
        order_num_var.set(current_order_num - 1)
        restore_params(order_num_var.get(), k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var,
                       fit_dict)
        on_param_change(
            canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
            k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict
        )

# Show next order
def on_next_click(canvas, root, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                    k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict):
    current_order_num = order_num_var.get()
    if current_order_num < orders - 1:
        order_num_var.set(current_order_num + 1)
        restore_params(order_num_var.get(), k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var,
                       fit_dict)
        on_param_change(
            canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
            k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict
        )
    else:
        root.after(100, lambda: root.destroy())  # close window after a few time

# Show the spectrum without modifications (deleted part for the fit of the continuum)
def reset_spec(canvas, root, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                    k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict):
    current_order_num = order_num_var.get()

    if 'del_state' in fit_dict and 'min_x' in fit_dict['del_state']:
        obsWl = fit_dict['initial_data']['obsWl_order']
        obsI = fit_dict['initial_data']['obsI_order']
        obsWll = fit_dict['initial_data']['obsWll']
        obsII = fit_dict['initial_data']['obsII']

        obs_data_list[current_order_num] = obsWll
        order_I_list[current_order_num] = obsII

        obsWl_order, obsI_order, fitIvals, test2, tck_clipped = fit_and_plot(
            obsWl,
            obsI,
            k_var.get(),
            t_var.get(),
            sigma_above_var.get(),
            sigma_below_var.get(),
            num_iterations_var.get()
        )

        # Plot the entire spectrum again
        show_base_spectrum = show_base_spectrum_var.get()

        plot_single_order(obsWl_order, obsI_order, fitIvals, fit_dict, tck_clipped, current_order_num + 1,
                          obs_data_list[current_order_num], order_I_list[current_order_num], show_base_spectrum,
                          order_num_var)

        on_param_change(
            canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
            k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict
        )

        canvas.draw()


# Select a part of the spectrum and delete it to the calculation of the fit
def on_select_range(click, release, canvas, ax, root, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                    k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict):
    x_min, x_max = min(click.xdata, release.xdata), max(click.xdata, release.xdata)
    y_min, y_max = min(click.ydata, release.ydata), max(click.ydata, release.ydata)  #coord of the selector rectangle

    current_order_num = order_num_var.get()

    fit_dict['del_state'][current_order_num] = fit_dict['del_state'].get(current_order_num, [])
    fit_dict['del_state'][current_order_num].append({
        'min_x': x_min,
        'max_x': x_max,
        'min_y': y_min,
        'max_y': y_max,
        'obsWl_order': None,
        'obsI_order': None,
        'fitIvals': None,
    })

    print("Selected coordinates:", fit_dict['del_state'][current_order_num])

    obsWll = obs_data_list[current_order_num]
    obsII = order_I_list[current_order_num]

    obsWl = fit_dict['obsWl_order']
    obsI = fit_dict['obsI_order']
    obsWl_order = obsWl[current_order_num][0]
    obsI_order = obsI[current_order_num][0]

    fit_dict['initial_data'] = {
        'obsWl_order': obsWl_order.copy(),
        'obsI_order': obsI_order.copy(),
        'obsWll': obsWll.copy(),
        'obsII': obsII.copy(),
    }

    # Apply the mask to the selected range (between the coord selected)
    mask_selected = ((obsWl_order >= x_min) & (obsWl_order <= x_max) &
                    (obsI_order >= y_min) & (obsI_order <= y_max))

    mask_selected_a = ((obsWll >= x_min) & (obsWll <= x_max) &
                     (obsII >= y_min) & (obsII <= y_max))

    # Replace the values in the selected range with NaN
    obsI_order[mask_selected] = np.nan
    obsWl_order[mask_selected] = np.nan

    obsII[mask_selected_a] = np.nan
    obsWll[mask_selected_a] = np.nan

    # Remove NaN values from the dataset
    obsI_order = obsI_order[~np.isnan(obsI_order)]
    obsWl_order = obsWl_order[~np.isnan(obsWl_order)]

    #fitIvals = fitIvals[~np.isnan(fitIvals)]
    obsII = obsII[~np.isnan(obsII)]
    obsWll= obsWll[~np.isnan(obsWll)]

    #actutalise next and previous buttom!
    obs_data_list[current_order_num] = obsWll
    order_I_list[current_order_num] = obsII

    obsWl_order, obsI_order, fitIvals, test2, tck_clipped = fit_and_plot(
        obsWl_order,
        obsI_order,
        k_var.get(),
        t_var.get(),
        sigma_above_var.get(),
        sigma_below_var.get(),
        num_iterations_var.get()
    )

    Wl = fit_dict['Wl'][current_order_num]
    obsI = fit_dict['obsI'][current_order_num]

    test = splev(Wl, tck_clipped)  # Norm, all spectrum divided by fit model

    norm = obsI / test

    fit_dict['norm'][current_order_num] = [norm]

    # Update the values in the fit_dict
    fit_dict['obsWl_order'][current_order_num] = obsWl_order
    fit_dict['obsI_order'][current_order_num] = obsI_order

    # Save the lists in del_state
    fit_dict['del_state']['obsWl_order'] = obsWl_order.tolist()
    fit_dict['del_state']['obsI_order'] = obsI_order.tolist()

    # Plot the entire spectrum again
    show_base_spectrum = show_base_spectrum_var.get()

    plot_single_order(obsWl_order, obsI_order, fitIvals, fit_dict, tck_clipped, current_order_num + 1,
                      obs_data_list[current_order_num], order_I_list[current_order_num], show_base_spectrum, order_num_var)


    on_param_change(
        canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
        k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict
    )

    canvas.draw()


#Interactive part (GUI)
def interactive(fit_dict):

    obs_data_list = fit_dict.get('obsWl_order', [])
    order_I_list = fit_dict.get('obsI_order', [])
    order_fitIvals_list = fit_dict.get('fitIvals', [])
    parameters_table = fit_dict.get('parameter_table', [])
    Wl_list = fit_dict.get('Wl', [])

    orders = len(obs_data_list)

    root = tk.Tk()
    root.title("Interactive window") #name of the GUI

    # Variables Tkinter, init value
    order_num_var = IntVar()
    order_num_var.set(0)

    if parameters_table:
        first_params = parameters_table[0]  # Obtenir le premier élément de la liste
    else:
        first_params = {}  # Utiliser un dictionnaire vide si la liste est vide

    k_var = IntVar(value=first_params.get('k'))
    t_var = IntVar(value=first_params.get('t'))
    sigma_above_var = DoubleVar(value=first_params.get('sigma_above'))
    sigma_below_var = DoubleVar(value=first_params.get('sigma_below'))
    num_iterations_var = IntVar(value=first_params.get('num_iterations'))

    restore_params(0, k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, fit_dict)

    show_base_spectrum_var = IntVar()
    show_base_spectrum_var.set(1)  # if init value is 1 spectrum is shown by default

    # subplot to Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

    #Sliders for the parameters to updated the spline
    k_label = tk.Label(root, text='Degree:') #degree of the fit
    k_scale = Scale(root, from_=1, to=5, orient=tk.HORIZONTAL, variable=k_var,
                    command=lambda val: on_param_change(
                        canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                        k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var,
                        fit_dict
                    ))
    k_label.pack(side='left')
    k_scale.pack(side='left')

    t_label = tk.Label(root, text='Knots:') #number of wl knots for the spline
    t_scale = Scale(root, from_=1, to=30, orient=tk.HORIZONTAL, variable=t_var,
                    command=lambda val: on_param_change(
                        canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                        k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var,
                        fit_dict
                    ))
    t_label.pack(side='left')
    t_scale.pack(side='left')

    sigma_above_label = tk.Label(root, text='Sigma Above:') #upper sigma, sigma clipping
    sigma_above_scale = Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, resolution=0.1, variable=sigma_above_var,
                              command=lambda val: on_param_change(
                                  canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                                  k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var,
                                  show_base_spectrum_var, fit_dict
                              ))
    sigma_above_label.pack(side='left')
    sigma_above_scale.pack(side='left')

    sigma_below_label = tk.Label(root, text='Sigma Below:')  #lower sigma, for the sigma clipping
    sigma_below_scale = Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, resolution=0.1, variable=sigma_below_var,
                              command=lambda val: on_param_change(
                                  canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                                  k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var,
                                  show_base_spectrum_var, fit_dict
                              ))
    sigma_below_label.pack(side='left')
    sigma_below_scale.pack(side='left')

    num_iterations_label = tk.Label(root, text='Iterations:')  #number of iterations for the sigma clipping
    num_iterations_scale = Scale(root, from_=1, to=10, orient=tk.HORIZONTAL, variable=num_iterations_var,
                                 command=lambda val: on_param_change(
                                     canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                                     k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var,
                                     show_base_spectrum_var, fit_dict
                                 ))
    num_iterations_label.pack(side='left')
    num_iterations_scale.pack(side='left')

    # Add a check button to show or not all the initial spectrum
    show_base_spectrum_checkbox = Checkbutton(root, text="Show all spectrum", variable=show_base_spectrum_var,
                                              command=lambda: on_param_change(
                                                  canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                                                  k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var,
                                                  show_base_spectrum_var, fit_dict
                                              ))
    show_base_spectrum_checkbox.pack(side='left')

    # To get back to the original spectrum (without modification)
    RESET_button = tk.Button(root, text="Reset",
                             command=lambda: reset_spec(canvas, root, orders, order_num_var, obs_data_list,
                                                        order_I_list, order_fitIvals_list,
                                                        k_var, t_var, sigma_above_var, sigma_below_var,
                                                        num_iterations_var, show_base_spectrum_var, fit_dict))
    RESET_button.pack(pady=10, side='left')

    # Previous button = show previous order
    previous_button = tk.Button(root, text="Previous", command=lambda: previous(
        canvas, root, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
        k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict
    ))
    previous_button.pack(pady=10, side='left')

    #On next click = show next order
    next_button = tk.Button(root, text="Next", command=lambda: on_next_click(
        canvas, root, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
        k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict
    ))
    next_button.pack(pady=10, side='left')


    #Select and delect emission lines of the spectrum button
    select_range_button = tk.Button(root, text="Select Range", command=lambda: on_select_range(click, release, canvas, ax, root, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                    k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict))
    select_range_button.pack(pady=10, side='left')

    # Used RectangleSelector for selected and delected part
    rect_selector = RectangleSelector(ax, lambda click, release: on_select_range(click, release, canvas, ax, root, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
                    k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict),
                                      useblit=True, button=[1], minspanx=5, minspany=5,
                                      spancoords='pixels')


    # updated the plot
    on_param_change(
        canvas, orders, order_num_var, obs_data_list, order_I_list, order_fitIvals_list,
        k_var, t_var, sigma_above_var, sigma_below_var, num_iterations_var, show_base_spectrum_var, fit_dict
    )

    root.mainloop()

    return fit_dict


# Save function, params and position wl I when deleted emission lines for automatic mode and normalisation
def save(observationName, fit_dict, choice='AB', output_directory=None):
    if output_directory is None:
        output_directory = input("Please provide the path to the directory to save the file: ")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)

    output_filename = os.path.splitext(os.path.basename(observationName))[0] + '.fits'
    output_path = os.path.join(output_directory, output_filename)

    adjusted_lists = []
    adjusted_lists1 = []
    target_length = 4088

    norm_I_list = fit_dict['norm']  # I norm
    parameters = fit_dict['parameters']  # dict of params
    obsIcont = fit_dict['result']

    # Calculate adjusted lists
    for i in range(len(fit_dict['obsWl_order'])):
        Wl_list = fit_dict['Wl'][i]
        obsI_list = fit_dict['obsI_order'][i][0]
        obsWl_list = fit_dict['obsWl_order'][i][0]

        adjusted_list = np.full(target_length, np.nan)
        common_indices = np.where(np.isin(Wl_list, obsWl_list))[0]  # find index where Wl and obsWl_list match
        adjusted_list[common_indices] = obsI_list  # list of 4088 elements for obsI
        adjusted_lists.append(adjusted_list)

        adjusted_list1 = np.full(target_length, np.nan)
        common_indices1 = np.where(np.isin(Wl_list, obsWl_list))[0]
        adjusted_list1[common_indices1] = obsWl_list
        adjusted_lists1.append(adjusted_list1)

    new_delI = np.vstack(adjusted_lists)

    obsI_norm = np.vstack(norm_I_list)  # create 2D array (49, 4088)

    cont = np.vstack(obsIcont)

    # Open the original FITS file in read-only mode
    with fits.open(observationName, mode='readonly') as hdul_original:
        # Check if the output file already exists
        if os.path.exists(output_path):
            # Open the existing FITS file in update mode
            hdul_new = fits.open(output_path, mode='update')
        else:
            # Create a new HDUList object
            hdul_new = fits.HDUList(hdul_original)

        # Check if extensions already exist for the given choice
        if f'NORM_I_{choice}' in hdul_new:
            # Remove existing extensions for the given choice
            hdul_new.pop(f'NORM_I_{choice}')
            hdul_new.pop(f'DEL_I_ARRAY_{choice}')
            hdul_new.pop(f'PARAMETERS_{choice}')

        cont_extension_exists = f'CONT_{choice}' in hdul_new

        # If 'CONT_A' extension exists, remove it
        if cont_extension_exists:
            hdul_new.pop(f'CONT_{choice}')

        # Add new extensions for the given choice
        new_flux_hdu = fits.ImageHDU(obsI_norm, name=f'NORM_I_{choice}')
        hdul_new.append(new_flux_hdu)

        new_delI_hdu = fits.ImageHDU(new_delI, name=f'DEL_I_ARRAY_{choice}')
        hdul_new.append(new_delI_hdu)

        new_cont_hdu = fits.ImageHDU(cont, name=f'CONT_{choice}')
        hdul_new.append(new_cont_hdu)

        # Convert list of dictionaries to a Pandas DataFrame
        parameters_df = pd.DataFrame(parameters)
        # Create a table with parameters and save it in the FITS file
        parameters_table = fits.BinTableHDU.from_columns(fits.ColDefs(parameters_df.to_records(index=False)))
        parameters_table.name = f'PARAMETERS_{choice}'
        hdul_new.append(parameters_table)  # Add to HDUList

        # Write the new HDUList object to the output file
        hdul_new.writeto(output_path, overwrite=True)

    # Close the HDUList objects
    hdul_original.close()
    hdul_new.close()

# ------------------------------------------------------------------------------#



















