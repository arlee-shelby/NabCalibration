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
parser.add_argument('-d', '--directory', type = str, default='', help='run directory')

args = vars(parser.parse_args())

if args['run_number']==None:
    print('Run number not specified')
    sys.exit(1)


if args['directory']=='':
    print('No directory specified')
    sys.exit(1)


run_number = args['run_number']
directory = args['directory']

num_files = len(fnmatch.filter(os.listdir(directory),'Run%d*'%run_number))
print('There are %d subruns in run %d'%(num_files,run_number))

cnt = 0
if int(num_files/15) == num_files/15:
    num_sub_groups= int(num_files/15)
else:
    num_sub_groups = int(num_files/15) + 1

print(num_sub_groups)

pulser_df = {}
pulser_df['hist'] = {}
pulser_df['bin_edges'] = {}

for i in range(num_sub_groups):
    pulser_df['hist'][i] = {}
    pulser_df['bin_edges'][i] = {}
    subRunMin= i*15
    subRunMax= subRunMin+14

    start1 = time.time()
    run = Nab.DataRun(directory, run_number,subRunMin=subRunMin,subRunMax=subRunMax)
    end1 = time.time()
    print("Time to get run for sub group %d:"%i,(end1-start1),"s")


    start2 = time.time()
    results = run.pulsrWaves().determineEnergyTiming(method='trap', params=[1250,50,1250])
    end2 = time.time()
    print("Time to apply trap filter for sub group%d:"%i,(end2-start2),"s")

    for j in range(1,128):
        results.resetCuts()
        results.defineCut('pixel', '=', int(j))
        hist,bin_edges = np.histogram(results.data()['energy'],bins = np.arange(0,10000))
        pulser_df['hist'][i][j] = hist.tolist()
        pulser_df['bin_edges'][i][j] = bin_edges.tolist()

    for j in range(1001,1128):
        results.resetCuts()
        results.defineCut('pixel', '=', int(j))
        hist,bin_edges = np.histogram(results.data()['energy'],bins = np.arange(0,10000))
        pulser_df['hist'][i][j] = hist.tolist()
        pulser_df['bin_edges'][i][j] = bin_edges.tolist()

    run.pulsrWaves().resetCuts()
    run.pulsrWaves().defineCut('bc', '=',118)

    results_pulser = run.pulsrWaves().determineEnergyTiming(method='trap', params=[1250,50,1250])
    hist,bin_edges = np.histogram(results_pulser.data()['energy'],bins = np.arange(0,10000))
    
    pulser_df['hist'][i]['pulser BC 118'] = hist.tolist()
    pulser_df['bin_edges'][i]['pulser BC 118'] = bin_edges.tolist()


    run.pulsrWaves().resetCuts()
    run.pulsrWaves().defineCut('bc', '=',112)
    print("getting BC 112")
    results_pulser = run.pulsrWaves().determineEnergyTiming(method='trap', params=[50,250,1000000])
    hist,bin_edges = np.histogram(results_pulser.data()['energy'],bins = np.arange(-10000,10000))
    
    pulser_df['hist'][i]['pulser BC 112'] = hist.tolist()
    pulser_df['bin_edges'][i]['pulser BC 112'] = bin_edges.tolist()

    run.pulsrWaves().resetCuts()
    run.pulsrWaves().defineCut('bc', '=',230)

    results_pulser = run.pulsrWaves().determineEnergyTiming(method='trap', params=[1250,50,1250])
    hist,bin_edges = np.histogram(results_pulser.data()['energy'],bins = np.arange(0,10000))
    
    pulser_df['hist'][i]['pulser BC 230'] = hist.tolist()
    pulser_df['bin_edges'][i]['pulser BC 230'] = bin_edges.tolist()
    
    run.pulsrWaves().resetCuts()
    run.pulsrWaves().defineCut('bc', '=',223)

    results_pulser = run.pulsrWaves().determineEnergyTiming(method='trap', params=[50,250,1000000])
    hist,bin_edges = np.histogram(results_pulser.data()['energy'],bins = np.arange(-10000,10000))
    
    pulser_df['hist'][i]['pulser BC 223'] = hist.tolist()
    pulser_df['bin_edges'][i]['pulser BC 223'] = bin_edges.tolist()

with open("../../HistData/PulserData/pulser_data%d.json"%run_number, "w") as json_file:
    json.dump(pulser_df, json_file)
    json_file.flush()
    os.fsync(json_file.fileno())
print("done getting results for run!!!")
print("exists immediately:", os.path.exists("../../HistData/PulserData/pulser_data%d.json"%run_number))
time.sleep(2)