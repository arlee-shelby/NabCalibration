from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys
import fnmatch
import os
import time
import nabPy as Nab
import numpy as np
import json
import pandas as pd

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-r', '--run_number', type=int, default=None, help='run to process')
parser.add_argument('-p', '--pixels', type = int, default=[], nargs="*", help='pixels to get')
parser.add_argument('-d', '--directory', type = str, default='', help='run directory')
parser.add_argument('-dt', '--detector_type', type = str, default='', help='UDET or LDET')

args = vars(parser.parse_args())

if args['run_number']==None:
    print('Run number not specified')
    sys.exit(1)

if args['pixels']==[]:
    print('No pixels specified')
    sys.exit(1)

if args['directory']=='':
    print('No directory specified')
    sys.exit(1)

if args['detector_type']=='':
    print('No detector type specified')
    sys.exit(1)


run_number = args['run_number']
pixels = args['pixels']
directory = args['directory']
detector_type = args['detector_type']

num_files = len(fnmatch.filter(os.listdir(directory),'Run%d*'%run_number))
print('There are %d subruns in run %d'%(num_files,run_number))

cnt = 0
if int(num_files/15) == num_files/15:
    num_sub_groups= int(num_files/15)
else:
    num_sub_groups = int(num_files/15) + 1

print(num_sub_groups)

time_df = {}
energy_df = {}
energy_df['hist'] = {}
energy_df['bin_edges'] = {}

for i in range(num_sub_groups):
    time_df[i] = {}
    energy_df['hist'][i] = {}
    energy_df['bin_edges'][i] = {}
    subRunMin= i*15
    subRunMax= subRunMin+14

    start1 = time.time()
    run = Nab.DataRun(directory, run_number,subRunMin=subRunMin,subRunMax=subRunMax)
    end1 = time.time()
    print("Time to get run for sub group %d:"%i,(end1-start1),"s")


    start2 = time.time()
    results = run.singleWaves().determineEnergyTiming(method='trap', params=[1250,50,1250])
    end2 = time.time()
    print("Time to apply trap filter for sub group%d:"%i,(end2-start2),"s")

    headers = run.singleWaves().headers()
    max_unix_timestamp = max(headers['unix timestamp'])*4
    min_unix_timestamp = min(headers['unix timestamp'])*4

    start_of_group = pd.to_datetime(min_unix_timestamp, unit='ns').strftime('%Y-%m-%dT%H:%M:%S')
    end_of_group = pd.to_datetime(max_unix_timestamp, unit='ns').strftime('%Y-%m-%dT%H:%M:%S')

    time_df[i]['subgroup_start'] = start_of_group
    time_df[i]['subgroup_end'] = end_of_group

    for j in range(len(pixels)):
        results.resetCuts()
        results.defineCut('pixel', '=', pixels[j])
        hist,bin_edges = np.histogram(results.data()['energy'],bins = np.arange(0,4500))
        energy_df['hist'][i][pixels[j]] = hist.tolist()
        energy_df['bin_edges'][i][pixels[j]] = bin_edges.tolist()


with open("../../HistData/TimeData/time_data%d.json"%run_number, "w") as json_file:
    json.dump(time_df, json_file)

with open("../../HistData/EnergyData/%s/%senergy_data%d.json"%(detector_type,detector_type,run_number), "w") as json_file:
    json.dump(energy_df, json_file)

print("done getting results for run!!!")