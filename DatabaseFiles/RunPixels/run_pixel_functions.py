import csv
import pandas as pd

def read_metadata_file(metadata_path):
    with open(metadata_path) as f:
        csv.DictReader(f)
        metadata = pd.read_csv(f)
    return metadata

def get_run_pixel_df_for_db(metadata,detector_data):
    zipped_data = list(zip(metadata['Pixel'],metadata['run_numbers'],detector_data,metadata['Source']))
    df = pd.DataFrame(zipped_data, columns=['pixel_number','run_number','detector','source'])
    return df