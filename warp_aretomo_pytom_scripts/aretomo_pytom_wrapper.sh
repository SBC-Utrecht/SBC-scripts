#!/bin/bash
# run these commands first to load required modules on angstrom
# module load aretomo imod miniconda/pytom/tm
# condaactivate

# BEFORE RUNNING:
# - make sure bad tilts are excluded beforehand in Warp, this greatly improves alignments
# - review and adjust parameters carefully for your project (check software docs if things are unclear!)
# - try running on a single tilt-series first to ensure everything works
# - use pytom_create_template.py and pytom_create_mask.py to create a template and mask
# 	> docs and tutorial can be found on the pytom_tm wiki

for i in *.mrc; 
do 
	echo "running $i"
	
	# crop stack with IMOD because aretomo seems to work better with square images
	aretomo -InMrc "$i/${i%.mrc}.st" -OutMrc "$i/$i" -AngFile "$i/$i.rawtlt" -VolZ 1200 -AlignZ 800 -Wbp 1 -FlipVol 1 -OutBin 8 -Gpu 0 -TiltAxis 84.5 -DarkTol 0.01 -OutImod 2
	
	# move some aretomo output
	mv "${i%.mrc}_projXY.mrc" "$i"
	mv "${i%.mrc}_projXZ.mrc" "$i"
	mv "${i%.mrc}.aln" "$i"
	
	# create tomo specific output folder for TM with pytom
	mkdir "$i/tm_results"
	pytom_match_template.py -t "templates/emd_18231.mrc" -m "templates/mask.mrc"   -v "$i/$i" -d "$i/tm_results" -a "$i/$i.rawtlt" --per-tilt-weighting --angular-search 7.00 --voxel-size 17.36  --low-pass 40 --spectral-whitening -g 0 1 
	# extract annotations from score map	
	pytom_extract_candidates.py -j "$i/tm_results/${i%.mrc}_job.json" -n 2000 -r 7
	echo "candidate list created for $i"
done
