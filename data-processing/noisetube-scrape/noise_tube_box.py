'''
Trim NoiseTube observations to keep only those within a bounding box
Some samples were way out in the middle of nowhere, I'll discard those.
I chose a bounding box by examining observations on
the map in eda-nt-clean.ipynb.
'''
import pandas as pd

# take in a df and filter rows to within a bounding box
def box_filter(in_df, # input df with columns for lat an lng
    lat = 'lat', # lat lng col names
    lng = 'lng',
    bounds = [[42.23, -71.20], [42.419, -70.95]]):
    out_df = in_df[(
        # bottom
        (in_df[lat] > bounds[0][0]) &
        # top
        (in_df[lat] < bounds[1][0]) &
        # left
        (in_df[lng] > bounds[0][1]) &
        # right
        (in_df[lng] < bounds[1][1])
        )].reset_index(drop = True)
    return out_df

noise = pd.read_csv('/Users/Ben/Dropbox/Insight/noisetube-scrape/noise-tube-clean.csv')

print(
	'N obs unboxed: ' +
	str(len(noise))
	)

noise_boxed = box_filter(noise)
noise_boxed = noise_boxed.drop('Unnamed: 0', axis = 1)

print(
	'N obs boxed: ' +
	str(len(noise_boxed))
	)

noise_boxed.to_csv('/Users/Ben/Dropbox/Insight/noisetube-scrape/noise-tube-boxed.csv')