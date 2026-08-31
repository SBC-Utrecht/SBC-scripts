#!/usr/bin/env python3

import mrcfile
import numpy as np
import argparse


# Extract and normalize subvolume from tomogram
def extract_box(volume, center, box_size):
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

def read_coordinates(file_path):
    coordinates = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            values = line.strip().split()  # Strip leading/trailing spaces and split
            if len(values) < 3:  # Ensure we have at least 3 values
                continue
            try:
                x, y, z = map(float, values[:3])  # Convert to float first
                coordinates.append((int(x), int(y), int(z)))
            except ValueError:
                print(f"Skipping malformed line: {repr(line)}")  # Debugging info
    return coordinates

# Main function
def process_mrc(input_mrc, output_mrc, coord_file, box_size):
    # Load the tomogram
    volume = mrcfile.open(input_mrc)
    volume = volume.data

    # Read coordinates from the file
    coordinates = read_coordinates(coord_file)

    # Create an empty volume to accumulate the data
    start_box = extract_box(volume, [s/2 for s in volume.shape[::-1]], box_size)
    result_box = start_box
    result_box.flags.writeable = True
    result_box[:,:,:] = 0 
    
    ini_size = np.size(result_box)
    ini_z = np.size(result_box[:,0,0])
 

    skipped = 0 
    # Iterate through the coordinates
    for coord in coordinates:
        box = extract_box(volume, coord, box_size)
        if np.size(box) != ini_size or np.size(box[:,0,0]) != ini_z:
            skipped += 1
            continue
        result_box += box
    print("No. of skipped particles: "+str(skipped))

    # Normalize by the number of coordinates and invert contrast
    result_box /= (len(coordinates)-skipped)
    result_box *= -1

    # Save the resulting average to a new MRC file
    with mrcfile.new(output_mrc, overwrite=True) as mrc:
        mrc.set_data(result_box.astype(np.float32))

    print(f"Saved averaged box to {output_mrc}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process MRC file and average box data around coordinates.")
    parser.add_argument("input_mrc", type=str, help="Input MRC file (tomogram)")
    parser.add_argument("output_mrc", type=str, help="Output MRC file (average)")
    parser.add_argument("coord_file", type=str, help="Coordinates file (x, y, z: space-separated)")
    parser.add_argument("--box_size", type=int, nargs=1, default=100, help="Box size")

    args = parser.parse_args()

    process_mrc(args.input_mrc, args.output_mrc, args.coord_file, args.box_size)
