'''
This script groups redundant observations,
which are close in space.

Yelp reports the lat lng coords of some venues to 13 decimal places.
This is unrealistically precise.

I'll round them up to the 4th decimal place to
collapse points that are within about 10m of each other.

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

bars = pd.read_csv('/Users/Ben/Dropbox/Insight/yelp-scrape/bars.csv')
restaurants = pd.read_csv('/Users/Ben/Dropbox/Insight/yelp-scrape/restaurants.csv')

combined = pd.concat([bars, restaurants])


# checking for duplicates
print('listed restaurants and bars:')
print(len(combined))

uncombined = combined.drop_duplicates()

print('unique restaurants and bars:')
print(len(uncombined))
# only two duplicates

# collapsing points within 10 m of each other
# round coords
combined.lat = np.round(combined.lat, decimals = 4)
combined.lng = np.round(combined.lng, decimals = 4)

# aggregate similar values
gb = combined.groupby(['lat', 'lng'])
grouped = gb.agg({
	'lat': pd.Series.unique, 
	'lng': pd.Series.unique
	}
	)
counts = gb.size().to_frame(name = 'n_agg')

combined = grouped.join(counts)
combined = combined.reset_index(drop = True)

print('Grouped by location:')
print(len(combined))

combined.to_csv('/Users/Ben/Dropbox/Insight/yelp-scrape/bars-rests-combined.csv')


