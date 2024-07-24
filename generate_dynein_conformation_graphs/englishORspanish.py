import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt

# Declaring important folders
rawdata_folder = 'Data'
analysis_folder = 'Results'
results_folder = "EORS"

# Ensure output folder exists
if not os.path.exists(f"{analysis_folder}/{results_folder}"):
    os.makedirs(f"{analysis_folder}/{results_folder}")

# Declare the results overview file and remove it if it already exists
overview_results = "overview_bending_results.txt"
overview_results_path = f"{analysis_folder}/{results_folder}/{overview_results}"

if os.path.exists(overview_results_path):
    os.remove(overview_results_path)

# Adjustable parameters, print_results prints intermediate results into the console and show_plots displays the relevant plots while the code is running. This is useful for debugging for explaining what the code is doing.
print_results = False
show_plots = False

# Function to calculate the angles between direction vectors of segments
def calculate_angles(data, num_segments, angle_threshold):
    # Calculate the length of each segment
    segment_length = len(data) // num_segments

    # Initialize empty lists
    direction_vectors = [] # Initialize a list to store the direction vectors of each segment
    angles = [] # Initialize a list to store the angles between consecutive direction vectors

    # Loop through the data to create direction vectors for each segment
    for i in range(num_segments):
        # Extract the segment from the data
        segment = data[i * segment_length:(i + 1) * segment_length]
        
        # Calculate the mean of the segment
        segment_mean = segment.mean(axis=0)

        # Perform Singular Value Decomposition (SVD) on the mean-centered segment
        uu, dd, vv = np.linalg.svd(segment - segment_mean)
        
        # The first right singular vector (vv[0]) represents the direction of the segment
        direction_vectors.append(vv[0])

    # Loop through the direction vectors to calculate angles between consecutive vectors    
    for i in range(len(direction_vectors) - 1):
        vec1 = direction_vectors[i]
        vec2 = direction_vectors[i + 1]
        
        # Calculate the cosine of the angle between the two vectors   
        # Using np.clip to prevent numerical issues by ensuring the cosine value is within [-1, 1]     
        angle = np.arccos(np.clip(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)), -1.0, 1.0))
        
        # Calculate the angle in degrees
        angle_degrees = np.degrees(angle)

        # Filter out angles that are greater than the angle_threshold
        if angle_degrees <= angle_threshold: 
            angles.append(angle_degrees)
    
    return angles

# Function to process the angle data 
def calculate_fit(data_lists, foldername):
    # Adjustable parameters, after optimizing, these were the best settings
    angle_threshold = 6  # When the angle is greater than x degrees, it is considered a bend
    bend_threshold = 100 # Everything greater than x degrees, will be removed because junkdata
    num_segments = 10    # How many segments per doublet

    # Initialize empty lists
    all_angles = [] 
    bent_lists = [] 
    bending_amounts = []
    angle_differences = []

    # Loop through each doublet of data points
    for index, data in enumerate(data_lists):
        # Calculate angles for the current doublet
        angles = calculate_angles(data, num_segments, bend_threshold)
        all_angles.append(angles)
        
        # Sum of absolute angles as bending metric
        bending_amount = np.sum(np.abs(angles))  
        bending_amounts.append(bending_amount)

        # Filter all angles greater than the angle_threshold
        if any(angle > angle_threshold for angle in angles):
            bent_lists.append(index+1)

    # Print results
    if print_results:
        for i, (angles, bending_amount) in enumerate(zip(all_angles, bending_amounts), start=1):
            print(f"Angles for list {i} (in degrees): {angles}")
            print(f"Bending amount for list {i}: {bending_amount}")

    # Calculate the aggregate bending scores
    mean_bending = np.mean(bending_amounts)
    max_bending = np.max(bending_amounts)

    # Calculate max angle difference
    for doublet in all_angles:
        min_angle = np.min(doublet)
        max_angle = np.max(doublet)

        angle_difference = max_angle - min_angle
        angle_differences.append(angle_difference)

    angle_differences_average = np.average(angle_differences)

    # Draw a conclusion based on the presence of bends 
    if bent_lists:
        result = f"Doublets likely to have a bend: {bent_lists}"
    else:
        result = "All doublets are likely straight."

    # Write results to a file in the EORS folder
    # Note if you want to have the results in Results/poly01Tomo01 folder for example, you should change {results_folder} to {foldername}
    single_result = f"{foldername}_bending_results.txt"
    single_result_path = f"{analysis_folder}/{results_folder}/{single_result}"

    with open(single_result_path, "w") as file:
        for i, (angles, bending_amount, angle_difference) in enumerate(zip(all_angles, bending_amounts, angle_differences), start=1):            
            file.write(f"Angles for doublet {i} (in degrees): {angles}\n")
            file.write(f"Max angle difference: {angle_difference}\n")
            file.write(f"Bending amount for doublet {i}: {bending_amount}\n\n")
    
        file.write(f"\nAggregate Scores:\n")
        file.write(f"Mean Bending Amount: {mean_bending}\n")
        file.write(f"Average angle difference: {angle_differences_average}\n")
        file.write(f"Maximum Bending Amount: {max_bending}\n")
        
        file.write(f"{result}")

    print(f"Results written to {single_result}\n")

    # Write results to a single file which will contains a summary of the analysis
    with open(overview_results_path, "a") as file:
        file.write(f"Aggregate Scores for {foldername}:\n")
        file.write(f"Mean Bending Amount: {mean_bending}\n")
        file.write(f"Average angle difference: {angle_differences_average}\n")
        file.write(f"Maximum Bending Amount: {max_bending}\n")
        
        file.write(f"{result}\n\n")

    # Visualize the bending amounts in a bar graph
    if show_plots:
        plt.figure()
        plt.bar(range(1,10), bending_amounts, color='blue')
        plt.xlabel('List Index')
        plt.ylabel('Bending Amount (degrees)')
        plt.title('Bending Amount for Each List')
        plt.show()

    # Plot the data and the segments
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        colors = plt.cm.jet(np.linspace(0, 1, 9))

        for data, color in zip(data_lists, colors):
            segment_length = len(data) // 10
            for i in range(10):
                segment = data[i * segment_length:(i + 1) * segment_length]
                ax.scatter3D(segment[:, 0], segment[:, 1], segment[:, 2], color=color)

        plt.show()

# Main loop
for foldername in os.listdir(rawdata_folder):
    points_list = []

    input_file = f'{foldername}_bin4_points.csv'
    input_file_path = f"{analysis_folder}/{foldername}/{input_file}"

    # Ensure input file exists
    if not os.path.exists(input_file_path):
        print(f"Couldn't find {foldername}, moving on..\n")
        continue
    
    print(f"Currently calculating the EORS score for {foldername}")

    df = pd.read_csv(input_file_path)

    # Looping through each doublet 
    for doublet in range(1,10):
        # Filter the data based on in which doublet they are 
        filtered_df = df.query(f'Doublet == {doublet}')

        # Extract the X, Y and Z coordinates of each point
        points_xyz = filtered_df[['X', 'Y', 'Z']].values.tolist()

        points_xyz = np.array(points_xyz)
        points_list.append(points_xyz)

    calculate_fit(points_list, foldername)