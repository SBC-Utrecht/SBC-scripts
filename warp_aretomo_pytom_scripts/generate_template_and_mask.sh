#!/bin/bash

# create folder and put reference structure in, here 'templates/er_ribos_filt.mrc'
mkdir templates

# create the template by convoluting with CTF:
# - here we used a previous subtomogram average
# - a reconstruction from the emdb generally also works well (but pdbs can also work)
pytom_create_template.py -i templates/er_ribos_filt.mrc -o templates/ribo.mrc --input-voxel 1.724 --output-voxel 17.36 -c -z 4 -a 0.08 -v 300 --Cs 2.7 --cut-after-first-zero -b 80

# create corresponding mask
pytom_create_mask.py -b 80 --output templates/mask.mrc --voxel-size 17.36 -r 11 -s 1

