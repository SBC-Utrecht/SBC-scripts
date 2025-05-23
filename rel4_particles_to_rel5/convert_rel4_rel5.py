import starfile
import pandas as pd
import argparse

def scale_coordinates(star_filename, pixel_sizes):
    # Load the STAR file
    data = starfile.read(star_filename)
    # Check if the required columns exist
    required_columns = ['rlnCoordinateX', 'rlnCoordinateY', 'rlnCoordinateZ', 'rlnDetectorPixelSize']
    if not all(col in data.columns for col in required_columns):
        print(data.columns)
        print(f"Missing columns: {set(required_columns)-set(data.columns)}")
        raise ValueError(f"A RELION4 STAR file must contain the columns: {required_columns}")

    # Check if the required columns exist
    # same guestimate pytom-match-pick uses
    center_x = pixel_sizes[0] / 2
    center_y = pixel_sizes[1] / 2
    center_z = pixel_sizes[2] / 2
    # Multiply each coordinate by the corresponding pixel size and detector pixel size
    data['rlnCoordinateX'] = (data['rlnCoordinateX'] - center_x) * data['rlnDetectorPixelSize']
    data['rlnCoordinateY'] = (data['rlnCoordinateY'] - center_y) * data['rlnDetectorPixelSize']
    data['rlnCoordinateZ'] = (data['rlnCoordinateZ'] - center_z) * data['rlnDetectorPixelSize']

    column_change = {
        "rlnCoordinateX": "rlnCenteredCoordinateXAngst",
        "rlnCoordinateY": "rlnCenteredCoordinateYAngst",
        "rlnCoordinateZ": "rlnCenteredCoordinateZAngst",
        "rlnMicrographName": "rlnTomoName",
        "rlnDetectorPixelSize": "rlnTomoTiltSeriesPixelSize",
    }
    data = data.rename(columns=column_change)

    # Write the updated data to a new STAR file
    output_filename = star_filename.replace('.star', '_rf5.star')
    starfile.write({"particles":data}, output_filename, overwrite=True)

    print(f"RELION5 coordinates written to: {output_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scale coordinates in a STAR file by pixel sizes and detector pixel size.")
    parser.add_argument("starfile", type=str, help="Path to the input STAR file")
    parser.add_argument("pixel_x", type=float, help="Pixel size in X dimension")
    parser.add_argument("pixel_y", type=float, help="Pixel size in Y dimension")
    parser.add_argument("pixel_z", type=float, help="Pixel size in Z dimension")

    args = parser.parse_args()
    pixel_sizes = (args.pixel_x, args.pixel_y, args.pixel_z)

    scale_coordinates(args.starfile, pixel_sizes)
