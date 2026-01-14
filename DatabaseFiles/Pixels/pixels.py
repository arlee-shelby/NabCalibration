with open('/Users/arleeshelby/Downloads/SourcePixelTracking.csv') as f:
    csv.DictReader(f)
    pix_source = pd.read_csv(f)

pix_source.loc[pix_source['Pixel']==11]