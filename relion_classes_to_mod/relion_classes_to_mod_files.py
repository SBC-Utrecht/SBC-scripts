#!/usr/bin/env python
# Script to go from an relion classification star file to a set of .mod files for visualisation
# WARNING: this is all very experimental, assumes:
# -no more than 10 classes
# -We can find all required info in the relion star file
# -imod is installed and point2model is findable

import argparse
from itertools import chain
import subprocess
RLN_COLS = {'_rlnCoordinateX': 'x',
            '_rlnCoordinateY': 'y',
            '_rlnCoordinateZ': 'z',
            '_rlnHelicalTubeID': 'contour',
            '_rlnTomoName': 'tomoname',
            '_rlnClassNumber': 'class_nr'
            }
# Grab the MPL tabel colors
MPL_COLORS = [(31, 119, 180),
              (255,127,14),
              (44, 160, 44),
              (214, 39, 40),
              (148, 103, 189),
              (140, 86, 75),
              (227, 119, 194),
              (127, 127, 127),
              (188, 189, 34),
              (23, 190, 207)]

def main(starfile, binning=1):
    # output structure: {tomoname: (class, helix_id, x, y, z)}
    outputs = {}
    cols = {i : None for i in RLN_COLS.values()}
    min_class, max_class = 1, 1
    with open(starfile, 'r') as f:
        iterator = (line for line in f)
        # find all columns
        while any(i is None for i in cols.values()):
            try:
                line = next(iterator)
            except StopIteration:
                break
            line = line.strip().split()
            if len(line) > 0 and line[0] in RLN_COLS:
                cols[RLN_COLS[line[0]]] = int(line[1].strip('#'))-1
        # find start of data
        line = next(iterator)
        while line.startswith('_'):
            line = next(iterator)
        for line in chain([line], iterator):
            split = line.strip().split()
            if len(split) == 0:
                continue
            tomoname = split[cols['tomoname']]
            contour = split[cols['contour']]
            class_nr = int(split[cols['class_nr']])
            x = split[cols['x']]
            y = split[cols['y']]
            z = split[cols['z']]
            min_class = min(min_class, class_nr)
            max_class = max(max_class, class_nr)
            particles = outputs.get(tomoname, list())
            # contours start at 0 while classes start a 1, make both start at 1
            particles.append((class_nr, int(contour)+1, float(x)/binning, float(y)/binning, float(z)/binning))
            outputs[tomoname] = particles

    # Start writing text files
    conversion_list = []
    for output_name, output_data in outputs.items():
        output_name += '_coordinates.txt'
        with open(output_name, 'w+') as f:
            f.writelines([f'{i[0]:6d}{i[1]:6d}{i[2]:12.2f}{i[3]:12.2f}{i[4]:12.2f}\n' 
                for i in output_data])
        conversion_list.append(output_name)
    # Convert text to mdocs
    used_colors = [MPL_COLORS[i] for i in range(0, max_class-min_class+1)]
    for name in conversion_list:
        outname = name.split('.')[0]+'.mod'
        cmd = ['point2model','-sphere', '5']
        for c in used_colors:
            cmd += ["-color", f"{c[0]},{c[1]},{c[2]}"] 
        cmd += [f"{name}", f"{outname}"]
        print(f"Converting {name} to {outname}")
        subprocess.run(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-sf','--starfile', required=True)
    parser.add_argument('-b', '--binning', default=1, type=int, help='Binning of the tomogram associated with the final .mod')
    args = parser.parse_args()
    main(starfile=args.starfile, binning=args.binning)
