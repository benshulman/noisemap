from x_prep_funcs import xy_to_latlng, box_filter # custom functions in same dir
import shapefile
import pandas as pd
from shapely import geometry
import pickle

roads = shapefile.Reader('/Users/Ben/Dropbox/Insight/x-data-mass/MassDOT_Roads_SHP/EOTROADS_ARC')

# define bounding box
bounds = [[42.22, -71.21], [42.429, -70.94]]
bbox = geometry.box(
    minx = bounds[0][0],
    miny = bounds[0][1],
    maxx = bounds[1][0],
    maxy = bounds[1][1]
)

'''
1 - Limited Access Highway
2 - Multi-lane Highway, not limited access
3 - Other numbered route
4 - Major road - arterials and collectors
5 - Minor street or road (with Road Inventory information, not class 1-4)
6 - Minor street or road (with minimal Road Inventory information and no street name)
'''

# a list of empty dictionaries
rd_boxed = {k: [] for k in range(5)}

# ref dict
rd_ref_dict = {
    0: 'lm_acc_hwy',
    1: 'mul_ln_hwy',
    2: 'num_rt_hwy',
    3: 'maj_rd',
    4: 'min_rd'
}

# the reference for which roads go in which list
rd_boxed_ref = {
    1: 0,
    2: 1,
    3: 2,
    4: 3,
    5: 4, # assigning minor streets to same list
    6: 4
}

for index, road, record in zip(
    range(len(roads)),
    roads.iterShapes(),
    roads.iterRecords()):
    road_class = record.as_dict()['CLASS']
    # points to lat lng
    road_latlng = [xy_to_latlng(point) for point in road.points]
    # make geometry object
    road_line = geometry.LineString(road_latlng)
    # intersect with bounding box
    road_line_int = road_line.intersection(bbox)
    print(index)
    # if non zero, add to list
    if road_line_int.length > 0:
        if isinstance(road_line_int,
            geometry.multilinestring.MultiLineString):
                for line in road_line_int.geoms:
                    # look up which list to store it in,
                    # given the road class
                    rd_boxed[rd_boxed_ref[road_class]].append(list(line.coords))
        else:
            # look up which list to store it in,
            # given the road class
            rd_boxed[rd_boxed_ref[road_class]].append(list(road_line_int.coords))

####
# with open('/Users/Ben/Dropbox/Insight/x-data-mass/road_line_lists.pkl', 'rb') as f:
#     rd_boxed = pickle.load(f)
####

for index, road_list in zip(range(len(rd_boxed)), rd_boxed):
    base_path = '/Users/Ben/Dropbox/Insight/x-data-mass/'
    file_name = rd_ref_dict[index]
    with open(base_path + file_name + '_line_lists.pkl', 'wb') as f:
        pickle.dump(rd_boxed[index], f)