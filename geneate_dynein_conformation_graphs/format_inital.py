import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import yaml

rawdata_folder = 'Data'
analysis_folder = 'Results'
metadata_file = 'metadata.yaml'

# Ensure output folder exists
if not os.path.exists(metadata_file):
    os.makedirs(analysis_folder)

def transform_value_c(x):
    return ((x - 1) % 9) + 1

def transform_value_cc(x):    
    match x:
        case -7:
            return 9
        case -6:
            return 8
        case -5:
            return 7
        case -4:
            return 6
        case -3:
            return 5
        case -2:
            return 4
        case -1:
            return 3
        case 0:
            return 2
        case 1:
            return 1
        case 2:
            return 9
        case 3:
            return 8
        case 4:
            return 7
        case 5:
            return 6
        case 6:
            return 5
        case 7:
            return 4
        case 8:
            return 3
        case 9:
            return 2

def calculate_counts(data):
    df = pd.read_csv(data)
    max_rows = df['Doublet'].value_counts()
    sorted_max_rows = max_rows.sort_index()

    counts_file = f"{foldername}_count.csv"
    counts_file_path = f"{analysis_folder}/{foldername}/{counts_file}"

    sorted_max_rows.reset_index().to_csv(counts_file_path, header=['Doublet', 'Count'], index=False)
    print(f"Succesfully counted the instances of each class for {foldername}")

def show_plot(data):
    df = pd.read_csv(data)

    # Find the maximum number of rows needed for any Doublet
    max_rows = df['Doublet'].value_counts().max()

    # Initialize the table with NaN values
    table_data = np.full((max_rows, 9), np.nan)
    class_data = np.full((max_rows, 9), np.nan)

    # Populate the table with the class values
    for i, doublet in enumerate(sorted(df['Doublet'].unique())):
        doublet_data = df[df['Doublet'] == doublet]['class'].values
        table_data[:len(doublet_data), i] = doublet_data
        class_data[:len(doublet_data), i] = doublet_data

    # Define a color map for the classes => PEET 
    class_colors = {
        1: '#0173b2',
        2: '#de8f05',
        3: '#029e73',
        4: '#de8f05'
    }

    # Create a colormap for class values
    colors = np.vectorize(class_colors.get)(class_data)

    fig, ax = plt.subplots()

    # Hide axes
    ax.xaxis.set_visible(False) 
    ax.yaxis.set_visible(False)
    ax.set_frame_on(False)

    # Create the table
    table = ax.table(cellColours=colors, #cellText=table_data
                    colLabels=[f'Doublet {i+1}' for i in range(9)],
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.07 for i in range(9)])

    # Adjust the font size
    table.auto_set_font_size(True)

    # Scale the table
    table.scale(0.6, 0.35)

    # Figure creation 
    fig_name = f"{foldername}_figure.png"
    fig_path = f"{analysis_folder}/{foldername}/{fig_name}"
    plt.savefig(fig_path, dpi = 600)

    print(f"Succesfully made a figure of {foldername}")

def prepare_metadata():

    metadata = {
            "ready4analysis": False,
            "firstDoublet": {},
            "clockDirection": {},
            "bendDirection": {}
    }

    folder_names = [name for name in os.listdir(rawdata_folder)]

    for folder in folder_names:
        metadata["firstDoublet"][folder] = 0
        metadata["clockDirection"][folder] = "undetermined" 
        metadata["bendDirection"][folder] = "undetermined" 
    
    try:
        with open(metadata_file, 'w') as file:
            file.write("ready4analysis: false\n\n")
            
            file.write("firstDoublet:\n")
            for key, value in metadata["firstDoublet"].items():
                file.write(f"  {key}: {value}\n")
            file.write("\n")
            
            file.write("clockDirection:\n")
            for key, value in metadata["clockDirection"].items():
                file.write(f"  {key}: {value}\n")
            file.write("\n")
            
            file.write("bendDirection:\n")
            for key, value in metadata["bendDirection"].items():
                file.write(f"  {key}: {value}\n")
        print(f"Metadata written to '{metadata_file}' successfully.")
    except IOError as e:
        print(f"Error writing to '{metadata_file}': {e}")

def read_metadata():
    try:
        with open(metadata_file, 'r') as file:
            metadata = yaml.safe_load(file)
        return metadata
    except IOError as e:
        print(f"Error reading '{metadata_file}': {e}")
        return None

# Ensure metadata file exists
if not os.path.exists(metadata_file):
    prepare_metadata()

# Read the metadata file in memory
yaml_file = read_metadata()

# If Ready for analysis is false, return error
if not yaml_file['ready4analysis']:
    print('Please check the metadata file and make sure everything in entered!')
    exit()

# Main loop
for foldername in os.listdir(rawdata_folder):
    input_file = f'{foldername}_bin4_doublets_PtsAdded.mod'
    input_file_path = f"{rawdata_folder}/{foldername}/{input_file}"
    
    output_file = f"{foldername}_bin4_points.txt"
    output_file_path = f"{analysis_folder}/{foldername}/{output_file}"

    class_file = f"04_bin4_classification_MOTL_{foldername}_Iter2.csv"
    class_file_path = f"{rawdata_folder}/{foldername}/{class_file}"

    output_csv_file = f"{foldername}_bin4_points.csv"
    output_csv_file_path = f"{analysis_folder}/{foldername}/{output_csv_file}"

    # Ensure output folder exists
    if not os.path.exists(f"{analysis_folder}/{foldername}"):
        os.makedirs(f"{analysis_folder}/{foldername}")
    
    # Check if required files are there
    if not os.path.exists(input_file_path):
        print(f"{input_file} does not exists, moving on..")
        continue

    if not os.path.exists(class_file_path):
        print(f"{class_file} does not exists, moving on..")
        continue

    print(f"Currently getting the points file for {foldername}")

    # Make a points file
    if not os.path.exists(output_file_path):
        os.system(f"model2point -contour {input_file_path} {output_file_path}")

    print(f"Currently formatting the points file to csv for {foldername}")

    # Read the data from the input file
    data = []
    with open(output_file_path, 'r') as file:
        counter = 1  # Initialize counter
        for line in file:
            columns = line.split() # Split the line into columns based on whitespace
            columns.insert(0, counter) # Insert the counter value at the beginning of the columns list
            data.append(columns)
            counter += 1  # Increment counter

    # Write the data to the CSV file
    with open(output_csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write the header
        writer.writerow(['Point', 'Contour', 'X', 'Y', 'Z'])

        # Write the data
        for row in data:
            writer.writerow(row)

    print(f"Data successfully formatted into .csv")

    # Load the CSV file
    df = pd.read_csv(output_csv_file_path)

    # Determine the correct doublet
    if yaml_file['clockDirection'][foldername] == 'c':
        shift = 1 - yaml_file['firstDoublet'][foldername] # Calculate the relative shift based on first doublet
        df['Doublet'] = df['Contour'] + shift # Apply shift on every data point
        df['Doublet'] = df['Doublet'].apply(transform_value_c) # Correct negative values
    else:
        shift = 1 - yaml_file['firstDoublet'][foldername] 
        df['Doublet'] = df['Contour'] + shift
        df['Doublet'] = df['Doublet'].apply(lambda x: transform_value_cc(x))

    # Load MOTL file
    df_class = pd.read_csv(class_file_path)

    # Parse the right class from MOTL to new csv file
    df['class'] = df_class['class']

    # Save the modified CSV file
    df.to_csv(output_csv_file_path, index=False)

    show_plot(output_csv_file_path)
    calculate_counts(output_csv_file_path)
    print()
    print()









