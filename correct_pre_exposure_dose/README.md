## Correct pre-exposure dose of star files created by aretomo3torelion5.py

This script corrects the star files that are written out by aretomo3torelion5.py script from the TomoGuide.
Run `python correct_pre_exposure_dose.py --help` to see the (required) input flags.


Scripts depend on:
* python 3

Some notes:
* It looks for a TOMONAME.mdoc file in the mdoc folder for each TOMONAME.mrc.star in the starfile folder
* Dose should be given per complete-tilt (**not** per subframe)
