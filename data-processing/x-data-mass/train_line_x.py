from x_prep_funcs import xy_to_latlng, box_filter # custom functions in same dir
import shapefile
import pandas as pd
from shapely import geometry
import pickle

trains = shapefile.Reader('/Users/Ben/Dropbox/Insight/x-data-mass/point_line_x/trains/TRAINS_ARC')

# define bounding box
bounds = [[42.22, -71.21], [42.429, -70.94]]
bbox = geometry.box(
    minx = bounds[0][0],
    miny = bounds[0][1],
    maxx = bounds[1][0],
    maxy = bounds[1][1]
)

'''
I'll keep only type 1: active use.

https://docs.digital.mass.gov/dataset/massgis-data-trains#tab1
1   Active rail service
2   Multiple use i.e. active and recreation
3   Abandoned rail service
4   Abandoned rail service ROW in public ownership
5   Unknown status
6   Out of service
7   Right-of-way (ROW) used for hiking and biking
8   Other ROW (once used for trolleys, or never built or used for rail)
9   MBTA Rapid Transit
'''

train_boxed = list()
for index, train, record in zip(
    range(len(trains)),
    trains.iterShapes(),
    trains.iterRecords()):
    train_type = record.as_dict()['TYPE']
    if train_type == 1:
        # points to lat lng
        train_latlng = [xy_to_latlng(point) for point in train.points]
        # make geometry object
        train_line = geometry.LineString(train_latlng)
        # intersect with bounding box
        train_line_int = train_line.intersection(bbox)
        print(index)
        # if non zero, add to list
        if train_line_int.length > 0:
            # if it's multiline, append each line separately
            if isinstance(train_line_int, geometry.multilinestring.MultiLineString):
                for line in train_line_int.geoms:
                    # look up which list to store it in,
                    # given the road class
                    train_boxed.append(list(line.coords))
            else:
                # look up which list to store it in,
                # given the road class
                train_boxed.append(list(train_line_int.coords))

with open('/Users/Ben/Dropbox/Insight/x-data-mass/train_line_lists.pkl', 'wb') as f:
    pickle.dump(train_boxed, f)