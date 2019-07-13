'''
Noise clean

The NoiseTube app samples every second or two, 
so having it run in place for a minute can 
produce 10s of fairly redundant observations.

This script will group redundant observations,
which are close in time and space
and take their average noise level.

The NoiseTube coordinates have precision to 6 decimal places.
I'll round them up to the 3rd decimal place to
compare points that are within about 100m of each other.

From https://gis.stackexchange.com/a/8674

The tens digit gives a position to about 1,000 kilometers.
It gives us useful information about what continent or ocean we are
on. 

The units digit (one decimal degree) gives a position up to 111
kilometers (60 nautical miles, about 69 miles). It can tell us roughly
what large state or country we are in. 

The first decimal place is worth up to 11.1 km: it can distinguish the
position of one large city from a neighboring large city. 

The second decimal place is worth up to 1.1 km: it can separate one
village from the next. 

The third decimal place is worth up to 110 m: it can identify a large
agricultural field or institutional campus.

The fourth decimal place is worth up to 11 m: it can identify a parcel
of land. It is comparable to the typical accuracy of an uncorrected
GPS unit with no interference. 

The fifth decimal place is worth up to
1.1 m: it distinguish trees from each other. Accuracy to this level
with commercial GPS units can only be achieved with differential
correction.

The sixth decimal place is worth up to 0.11 m: you can
use this for laying out structures in detail, for designing
landscapes, building roads. It should be more than good enough for
tracking movements of glaciers and rivers. This can be achieved by
taking painstaking measures with GPS, such as differentially corrected
GPS. 

The seventh decimal place is worth up to 11 mm: this is good for
much surveying and is near the limit of what GPS-based techniques can
achieve. 

The eighth decimal place is worth up to 1.1 mm: this is good
for charting motions of tectonic plates and movements of volcanoes.
Permanent, corrected, constantly-running GPS base stations might be
able to achieve this level of accuracy.

The ninth decimal place is
worth up to 110 microns: we are getting into the range of microscopy.
For almost any conceivable application with earth positions, this is
overkill and will be more precise than the accuracy of any surveying
device
'''

import pandas as pd
import numpy as np
import re
from os import listdir

# get all the noise-tube files
file_path = '/Users/Ben/Dropbox/Insight/noisetube-scrape/'
file_names = listdir(file_path)
file_names = [file for file in file_names if 'noise-tube.csv' in file]

file_list = list()
for file in file_names:
    city_name = re.search(
        re.compile(r"^[^-]*"),
        file).group(0)
    df = pd.read_csv(file_path + file)
    df['city'] = city_name
    file_list.append(df)

noise = pd.concat(file_list, axis = 0, ignore_index = True)

# drop obs missing location
noise = noise.dropna(subset = ['lat', 'lng'])
noise = noise[(noise.lat != 0) & (noise.lng != 0)]

# structure time
noise.made_at = pd.to_datetime(noise.made_at)
# extract minute and hour
# to average them when aggregating
noise['hour'] = noise.made_at.dt.hour
noise['minute'] = noise.made_at.dt.minute
# day of the week
noise['day'] = noise.made_at.dt.dayofweek

# 15 minute intervals for grouping
noise['qtr_hr'] = round(noise.minute / 15)

# round coords
noise['lat_rnd'] = np.round(noise.lat, decimals = 3)
noise['lng_rnd'] = np.round(noise.lng, decimals = 3)

# aggregate similar values
gb = noise.groupby(['lat_rnd', 'lng_rnd', 'hour', 'qtr_hr', 'day'])
counts = gb.size().to_frame(name = 'n_agg')
grouped = gb.agg({
	'lat': 'mean', 
	'lng': 'mean',
	'minute': 'mean',
	'loudness': 'mean',
	'city': pd.Series.unique
	}
	)
grouped = grouped.join(counts)
grouped = grouped.reset_index()

grouped = grouped.loc[:, ['lat', 'lng', 'day', 'minute', 'hour', 'loudness', 'city', 'n_agg']]

grouped.to_csv('/Users/Ben/Dropbox/Insight/noisetube-scrape/noise-tube-clean.csv')