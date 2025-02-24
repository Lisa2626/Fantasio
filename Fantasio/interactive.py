#Code for normalizing and plotting an observed spectrum, can work interactively with a graphical interface

import fitting_GUI_functions as ff
import sys
import argparse

# ------------------------------------------------------------------------------#
def main():

    parser = argparse.ArgumentParser(
        description='Normalize an observed spectrum, working order by order interactively.')  # User modifiable parameters
    parser.add_argument('observationName', nargs='?', type=str, help='Name of the FITS file to normalise')  # arg name file
    parser.add_argument('user_choice', nargs='?', type=str.upper, choices=['A', 'B', 'AB'],
                        help='Which flux do you want to normalize? Choose from A, B, or AB')  # arg for the flux
    parser.add_argument('output_directory', nargs='?', type=str, help="Path to the directory to save the file.")
    # observationName = '2812667t.fits' #V806tau
    args = parser.parse_args()

    if len(sys.argv) == 1:
        observationName = input("Name of the FITS file to normalise: ")
        user_choice = input("Which flux do you want to normalize? FLUX ('A', 'B', or 'AB'): ").upper()
        output_directory = input("Path to the directory to save the file?: ")
    else:
        observationName = args.observationName
        user_choice = args.user_choice
        output_directory = args.output_directory

    if output_directory is None:
        output_directory = input("Please provide the path to the directory to save the file: ")

    if user_choice is None:
        user_choice = input("Which flux do you want to normalize? FLUX ('A', 'B', or 'AB'): ").upper()

    # Read an observation
    obsWl_order, obsI_order, Wl = ff.readFitsFile(observationName, choice=user_choice, trimMax=100.)

    # Remove nan for fitting function
    obsWl, obsI = ff.remove_nan_rows(obsWl_order, obsI_order)

    # Interactive window to normalized order by order
    fit_dict = ff.fit_order(obsWl, obsI, Wl, obsWl_order, obsI_order, k=5, t=5)
    # ff.plot(fit_dict) #plot order to check, without GUI
    fit_dict = ff.interactive(fit_dict)  # GUI

    # Save new .fits file with adding extension (normalized spectrum, parameters... to be used in automatic norm)
    ff.save(observationName, fit_dict, user_choice, output_directory)

if __name__ == "__main__":
    main()

# ------------------------------------------------------------------------------#












