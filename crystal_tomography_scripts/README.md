Utility scripts for cryogenic electron tomography on protein crystal fragments

create_template.py creates a subvolume centered on input coordinates that may serve as a template in template matching procedures
Usage: average_coordinates.py tomogram_in.mrc template_out.mrc x,y,z box_size

average_coordinates.py averages subvolumes centered on a list of coordinates and outputs this average
Usage: average_coordinates.py tomogram_in.mrc average_out.mrc coordinates_in.txt [--box_size 100]  
