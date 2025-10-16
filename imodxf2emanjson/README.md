1) Generates hdf from mrc and puts in to tiltseries directory
2) Generates eman2 json file from imod style xf and tlt file produced with aretomo3 -OutImod 1 flag and puts into info directory
3) Can optionally add defocus values from aretomo3 CTF.txt file
4) To run:
    a) Symlink xf, tlt, mrc, txt files to working new eman2 working working_directory
    b) Edit unbinned_pix with pixel size and function calls in imodxf2emanjson.py so they contain your filenames e.g. tomo1.xf, tomo1.tlt, tomo1_CTF.txt, tomo1.mrc
    c) Comment out functions you don't want to run e.g. #convert_to_hdf(tilt_name)
    d) Need to have eman2 loaded, we have an eman2 conda environment so eman2 is in python path and libraries are importable
    e) run the script with: python imodxf2emanjson.py
