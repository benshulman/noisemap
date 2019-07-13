from x_prep_funcs import xy_to_latlng, box_filter # custom functions in same dir
import shapefile
import pandas as pd
from shapely import geometry
import pickle

bus_routes = shapefile.Reader('/Users/Ben/Dropbox/Insight/x-data-mass/point_line_x/mbtabus/MBTABUSROUTES_ARC')

bus_xy = [list(route.points) for route in bus_routes.iterShapes()]

bus_latlng = list()
for xy_route in bus_xy:
    latlng_route = [xy_to_latlng(point) for point in xy_route]
    bus_latlng.append(latlng_route)

with open('/Users/Ben/Dropbox/Insight/x-data-mass/bus_line_lists.pkl', 'wb') as f:
    pickle.dump(bus_latlng, f)