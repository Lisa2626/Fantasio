# Fantasio: Normalization tool for SPIRou spectra
=======

A tool for normalizing stellar spectra using a sigma-clipping method, designed for SPIRou data.
The normalization is performed order by order and can be used with an interactive GUI. Thus GUI offers several options, allowing the user to remove emission lines, adjust sigma-clipping parameters, and modify spline fitting parameters (degree and number of knots). Users can visualize the normalized spectra in real time while adjusting these parameters.

- Installation:

You can clone the Fantasio repository directly from GitHub using the following command:

`git clone https://github.com/Lisa2626/Fantasio.git`

This will create a local copy of the project on your machine.

Alternatively, you can install via pip with:

`pip install ./Fantasio`

or

`pip install git+https://github.com/Lisa2626/Fantasio.git`


- Prerequisites:

Ensure you have Python >=3.6 and pip installed on your machine (make sure of the version). Check this by running:

`python --version`

`pip --version`

You also need the following libraries: matplotlib, astropy, pandas, numpy, and scipy.
If you don't have them, an error will appears and you can used pip install to install them.
Tip: It is recommended to create a virtual environment and install all required library.

- How to run the code?

Once installed, you can import the Fantasio package in python with the following line:

`import Fantasio`

`Fantasio/fantasio.py`

Run the fantasio code from your terminal window, you have to choose between interactive or automatic normalization.

- Which one should you usde?

You must start with the interactive tool to perform an initial normalization. The parameters used for each order will be stored in a .fits file and reused later if you choose automatic normalization for several fieles.
To us automatic normalization, you need a previous normalized .fits file containing all the normalization parameters.

- How to use Fantasio?

Interactive mode, you can test the tool with the test.fits file provided in the folder.

You will be prompted to answer the following questions:

Choose normalisation mode ('interactive' or 'automatic'):

If you choose interactive, 

Name of the FITS file to normalise:

Which flux do you want to normalize? FLUX ('A', 'B', or 'AB'):

Path to the directory to save the file?

Use a single .fits file to review all order with the interactive window. Choose the flux you want to normalize (A, B, or AB), and provide the path where the _norm.fits file should be saved. 

You can: 

Normalize all fluxes using the same parameters (spline degree, number of knots, sigma-clipping thresholds, number of iterations, and manually removed regions), 

or

Normalize fluxes separately if the data differ (see the "More Options" section below).

Reminder: To run the automatic normalization, you must first perform interactive normalization to generate the _norm.fits file).

Automatic mode:

Once you have normalized one .fits file interactively, you can run the automatic mode to normalize all .fits files in a folder with the parameters you used previously and saved in the _norm.fits. The automatic mode will normalize all fluxes (A, B, AB) using the saved parameters. All the files you want to normalize need to be in the same folder, the code read the t.fits extension, ensure you don't have others t.fits file.

If you want to check for example the flux B, with the normalized parameters that you used for flux A it is possible with inter.py (see section more options).

The automatic.py code will ask you:

Path to the directory containing FITS files to normalize:

Path to the NORM parameters FITS file:

Path to save the norm files:

Enter the path where the data .fits file are, this folder need to contain all the t.fits to be normalized.
Enter the path where the _norm.fits file created using the interactive.py and enter where you want to saved all the normalized files.


You can run the scipts directly:

`Fantasio/interactive.py`

`Fantasio/automatic.py`


- How to use the interactive window??

If you choose interactive, a GUI will open showing the spectra and the normalised spectra. You can adjust normalization parameters using sliders for:

    Degree: Polynomial degree for spline fitting.
    Knots: Number of knots for spline interpolation.
    Sigma Clipping: Upper and lower thresholds for clipping.
    Iterations: Number of sigma-clipping iterations.

You can also remove some region of the spectra (e.g, emission lines) using the "Select Range" button. After selecting it, click and drag in the window to define the region you want to remove. If a misclick is made you can use the reset buttom (but just on the last removed region, if you removed several region the reset buttom will only restore the last one). 

Use the "Previous" and "Next" buttons to navigate between spectral orders. To complete the normalization, you need to check all 49 orders. When you click "Next" on the last order, the procedure is complete, and the _norm.fits file is created. Be carefull to not click on the next button if you did not finish the normalization.

You can use the slider to adjust the parameters and see how they affect the normalization. "Degree" and "Knots" are used for spline interpolation. The sigma clipping can be adjusted above and below the curve, and the number of iterations determines how many times the sigma clipping is applied.


<img width="1341" alt="2" src="https://github.com/user-attachments/assets/6bd3fdfa-1a19-4f9f-834c-2be5a1385f2c" />
  
The "Select Range" button allows you to select a region on the normalization window to remove from the spectra. If you make a mistake, you can use the "Reset" button. However, note that if you make multiple modifications, the "Reset" button will only undo the last modification, so be careful. Be careful to not use the reset button if you change order if you did not click on select range before ! Removing emission lines can significantly improve normalization results.


<img width="1074" alt="3" src="https://github.com/user-attachments/assets/3dbe8f82-2a7f-4562-a147-d01847f33fb7" />


- More options:

`Fantasio/auto.py`

Use this to automatically normalize only the flux you selected during the interactive session (e.g., only A).
If you normalized the flux A, you can run auto.py and normalize only A. (if you want the flux B and AB to be normalized with the same parameters run automatic.py).


`Fantasio/inter.py`

This script allows you to compare normalization parameters across different fluxes (A, B, AB).
It will plot the parameters saved in _params_norm.fits and let you visualize the differences.


- Improvements:

Improvements that need to be implemented:

1) Reset behavior across orders:
If you click the "Reset" button while on order n, but had previously selected a region on order n–1, it can cause unexpected behavior. This needs to be fixed so that resets only affect the currently selected order.

2) Limited reset functionality:
Currently, the "Reset" button only undoes the last region selection within a given order. If you select multiple regions, you won’t be able to reset all of them—only the most recent one. Therefore, be careful when selecting multiple regions, as only the last selection can be undone for now. This limitation will be addressed in a future update.
