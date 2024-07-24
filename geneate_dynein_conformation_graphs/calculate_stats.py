import numpy as np
import pandas as pd
import os 
from scipy.stats import chi2_contingency

rawdata_folder = 'Data'
analysis_folder = 'Results'
results_folder = "Stats"

data = []

# Ensure output folder exists
if not os.path.exists(f"{analysis_folder}/{results_folder}"):
    os.makedirs(f"{analysis_folder}/{results_folder}")

for foldername in os.listdir(rawdata_folder):
    if foldername == 'poly01Tomo01':
        continue

    input_file = f'{foldername}_bin4_points.csv'
    input_file_count = f'{foldername}_count.csv'
    input_file_path = f"{analysis_folder}/{foldername}/{input_file}"
    input_file_count_path = f"{analysis_folder}/{foldername}/{input_file_count}"

    export_file = f"{foldername}_statistics.txt"
    export_file_path = f"{analysis_folder}/{results_folder}/{export_file}"

    if os.path.exists(export_file_path):
        os.remove(export_file_path)

    print(f"Currently gettings statistics for {foldername}")

    for dynein_class in [[1],[2,4],[3]]:
        # Ensure input file exists
        if not os.path.exists(input_file_path) and os.path.exists(input_file_count_path):
            print(f"Couldn't find {foldername}, moving on..")
            continue
        
        # Load the nessecary files as dataframes
        df = pd.read_csv(input_file_path)
        df_count = pd.read_csv(input_file_count_path)

        # Filter data for specific doublets and dynein classes
        doublet_1_4 = df[df['Doublet'].isin([1, 2, 3, 4])]
        count_class2_1_4 = doublet_1_4[doublet_1_4['class'].isin(dynein_class)].shape[0]

        doublet_5 = df[df['Doublet'].isin([5])]
        count_class2_5 = doublet_5[doublet_5['class'].isin(dynein_class)].shape[0]

        doublet_6_9 = df[df['Doublet'].isin([6, 7, 8, 9])]
        count_class2_6_9 = doublet_6_9[doublet_6_9['class'].isin(dynein_class)].shape[0]

        # Calculate total counts for each group of doublets
        total_1_4 = df_count[df_count['Doublet'].isin([1, 2, 3, 4])]['Count'].sum()
        total_5 = df_count[df_count['Doublet'].isin([5])]['Count'].sum()
        total_6_9 = df_count[df_count['Doublet'].isin([6, 7, 8, 9])]['Count'].sum()

        # Create contingency tables for Chi-Square tests
        data = np.array([[count_class2_1_4, total_1_4 - count_class2_1_4],
                                [count_class2_5, total_5 - count_class2_5],
                                [count_class2_6_9, total_6_9 - count_class2_6_9]])

        data_1_4_vs_5 = np.array([[count_class2_1_4, total_1_4 - count_class2_1_4],
                                [count_class2_5, total_5 - count_class2_5]])

        data_1_4_vs_6_9 = np.array([[count_class2_1_4, total_1_4 - count_class2_1_4],
                                [count_class2_6_9, total_6_9 - count_class2_6_9]])

        data_5_vs_6_9 = np.array([[count_class2_5, total_5 - count_class2_5],
                                [count_class2_6_9, total_6_9 - count_class2_6_9]])

        # Perform Chi-Square Test
        chi2, p, dof, ex = chi2_contingency(data)

        # Perform pairwise Chi-Square Tests for each pair of groups
        chi2_1_4_vs_5, p_1_4_vs_5, _, _ = chi2_contingency(data_1_4_vs_5)
        chi2_1_4_vs_6_9, p_1_4_vs_6_9, _, _ = chi2_contingency(data_1_4_vs_6_9)
        chi2_5_vs_6_9, p_5_vs_6_9, _, _ = chi2_contingency(data_5_vs_6_9)

        # Apply Bonferroni correction
        alpha = 0.05
        bonferroni_alpha = alpha / 3

        # Write the results
        results = (
            f"Chi-Square Test Results for {dynein_class[0]}:\n"
            f"Chi-Square statistic: {chi2}\n"
            f"P-value: {p}\n"
            f"Degrees of freedom: {dof}\n"
            f"Expected frequencies:\n{ex}\n"
            f"Actual frequencies:\n{data}\n\n"
            "Pairwise Chi-Square Tests with Bonferroni Correction\n"
            f"1-4 vs 5: Chi-Square={chi2_1_4_vs_5}, P-value={p_1_4_vs_5}, Significant={p_1_4_vs_5 < bonferroni_alpha}\n"
            f"1-4 vs 6-9: Chi-Square={chi2_1_4_vs_6_9}, P-value={p_1_4_vs_6_9}, Significant={p_1_4_vs_6_9 < bonferroni_alpha}\n"
            f"5 vs 6-9: Chi-Square={chi2_5_vs_6_9}, P-value={p_5_vs_6_9}, Significant={p_5_vs_6_9 < bonferroni_alpha}\n\n\n"
        )

        # Write the results to a text file
        with open(export_file_path, 'a') as file:
            file.write(results)



