# Fantasio: Normalization tool for SPIRou spectra
=======

A tool for normalizing stellar spectra using a sigma-clipping method, designed for SPIRou data.
The normalization is performed order by order and can be used with an interactive GUI. Thus GUI offers several options, allowing the user to remove emission lines, adjust sigma-clipping parameters, and modify spline fitting parameters (degree and number of knots). Users can visualize the normalized spectra in real time while changing the parameters.

- Installation:

You can clone the Fantasio repository directly from GitHub using the following command:

`git clone https://github.com/Lisa2626/Fantasio.git`

This will create a local copy of the project on your machine.

Or you can install via pip with:

`pip install ./Fantasio`

or

`pip install git+https://github.com/Lisa2626/Fantasio.git`


- Prerequisites:

Ensure you have Python >=3.6 and pip installed on your machine (make sure of the version). You can check this by running:

`python --version`

`pip --version`

You also need the following libraries: matplotlib, astropy, pandas, numpy, scipy, astropy
If you don't have them, an error will appears and you can used pip install to install them.
The best is to create a virtual environment with all of the required library.

- How to run the code?

Once installed, you can import the Fantasio package in python with the following line:

`import Fantasio`

`Fantasio/fantasio.py`

Run the fantasio code from your terminal window, you have to choose between interactive or automatic normalisation.

- Which one to run?

You have to start first with the interactive tool and then you can use the automatic normalization. The parameters used for each order will be stored in a .fits file and re used.
To used automatic normalization you need one normalize file with all the normalization parameters, those parameters for the normalization will be apply for all the .fits file.

- How to use Fantasio?

Interactive mode, test the tool with the test.fits file provided in the folder.

You will be prompted to answer the following questions:

Choose normalisation mode ('interactive' or 'automatic'):

If you choose interactive, 

Name of the FITS file to normalise:

Which flux do you want to normalize? FLUX ('A', 'B', or 'AB'):

Path to the directory to save the file?

Use one .fits file to check all order with the interactive window, choose the flux you want to normalize (A or B), and the path where you want the _norm.fits file to be saved. 
It will be possible to normalize all flux with the same normalization parameters (degree and number of knots for the spline fitting, sigma-clipping above and below, number of iterations, part where you delected the spectra) or to normalize separatly if your data are different (see more options part).

Reminder: To run the automatic normalization, you have to do the interactive one once to have  _norm.fits file.)

Once you have normalized one .fits file interactively, you can use the automatic mode to normalize all .fits files in a folder with the parameters you used and saved in the _norm.fits. The automatic mode will normalize all fluxes (A, B, AB) using the saved parameters.

If you want to check for example the flux B, with the normalized parameters that you used for flux A it is possible with inter.py (see section more options).

The automatic.py code will ask you:

Path to the directory containing FITS files to normalize:

Path to the NORM parameters FITS file:

Path to save the norm files:

Enter the path where the data .fits file are, this folder need to contain all the t.fits to be normalized.
Enter the path where the _norm.fits file created using the interactive.py and enter where you want to saved all the normalized files.


You can directly run the interactive window with:

`Fantasio/interactive.py`

Or the automatic normalization with:

`Fantasio/automatic.py`


- How to use the interactive window??

If you run interactive, an interactive window with the spectra and the normalised spectra is showed. You can adjust normalization parameters using sliders for:

    Degree: Polynomial degree for spline fitting.
    Knots: Number of knots for spline interpolation.
    Sigma Clipping: Upper and lower thresholds for clipping.
    Iterations: Number of sigma-clipping iterations.

The user can deleted some region of the spectra like emission lines for example using the selec range button, once you click on select range, go with your mouse on the window and select a region, if a misclick is made you can use the reset buttom.

You can use the "Previous" button to go to the previous order and the "Next" button to view the next order. To complete the normalization, you need to check all 49 orders. When you click "Next" on the last order, the procedure is complete, and the _norm.fits file is created. Be carefull to not click on the next button if you did not finish the normalization.

You can use the slider to adjust the parameters and see how they affect the normalization. "Degree" and "Knots" are used for spline interpolation. The sigma clipping can be adjusted above and below the curve, and the number of iterations determines how many times the sigma clipping is applied.


<img width="1341" alt="2" src="https://github.com/user-attachments/assets/6bd3fdfa-1a19-4f9f-834c-2be5a1385f2c" />
  
The "Select Range" button allows you to select a region on the normalization window to remove from the spectra. If you make a mistake, you can use the "Reset" button. However, note that if you make multiple modifications, the "Reset" button will only undo the last modification, so be careful. Be careful to not use the reset button if you change order if you did not click on select range before ! Emission lines can be removed to improve the normalization.


<img width="1074" alt="3" src="https://github.com/user-attachments/assets/3dbe8f82-2a7f-4562-a147-d01847f33fb7" />


- More options:

`Fantasio/auto.py`

To normalize automaticly only the flux you used in the interactive.
If you normalized the flux A, you can run auto.py and normalize only A. (if you want the flux B and AB to be normalized with the same parameters run automatic.py).

`Fantasio/inter.py`

To check if the normalization changes between flux A, B and AB, this will plot the parameters saved in the _params_norm.fits file and visualed them with another param flux.


- Improvements:

Two improvements needs to be make: if you reset at order n but you click on the selected button at order n-1 it is a problem, second you cannot reset two regions so be careful to check before adding another region to be selected because the reset button only work one time per order for now, this has to be improve.
