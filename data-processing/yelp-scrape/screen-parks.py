'''
This script screens park entries scrapped from Yelp in yelp-scrape-parks.py
I'm listing which are dog parks or islands.
'''
import pandas as pd

parks = pd.read_csv('/Users/Ben/Dropbox/Insight/yelp-scrape/parks.csv')
parks = parks.drop('Unnamed: 0', axis = 1)

parks_out = parks[~ parks.name.str.contains("Dog")]
parks_out = parks_out[~ parks_out.name.str.contains("Island")]

print(str(len(parks)), str(len(parks_out)))

parks_out.to_csv('/Users/Ben/Dropbox/Insight/yelp-scrape/parks_clean.csv')