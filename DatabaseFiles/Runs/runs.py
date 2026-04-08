import sys
import run_functions as rf

metadata = rf.read_metadata_file('GrafanaMetaDataFrom10_10_25_to_12_03_25.csv')

calibrated_runs = []
for line in sys.stdin:
    run = line.strip()
    calibrated_runs.append(int(run))

run_metadata_columns = ['HV','UDET','MAIN','UDET bias','LDET bias','LDET leakage','UDET leakage','LDET armor','UDET armor','UDET ring','ExB voltage']

run_metadata = {}
for column in run_metadata_columns:
    run_metadata[column] = rf.get_run_metadata(metadata,calibrated_runs,column)

time_data = rf.get_time_data(calibrated_runs)
start_time, end_time, date = rf.get_run_time_and_date(calibrated_runs,time_data)

run_df = rf.get_run_df_for_db(calibrated_runs,run_metadata,start_time,end_time,date)

run_df.to_csv('run_db.csv', index=False)