## Make eman2 tomograms from imod tilt series alignment
* Generates hdf from mrc and puts in to tiltseries directory
* Generates eman2 json file from imod style xf and tlt file produced with aretomo3 -OutImod 1 flag and puts into info directory
* Can optionally add defocus values from aretomo3 CTF.txt file
* To run:
    1) Symlink xf, tlt, mrc, txt files to new eman2 working directory
    2) Edit unbinned_pix with pixel size and function calls in imodxf2emanjson.py so they contain your filenames e.g. tomo1.xf, tomo1.tlt, tomo1_CTF.txt, tomo1.mrc
    3) Comment out functions you don't want to run e.g. #convert_to_hdf(tilt_name)
    4) Need to have eman2 loaded, we have an eman2 conda environment so eman2 is in python path and libraries are importable
    5) run the script with: python imodxf2emanjson.py
    6) Generate tomogram with: e2tomogram.py tiltseries/tomo01.hdf --tltstep=3.0 --clipz 500 --niter=0 --patchtrack=0 --load
       1) where tltstep is your tilt step & clipz is your bin4 z size in pixels
