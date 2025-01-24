# Fantasio
<<<<<<< HEAD
Normalisation tool for SPIRou spectra
=======
A tool for normalizing stellar spectra, with an interactive GUI. Made for SPIRou data.

Run the fantasio code, you have to choose between interactive or automatic normalisation.

If you run interactive. An interactive window with the spectra and the normalised spectra is showed. The user can modified the parameters to normalised the star. Degree of polynome, number of knots, sigma clipping up and down, number of iteration of the sigma clipping. The bottom allows the users to change order, go to next order or previous one. Finally, the user can deleted some region of the spectra like emission lines for example, if a misclick is made you can use the reset buttom.

2 improvements needs to be make: if you reset at order n but you click on the selected button at order n-1 its a problem, second you cannot reset two regions so be careful to check before adding another region to be selected because the reset button only work one time per order for now, this has to be improve.

(Interactive.py to do once --> the saving file contains parameters and you can apply them automatically to others observations of the star using automatic.py. If you want to check parameters with another observation you can used inter.py. Diff between auto and automatic and inter and interactive. If you want to check what is inside your norm file you can use read_norm_files.py and change what you want to read.

>>>>>>> 23cd350 (Initial commit for Fantasio package)
