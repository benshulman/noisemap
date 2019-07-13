'''
Make a grid for request yelp hits
First sample an even grid across the lat lng box.
Then calculate the predictor values for those points
'''
import pandas as pd
import numpy as np
import itertools
import geopy.distance
from yelpapi import YelpAPI

yelp_api = YelpAPI('')

# bounds
top = 42.419
bottom = 42.23
left = -71.20
right = -70.95

step = 0.01 # close to 1000m spacing in lat and long degrees
lat_steps = int((top - bottom)/step)
long_steps = int((right - left)/step)

lats = np.linspace(bottom, top, num = lat_steps)
longs = np.linspace(right, left, num = long_steps)

latlong_pairs = list(itertools.product(lats, longs))

def rests_call(latlong):
    '''
    takes as input a pair of lat and lng
    returns list of tuples of restaurant locations
    '''

    # first call
    results = yelp_api.search_query(
        categories='restaurants',
        latitude = latlong[0],
        longitude= latlong[1],
        limit=50)

    # extract to list of tuples
    rests = [(
        r['name'],
        r['coordinates']['latitude'],
        r['coordinates']['longitude']) for r in results['businesses']]

    return rests

# first call
restaurants = rests_call(latlong_pairs[0])

# make df
restaurants = pd.DataFrame(restaurants, columns = ['name', 'lat', 'lng'])

# loop
for latlng in latlong_pairs[1:]:
    # get rests
    rests_temp = rests_call(latlng)

    # make df
    rests_temp = pd.DataFrame(rests_temp, columns = ['name', 'lat', 'lng'])

    # add to main df
    rests = rests.append(rests_temp)
    rests = rests.drop_duplicates()
    print(str(len(rests)))

restaurants = restaurants.reset_index(drop = True)
restaurants.to_csv('/Users/Ben/Dropbox/Insight/yelp-scrape/restaurants.csv')