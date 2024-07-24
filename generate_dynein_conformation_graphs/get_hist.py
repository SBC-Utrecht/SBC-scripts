import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import yaml

rawdata_folder = 'Data'
analysis_folder = 'Results'
metadata_file = 'metadata.yaml'
all_data_straight = pd.DataFrame()
all_data_bend = pd.DataFrame()

# If grouped is True, the individual histograms will be grouped using 1-4, 5, and 6-9 grouping
grouped = True # True or False
grouped_formatted = 'grouped' if grouped else 'single'

# If normalized is True, the individual histograms will be normalized
normalized = True # True or False
normalized_formatted = 'normalized' if normalized else ''

# Ensure metadata file exists
if not os.path.exists(metadata_file):
    print(f"Please run format_initial.py first before making histograms!")
    exit()

def read_metadata():
    try:
        with open(metadata_file, 'r') as file:
            metadata = yaml.safe_load(file)
        return metadata
    except IOError as e:
        print(f"Error reading '{metadata_file}': {e}")
        return None

def generate_figure(input_file_path, output_file_path):
    df = pd.read_csv(input_file_path)

    # Group classes 2 and 4 together
    df['class'] = df['class'].replace({2: 2, 4: 2})

    # Group doublets 1-4 into one group and 6-9 into another
    if grouped == True:
        df['Doublet'] = df['Doublet'].replace({1: '1-4', 2: '1-4', 3: '1-4', 4: '1-4',5: '5', 6: '6-9', 7: '6-9', 8: '6-9', 9: '6-9'})

    # Prepare data for histogram
    # Pivot the data to have Doublet as columns and Class as subcolumns
    pivot_df = df.pivot_table(index='Doublet', columns='class', values='Z', aggfunc='count', fill_value=0)

    # Normalize the counts by the total number of particles in each doublet group
    # axis=1 is one doublet, so sum(axis=1) sums all the classes so the total, then div() divides the indivudual count (axis=0) with the total
    if normalized == True:
        pivot_df = pivot_df.div(pivot_df.sum(axis=1), axis=0)

    # Ensure the order of doublets is 1-4, 5, 6-9
    if grouped == True:
        pivot_df = pivot_df.reindex(['1-4', '5', '6-9'])

    # Custom legend names
    custom_labels = {1: 'Unknown', 2: 'Pre PS', 3: 'Post PS'}

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 8))

    # Define bar width and positions
    bar_width = 0.2
    indices = np.arange(pivot_df.shape[0])

    # Use a colorblind-friendly palette
    colors = sns.color_palette("colorblind", n_colors=len(pivot_df.columns))

    # Plot each class as subcolumns
    for i, (class_label, color) in enumerate(zip(pivot_df.columns, colors)):
        ax.bar(indices + i * bar_width, pivot_df[class_label], bar_width, label=custom_labels[class_label], color=color)

    # Customizing the plot
    ax.set_xlabel('Doublets')
    ax.set_ylabel(f'{normalized_formatted.capitalize()} Count')
    ax.set_title(f'{normalized_formatted.capitalize()} Histogram of Doublets with Classes')
    ax.set_xticks(indices + bar_width)
    ax.set_xticklabels(pivot_df.index)
    ax.legend()

    # Remove old plots because matplotlib doesn't overwrite old files
    if os.path.isfile(output_file_path):
        os.remove(output_file_path)

    # Save the plot
    plt.savefig(output_file_path, dpi = 600)

def generate_combined_histogram(input_file_path, grouped_combined, type):
    # For comments check generate_figure()
    grouped_combined_formatted = 'grouped' if grouped_combined else 'single'

    output_file = f"Combined_histogram_{grouped_combined_formatted}_{type}.png"
    output_file_path = f"{analysis_folder}/{output_file}"

    df = pd.read_csv(input_file_path)

    print(f"Creating the combined histogram for the {type} tomograms in {grouped_combined_formatted} mode")
    
    df['class'] = df['class'].replace({2: 2, 4: 2})

    if grouped_combined == True:
        df['Doublet'] = df['Doublet'].replace({1: '1-4', 2: '1-4', 3: '1-4', 4: '1-4',5: '5', 6: '6-9', 7: '6-9', 8: '6-9', 9: '6-9'})
    
    pivot_df = df.pivot_table(index='Doublet', columns='class', values='Z', aggfunc='count', fill_value=0)
    
    if normalized == True:
        pivot_df = pivot_df.div(pivot_df.sum(axis=1), axis=0)

    if grouped_combined == True:
        pivot_df = pivot_df.reindex(['1-4', '5', '6-9'])

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 8))

    bar_width = 0.2
    indices = np.arange(pivot_df.shape[0])
    colors = sns.color_palette("colorblind", n_colors=len(pivot_df.columns))
    custom_labels = {1: 'Unknown', 2: 'Pre PS', 3: 'Post PS'}

    for i, (class_label, color) in enumerate(zip(pivot_df.columns, colors)):
        ax.bar(indices + i * bar_width, pivot_df[class_label], bar_width, label=custom_labels[class_label], color=color)

    ax.set_xlabel('Doublets')
    ax.set_ylabel(f'{normalized_formatted.capitalize()} Count')
    ax.set_title(f'{normalized_formatted.capitalize()} Histogram of {grouped_combined_formatted} Doublets for all the {type} pieces')
    ax.set_xticks(indices + bar_width)
    ax.set_xticklabels(pivot_df.index)
    ax.legend()

    if os.path.isfile(output_file_path):
        os.remove(output_file_path)

    plt.savefig(output_file_path, dpi = 600)

# Read the metadata file in memory
yaml_file = read_metadata()

# If Ready for analysis is false, return error
if yaml_file is None or not yaml_file['ready4analysis']:
    print('Please check the metadata file and make sure everything in entered!')
    exit()

# Main loop
for foldername in os.listdir(rawdata_folder):
    input_file = f'{foldername}_bin4_points.csv'
    input_file_path = f"{analysis_folder}/{foldername}/{input_file}"
    
    output_file = f"{foldername}_bin4_points_histogram.png"
    output_file_path = f"{analysis_folder}/{foldername}/{output_file}"

    # Ensure input file exists
    if not os.path.exists(input_file_path):
        print(f"Couldn't find {foldername}, moving on..")
        continue
    
    print(f"Currently making the histogram for {foldername}")

    # Make a histogram
    generate_figure(input_file_path, output_file_path)

    # Group all data with same bend direction
    if yaml_file['bendDirection'][foldername] == 'straight':
        df = pd.read_csv(input_file_path)
        all_data_straight = pd.concat([all_data_straight, df])
    elif yaml_file['bendDirection'][foldername] == 'bend':
        df = pd.read_csv(input_file_path)
        all_data_bend = pd.concat([all_data_bend, df])
    else:
        print(f'{foldername} is undetermined, moving on..')
        continue

straight_csv_name = "all_data_straight.csv"
straight_csv_path = f"{analysis_folder}/{straight_csv_name}"    

bend_csv_name = "all_data_bend.csv"
bend_csv_path = f"{analysis_folder}/{bend_csv_name}"

if not all_data_straight.empty:
    all_data_straight.to_csv(straight_csv_path, index=False)

if not all_data_bend.empty:
    all_data_bend.to_csv(bend_csv_path, index=False)

# Generate combined histograms
generate_combined_histogram(straight_csv_path, True, 'straight')
generate_combined_histogram(straight_csv_path, False, 'straight')

generate_combined_histogram(bend_csv_path, True, 'bend')
generate_combined_histogram(bend_csv_path, False, 'bend')