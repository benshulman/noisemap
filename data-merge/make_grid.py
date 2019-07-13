'''
Make a grid for predictions
Sample an even grid across the lat lng box.
Then we can calculate the predictor values for those points
'''
import pandas as pd
import numpy as np
import itertools, pickle
from shapely.geometry import Point, MultiPoint
from shapely import geometry

# bounds
bounds = [[42.24, -71.20], [42.419, -70.94]]
bottom = bounds[0][0]
top = bounds[1][0]
right = bounds[1][1]
left = bounds[0][1]

step = 0.001 # close to 100m spacing in lat and long degrees
lat_steps = int((top - bottom)/step)
long_steps = int((right - left)/step)

lats = np.linspace(bottom, top, num = lat_steps)
longs = np.linspace(right, left, num = long_steps)

latlong_pairs = list(itertools.product(lats, longs))

grid = pd.DataFrame(latlong_pairs, columns = ['lat', 'lng'])

# crop by coast
with open('/Users/Ben/Dropbox/Insight/coast/coast-crop.pkl', 'rb') as f:
    coast_coords = pickle.load(f)

r = geometry.LinearRing(coast_coords)
coast_shp = geometry.Polygon(r)

keep = list()
for index, lat, lng in zip(range(len(grid)),grid.lat, grid.lng):
    print(str(index) + 'of' + str(len(grid)))
    point_obj = geometry.Point(lat, lng)
    keep.append(not coast_shp.contains(point_obj))

grid_crop = grid[keep]

grid_crop.to_csv('/Users/Ben/Dropbox/Insight/data-merge/merge-aws/coord-in/grid.csv', index = False)