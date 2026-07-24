import csv
import pandas as pd
import json

def read_metadata_file(metadata_path):
    with open(metadata_path) as f:
        csv.DictReader(f)
        metadata = pd.read_csv(f)
    return metadata

def get_run_metadata(metadata,run_numbers,column):
    data = {}
    for i in range(len(run_numbers)):
        data[i] = metadata.loc[metadata['runnumber']==run_numbers[i],column].iloc[0]
    return data

def get_time_data(run_numbers):
    time = {}
    for i in range(len(run_numbers)):
        with open('../../HistData/TimeData/time_data%d.json'%run_numbers[i], 'r') as file:
            t = json.load(file)
        time[run_numbers[i]] = t
    return time

def get_run_time_and_date(run_numbers,time_data):
    start_time = []
    end_time = []
    date = []
    for run in run_numbers:
        date.append(time_data[run]['0']['subgroup_start'][:10])
        keys = list(time_data[run].keys())
        if len(keys)>1:
            start_time.append(time_data[run][keys[0]]['subgroup_start'][11:])
            end_time.append(time_data[run][keys[-1]]['subgroup_end'][11:])
        else:
            start_time.append(time_data[run][keys[0]]['subgroup_start'][11:])
            end_time.append(time_data[run][keys[0]]['subgroup_end'][11:])
    return start_time, end_time, date

def get_run_df_for_db(run_numbers,metadata,start_time,end_time,date):
    zipped_data = list(zip(run_numbers,list(metadata['UDET bias'].values()),list(metadata['LDET bias'].values()),
                           list(metadata['HV'].values()),list(metadata['MAIN'].values()),list(metadata['UDET'].values()),
                           date,start_time,end_time,list(metadata['ExB voltage'].values()),list(metadata['UDET armor'].values()),
                           list(metadata['UDET ring'].values()),list(metadata['LDET armor'].values()),list(metadata['UDET leakage'].values()),
                           list(metadata['LDET leakage'].values())))
    
    df = pd.DataFrame(zipped_data, columns=['run_number', 'UDET_bias','LDET_bias','HV','MAIN','UDET','date','start_time','end_time',
                                            'ExB','UDET_armor','UDET_ring','LDET_armor','UDET_leakage','LDET_leakage'])
    return df