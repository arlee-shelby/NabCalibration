# NabCalibration
This is a repository for the Nab Collaboration with all of my code I have used (during Fall 2025) to process the raw data (stored on GT), fit the spectrum data, calibrate the data, and output the results to be stored on a PostgreSQL database on GT. 

## Data Processing
### Main Files
The main files to process data on GT are in the folder "DataProcessingGT". There are four folders within that:
 - JobMakers
 - JobScripts
 - RunPixelMappingFiles
 - nabPyDataProcessing
   
The main python scripts that process the raw data are in "nabPyDataProcessing". These files process the hdf5 files and output an energy hisogram of specified pixels as a .json file. As an example, to process the source data you can run:
```shell
$ python get_pixels_hist_df.py -dt UDET -d /storage/ideas/is-ajezghani3-0/TempCal/ -r 8624 -p 26 40 29 43 74 78
```
where 
 - dt ("detector_type") specifies the detector
 - d ("directory") specifies the directory where the run data is stored on GT
 - r ("run_number") specifies the run number
 - p ("pixels") specifies the pixels to process, each separated by a space after the flag

The file will output the data in the "HistData/EnergyData/" folder in the appropriate associated detector type subfolder. In order to optimize the data processing, the file will process up to 15 subruns at a time and index a dictionary object for each subgroup of 15 subruns. Meaning, if there are 32 subruns, there will be 3 subgroups, the first two with 15 subruns each, and the last with 2 subruns. Index 0 in the output file corresponds to the first 15 subruns (the first subgroup), index 1 corresponds to the second 15 subruns (the second subgroup), etc. The pulser data processing script is run in a similar manor and the output is stored in "HistData/PulserData/" in the associated detector type subfolder. 

### Additional Files
To process a lot of run data more efficiently, I create and submit batch scripts on GT for each run. To more efficiently create these scripts, I use ROOT to run files that create batch scripts for each run and a final shell script to submit all the runs to GT. These files are in the "JobMakers" folder. To run the scripts you must have ROOT installed. As an example, they can be run like:
```shell
$ root
```
```shell
root [0] .L run_maker.cpp
```
```shell
root [1] Looper()
```
This will output batch files for the runs you specify in the .cpp file in the "JobScripts" folder. It will also output a fild like "SubmitManyJobsGT.sh" that makes each run batch file executable and submits the batch job to GT. 

## Data Analysis
Once the data has been process, you can follow the jupyter-notebook "DataAnalysisExample" which shows how I read out the .json files and calibrate data. All the functions and data you need to run the notebook are in this repo. 
