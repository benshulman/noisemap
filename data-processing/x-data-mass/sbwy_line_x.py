from x_prep_funcs import xy_to_latlng, box_filter # custom functions in same dir
import shapefile
import pandas as pd
from shapely import geometry
import pickle

sbwy_routes = shapefile.Reader('/Users/Ben/Dropbox/Insight/x-data-mass/point_line_x/mbta_rapid_transit/MBTA_ARC')

sbwy_xy = [list(route.points) for route in sbwy_routes.iterShapes()]

sbwy_latlng = list()
for xy_route in sbwy_xy:
    latlng_route = [xy_to_latlng(point) for point in xy_route]
    sbwy_latlng.append(latlng_route)

with open('/Users/Ben/Dropbox/Insight/x-data-mass/sbwy_line_lists.pkl', 'wb') as f:
    pickle.dump(sbwy_latlng, f)