# Readme for how to use the scrips
There are a few scripts and files in this folder which are quite important. You can call all these functions using python3:

```shell
python3 <script.py>
```

## format_inital.py
This is the main script that kickstarts everything. It makes all the nessecary folder and checks whether all the nessecary files are present. It starts by getting a points file from the .mod file using the model2point command from PEET. After which a new csv file is made with the XYZ coordinates and the contour of each point. After which the corrected doublet is calculated based on the metadata file. Lastly the corrected doublet and the class is added to each point in the csv. 

Lastly lastly, the table is created using show_plot() and the count for each column is calculated using calculate_counts().

## get_hist.py
This is the script that generates the histograms, the individual ones but also the combined ones. At the very top you can choose whether you want grouped or single histograms meaning if you want to group doublets 1-4 and 6-9. You can also choose if you want to normalize the data, if you want to do so, leave normalized on True. 

## englishORspanish.py
Don't ask me why this name. This is a small passion project which I thought I could knock out in an hour, I was mistaken. Anyway, the idea is that each doublet is split into 10 equal parts. After that, the code fill calculate the vector of the line through those points. Then it will calculate the difference between the current point and the next point. This way you can very accurately calculate bends in the doublet because two sections would differ from one another quite significantly. 

There are again some options at the top, print_results is whether you want a ton of logs in the console (mainly for debugging purposes) and show_plots is whether you want to get plots for each tomogram. There are two plots, one bar plot with the changes in degrees for different doublets. And the other is a 3D scatter plot where you can see the doublets and their segments.

## calculate_stats.py
This is a small passion project. It is using the chi2 test to calculate whether certain classes in the pooled (or grouped) histograms are significant. It is using a bonferoni correction of 3 (because there are 3 individual tests conducted). 

## metadata.yaml
Example metadata file
```yaml
ready4analysis: True

firstDoublet:
  poly01Tomo01: 5
  poly02Tomo06: 1
  poly02Tomo07: 1
  poly03Tomo13: 6
  poly12Tomo34: 1
  poly12Tomo45: 1
  poly12Tomo47: 5
  poly12Tomo56: 5
  poly12Tomo57: 1
  poly12Tomo59: 6

clockDirection:
  poly01Tomo01: c
  poly02Tomo06: cc
  poly02Tomo07: cc
  poly03Tomo13: c
  poly12Tomo34: c
  poly12Tomo45: c
  poly12Tomo47: c
  poly12Tomo56: c
  poly12Tomo57: cc
  poly12Tomo59: cc

bendDirection:
  poly01Tomo01: undetermined
  poly02Tomo06: straight
  poly02Tomo07: straight
  poly03Tomo13: undetermined
  poly12Tomo34: undetermined
  poly12Tomo45: straight
  poly12Tomo47: bend
  poly12Tomo56: straight
  poly12Tomo57: bend
  poly12Tomo59: straight
```

### Folder structure
This should be the rough folder structure. You can of course add more tomograms in the /Data folder

geneate_dynein_conformation_graphs/
├── calculate_stats.py
├── englishORspanish.py
├── format_inital.py
├── get_hist.py
├── README.md
└── Data/
    ├── poly01Tomo01/
    │   ├── 04_bin4_classification_MOTL_poly01Tomo01_Iter2.csv
    │   └── poly01Tomo01_bin4_doublets_PtsAdded.mod
    ├── poly02Tomo06/
    │   ├── 04_bin4_classification_MOTL_poly02Tomo06_Iter2.csv
    │   └── poly02Tomo06_bin4_doublets_PtsAdded.mod
    └── poly02Tomo07/
        ├── 04_bin4_classification_MOTL_poly02Tomo07_Iter2.csv
        └── poly02Tomo07_bin4_doublets_PtsAdded.mod