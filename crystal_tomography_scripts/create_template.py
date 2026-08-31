#!/usr/bin/env python3

import mrcfile
import numpy as np
import argparse

def extract_template(volume, center, box_size):
    x, y, z = center

    x_start = int(x-(box_size/2))
    x_end = int(x+(box_size/2))
    y_start = int(y-(box_size/2))
    y_end = int(y+(box_size/2))
    z_start = int(z-(box_size/2))
    z_end = int(z+(box_size/2))

    # Extract subvolume
    box = volume[z_start:z_end, y_start:y_end, x_start:x_end]

    # Normalize
    mean = np.mean(box)
    std = np.std(box)
    if std > 0:
        normalized_box = (box - mean) / std
    else:
        normalized_box = box - mean  # In case of zero standard deviation

    return normalized_box

def process_mrc(input_mrc, output_mrc, coordinates, size):
    # Load the tomogram
    volume = mrcfile.open(input_mrc, permissive=True)
    volume = volume.data

    x, y, z = map(int, coordinates.split(','))
 
    template = extract_template(volume, [x,y,z], size)
 
    with mrcfile.new(output_mrc, overwrite=True) as mrc:
        mrc.set_data(template.astype(np.float32))

    print(f"Saved template to {output_mrc}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract subvolume from tomogram to use as template")
    parser.add_argument("input_mrc", type=str, help="Input MRC file (tomogram)")
    parser.add_argument("output_mrc", type=str, help="Output MRC file (template)")
    parser.add_argument("coordinates", type=str, help="Coordinates x,y,z")
    parser.add_argument("size", type=int, help="Box size of output template")

    args = parser.parse_args()

    process_mrc(args.input_mrc, args.output_mrc, args.coordinates,args.size)

