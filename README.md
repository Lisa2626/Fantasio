# Fantasio
Normalisation tool for SPIRou spectra
=======
A tool for normalizing stellar spectra, with an interactive GUI. Made for SPIRou data.
Normalization tool order by order, with option allowing the user to remove emission line, adapt the normalization parameters.
Advice: the best is to use the interactive tool once and then use the automatic normalization.

Installation:
Clone the repository

You can clone the Fantasio repository directly from GitHub using the following command:

`git clone https://github.com/Lisa2626/Fantasio.git`

This will create a local copy of the project on your machine.

Install via pip:

`pip install ./Fantasio`

or

`pip install git+https://github.com/Lisa2626/Fantasio.git`

Prerequisites:
Make sure you have Python 3.x and pip installed on your machine. You can check this by running:

`python --version`

`pip --version`

Run package:

`python3 import Fantasio`

`python3 python3.11 Fantasio/fantasio.py`

How to use Fantasio?

Run the fantasio code, you have to choose between interactive or automatic normalisation.
You can test with the .fits in the folder.
If you run interactive, an interactive window with the spectra and the normalised spectra is showed. The user can modified the parameters to normalised the star. Degree of polynome, number of knots, sigma clipping up and down, number of iteration of the sigma clipping. The user can deleted some region of the spectra like emission lines for example, if a misclick is made you can use the reset buttom.

If you run fantasio.py, you have to answer those questions:

Choose normalisation mode ('interactive' or 'automatic'):

(To run the automatic normalization, you have to do the interactive one once to have a _norm.fits file.)

If you choose interactive, 
Name of the FITS file to normalise:
Which flux do you want to normalize? FLUX ('A', 'B', or 'AB'):
Path to the directory to save the file?

If you choose automatic, 
Path to the directory containing FITS files to normalize:
Path to the NORM parameters FITS file:
Path to save the norm files:

You can directly run the interactive window with:

`python3 python3.11 Fantasio/interactive.py`

Or the automatic normalization:

`python3 python3.11 Fantasio/automatic.py`

How to use the interactive window??

You can use the "Previous" button to go to the previous order and the "Next" button to view the next order. To complete the normalization, you need to check all 49 orders. When you click "Next" on the last order, the procedure is complete, and the _norm.fits file is created.

You can use the slider to adjust the parameters and see how they affect the normalization. "Degree" and "Knots" are used for spline interpolation. The sigma clipping can be adjusted above and below the curve, and the number of iterations determines how many times the sigma clipping is applied.


<img width="1341" alt="2" src="https://github.com/user-attachments/assets/6bd3fdfa-1a19-4f9f-834c-2be5a1385f2c" />
  
The "Select Range" button allows you to select a region on the normalization window to remove from the spectra. If you make a mistake, you can use the "Reset" button. However, note that if you make multiple modifications, the "Reset" button will only undo the last modification, so be careful. Emission lines can be removed to improve the normalization.


<img width="1074" alt="3" src="https://github.com/user-attachments/assets/3dbe8f82-2a7f-4562-a147-d01847f33fb7" />


Two improvements needs to be make: if you reset at order n but you click on the selected button at order n-1 its a problem, second you cannot reset two regions so be careful to check before adding another region to be selected because the reset button only work one time per order for now, this has to be improve.

(Interactive.py to do once --> the saving file contains parameters and you can apply them automatically to others observations of the star using automatic.py. If you want to check parameters with another observation you can used inter.py. Diff between auto and automatic and inter and interactive. If you want to check what is inside your norm file you can use read_norm_files.py and change what you want to read.
