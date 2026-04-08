import run_pixel_functions as runpixf

metadata = runpixf.read_metadata_file('UDETSourcePixelTracking.csv')

detector_data = detector = ['UDET: VALENTINE']*len(metadata)

run_pixel_df = runpixf.get_run_pixel_df_for_db(metadata,detector_data)

run_pixel_df.to_csv('run_pixel_db.csv', index=False)
