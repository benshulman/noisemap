'''
Trim NoiseTube observations to keep only those within a bounding box
Some samples were way out in the middle of nowhere, I'll discard those.
I chose a bounding box by examining observations on
the map in eda-nt-clean.ipynb.
'''
import pandas as pd

noise = pd.read_csv('/Users/Ben/Dropbox/Insight/noisescore/noise-score-clean.csv')

print(
	'N obs unboxed: ' +
	str(len(noise))
	)

bounds = [[42.23, -71.20], [42.419, -70.95]]

noise_boxed = noise[(
	# bottom
	(noise.lat > bounds[0][0]) &
	# top
	(noise.lat < bounds[1][0]) &
	# left
	(noise.lng > bounds[0][1]) &
	# right
	(noise.lng < bounds[1][1])
	)].reset_index(drop = True).drop('Unnamed: 0', axis = 1)

print(
	'N obs boxed: ' +
	str(len(noise_boxed))
	)

noise_boxed.to_csv('/Users/Ben/Dropbox/Insight/noisescore/noise-score-boxed.csv')