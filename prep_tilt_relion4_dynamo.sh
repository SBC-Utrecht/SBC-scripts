#!/bin/bash

#This script prepares tilt series for import into Dynamo and Relion4.
#Required to run from the Relion4 work folder, which should contain a folder 'tomograms',
#which in turn contains a folder 'TS' for each tilt series, and 'TS.st' and 'TS.rawtlt' inside of those. 

#Runs AreTomo -> ctfplotter -> newstack -> ctfphaseflip -> tilt to 
# generate binned, ctf corrected tomograms, and metadata for import into Dynamo and Relion4.

### INPUT PARAMETERS ###

TOMO_LIST=newtomo.txt 		#path tomo txt file with folder names, one per line

DEFOC=2000			#expected defocus in nm (i.e. 2000 for 2 um underfocus)
APIX=1.724			#pixelsize in Angstrom
BINNING=4			#binning for generated tomograms
THICKNESS=1200			#thickness of reconstruction in Z in unbinned pixels

VOLT=200
CS=2.7
AMP=0.1
TA=-88.7

### END OF INPUT ###

#create tomograms_descr.star
echo \# tomograms_descr.star > tomograms_descr.star
echo  >> tomograms_descr.star
echo data_ >> tomograms_descr.star
echo  >> tomograms_descr.star
echo loop_ >> tomograms_descr.star
echo _rlnTomoName >> tomograms_descr.star
echo _rlnTomoTiltSeriesName >> tomograms_descr.star
echo _rlnTomoImportCtfPlotterFile >> tomograms_descr.star
echo _rlnTomoImportImodDir >> tomograms_descr.star
echo  >> tomograms_descr.star

#create dynamo catalogue
cd tomograms
rm dynamo_cat.vll > /dev/null
touch dynamo_cat.vll
cd ..

#loop over tilt series
while read i;
	do
	
	cd tomograms/${tomo_name}
	
	echo Running AreTomo for ${tomo_name}
	AreTomo_1.3.3 -InMrc ${tomo_name}.st -OutMrc ${tomo_name}_Are.mrc -AngFile ${tomo_name}.rawtlt -VolZ $THICKNESS -AlignZ $(echo $THICKNESS / 1.5 | bc) -OutBin $BINNING -OutImod 2 -DarkTol 0.7 -Gpu 0 1 2 3 -TiltAxis $TA, 1 > AreTomo.log
	#we don't use AreTomo's volume
	rm ${tomo_name}_Are.mrc	

	echo Running CtfPlotter for ${tomo_name}
	cd ${tomo_name}_Are_Imod
	ctfplotter -inp ${tomo_name}_Are.st -angleFn ${tomo_name}_Are.tlt -defFn ${tomo_name}.defocus -aAngle $TA -pi $(echo "scale=4;$APIX/10" | bc) -vo $VOLT -cs $CS -am $AMP -expDef $DEFOC -useDef -find 1,0,0 -au 0,0 -sa > CtfPlotter.log		

	echo Running IMOD for ${tomo_name}

	#empty newline in AreTomo .tlt causes issues for Relion import
	sed -i '$ d' ${tomo_name}_Are.tlt

	#get binning for dynamo input and point to the ctf corrected images
	sed -i "/BinByFactor/s/.*/BinByFactor     $BINNING/" newst.com
	sed -i "/InputProjections/s/.*/InputProjections	 ${tomo_name}_Are_ctf.ali/" tilt.com	
	sed -i "/IMAGEBINNED/s/.*/IMAGEBINNED $BINNING/" tilt.com
	sed -i "/LOCALFILE/s/.*/# LOCALFILE/" tilt.com
	sed -i "/XTILTFILE/s/.*/# XTILTFILE/" tilt.com

	#run newstack -> ctfphaseflip -> tilt -> trimvol to get the tomograms
	submfg newst.com > /dev/null
	ctfphaseflip -inp ${tomo_name}_Are.ali -output ${tomo_name}_Are_ctf.ali -an ${tomo_name}_Are.tlt -xf ${tomo_name}_Are.xf -defFn ${tomo_name}.defocus -defT 15 -iW 10 -ax $TA -pi $(echo "scale=4;$APIX/10*$BINNING" | bc) -vo $VOLT -cs $CS -am $AMP > ctfphaseflip.log
	submfg tilt.com > /dev/null
	trimvol -rx ${tomo_name}_Are.rec ${tomo_name}_Are.mrc > /dev/null
	rm ${tomo_name}_Are.rec
	
	cd ../..
	
	#put relevant values in dynamo catalogue
	printf '%s/%s_Are_Imod/%s_Are.mrc\n' ${tomo_name} ${tomo_name} ${tomo_name} >> dynamo_cat.vll 
	printf '* apix = %s;\n' $(echo "scale=4;$APIX*$BINNING" | bc) >> dynamo_cat.vll
	printf '* ytilt = %s %s;\n' $(head -n 1 ${tomo_name}/${tomo_name}_Are_Imod/${tomo_name}_Are.tlt) $(tail -n 1 ${tomo_name}/${tomo_name}_Are_Imod/${tomo_name}_Are.tlt | head -n 1) >> dynamo_cat.vll
	printf '* xtilt = 0 0;\n' >> dynamo_cat.vll

	cd ..
	
	#add line to Relion import star file
	printf ' %s\ttomograms/%s/%s_Are_Imod/%s_Are.st:mrc\ttomograms/%s/%s_Are_Imod/%s.defocus\ttomograms/%s/%s_Are_Imod\n' ${tomo_name} ${tomo_name} ${tomo_name} ${tomo_name} ${tomo_name} ${tomo_name} ${tomo_name} ${tomo_name} ${tomo_name} >> tomograms_descr.star

done < $TOMO_LIST




