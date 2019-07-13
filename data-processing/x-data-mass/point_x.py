from x_prep_funcs import xy_to_latlng, box_filter # custom functions in same dir
import shapefile
import pandas as pd

files = ({
    'hosp' : '/Users/Ben/Dropbox/Insight/x-data-mass/point_x/acute_care_hospitals/HOSPITALS_PT',
    'fire' : '/Users/Ben/Dropbox/Insight/x-data-mass/point_x/firestations_pt/FIRESTATIONS_PT_MEMA.dbf',
    'pol' : '/Users/Ben/Dropbox/Insight/x-data-mass/point_x/policestations/POLICESTATIONS_PT_MEMA.cpg',
    'fw_exit' : '/Users/Ben/Dropbox/Insight/x-data-mass/point_x/exits/EXITS_PT.shp',
    'train_st' : '/Users/Ben/Dropbox/Insight/x-data-mass/point_line_x/trains/TRAINS_NODE',
    'bus_st' : '/Users/Ben/Dropbox/Insight/x-data-mass/point_line_x/mbtabus/MBTABUSSTOPS_PT',
    'sbwy_st' : '/Users/Ben/Dropbox/Insight/x-data-mass/point_line_x/mbta_rapid_transit/MBTA_NODE'
    })

# read in shape files
shp_list = [shapefile.Reader(file) for file in files.values()]

# extract fire xy coords
xy_lists = list()
for shp_file in shp_list:
    xy_lists.append(
        [tuple(shape.points[0]) for shape in shp_file.shapes()]
        )

# convert to latlng
latlng_lists = list()
for xy_list in xy_lists:
    latlng_lists.append(
        [xy_to_latlng(xy) for xy in xy_list]
    )

# convert to df
latlng_dfs = [pd.DataFrame(
    latlng_list,
    columns = ['lat', 'lng']) for latlng_list in latlng_lists]

for filename, df in zip(files.keys(), latlng_dfs):
    print(filename + ' N obs unboxed: ' + str(len(df)))

# keep only those in a bounding box
# bounds = [[42.22, -71.21], [42.429, -70.94]]
latlng_dfs = [box_filter(latlng_df) for latlng_df in latlng_dfs]

# save out
for filename, df in zip(files.keys(), latlng_dfs):
    print(filename + ' N obs boxed: ' + str(len(df)))
    df.to_csv('/Users/Ben/Dropbox/Insight/x-data-mass/point_latlng_clean/' + filename + '_latlng.csv')
    print('saved' + filename)