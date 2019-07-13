'''
compute distances between observations
and features of interest
'''
import geopy.distance
from geopy import distance
import numpy as np
import pandas as pd
from shapely import wkt, geometry
from shapely.ops import nearest_points
import pickle, time, tqdm
from concurrent import futures

# log elapsed time
start = time.time()

# target in
noise = pd.read_csv('/Users/Ben/Dropbox/Insight/data-merge/merge-aws/coord-in/noise-merged.csv')
noise = noise.drop('Unnamed: 0', axis = 1)

# point features in
point_features = {
    'bus_st': pd.read_csv('./x-in/point_latlng_clean/bus_st_latlng.csv'),
    'fire': pd.read_csv('./x-in/point_latlng_clean/fire_latlng.csv'),
    'fw_exit': pd.read_csv('./x-in/point_latlng_clean/fw_exit_latlng.csv'),
    'hosp': pd.read_csv('./x-in/point_latlng_clean/hosp_latlng.csv'),
    'pol': pd.read_csv('./x-in/point_latlng_clean/pol_latlng.csv'),
    'sbwy_st': pd.read_csv('./x-in/point_latlng_clean/sbwy_st_latlng.csv'),
    'train_st': pd.read_csv('./x-in/point_latlng_clean/train_st_latlng.csv'),
    'rests_bars':  pd.read_csv('./x-in/point_latlng_clean/bars-rests-combined.csv')
}

# line features in
line_features = {
    'bus_line': pickle.load(open('./x-in/line_pkl/bus_line_lists.pkl', 'rb')),
    'lm_acc_hwy': pickle.load(open('./x-in/line_pkl/lm_acc_hwy_line_lists.pkl', 'rb')),
    'maj_rd': pickle.load(open('./x-in/line_pkl/maj_rd_line_lists.pkl', 'rb')),
    'min_rd': pickle.load(open('./x-in/line_pkl/min_rd_line_lists.pkl', 'rb')),
    'mul_ln_hwy': pickle.load(open('./x-in/line_pkl/mul_ln_hwy_line_lists.pkl', 'rb')),
    'num_rt_hwy': pickle.load(open('./x-in/line_pkl/num_rt_hwy_line_lists.pkl', 'rb')),
    'sbwy_line': pickle.load(open('./x-in/line_pkl/sbwy_line_lists.pkl', 'rb')),
    'train_line': pickle.load(open('./x-in/line_pkl/train_line_lists.pkl', 'rb'))
}

def point_ft_dist(lat, lng, point_features = point_features):
    '''
    Takes as input:
        lat lng: an obs with lat lng coords for which we want distances calculated,
        point_features: a list of point features, each of which is a list of points.
    For each each point feature, calculate the distances between the obs 
    and each of the feature's points. Find the minimum distance and the number of feature points
    within a set of distance ranges.
    The distances ranges are hard-coded below as the dist_ranges list.
    Returns a dictionary with the obs and distances.
    '''
    obs = (lat, lng)
    dict_out = dict()
    dict_out['lat'] = lat
    dict_out['lng'] = lng
    dist_ranges = [
    25,
    50,
    100,
    150,
    200,
    250,
    300,
    500,
    1000
    ]
    for feature_name, feature_df, in point_features.items():
        # print(feature_name)
        # calculate distance from point to each feature point
        all_dists = [geopy.distance.distance(
            obs,
            (f_lat, f_lng)
            ).m for f_lat, f_lng in zip(feature_df.lat, feature_df.lng)]
        # record minimum to dictionary
        dict_out[feature_name + '_min_dist']  = min(all_dists)
        # record counts to temporary lists
        # exception for rests and bars because we aggregated
        # overlapping restaurants and bars
        # we need to sum the n_agg column, not simply count the rows
        if feature_name == 'rests_bars':
            for dist_range in dist_ranges:
                dict_out[feature_name + '_count_' + str(dist_range)] = sum(n_agg for dist, n_agg in zip(all_dists, feature_df.n_agg) if dist < dist_range)
        else:
            for dist_range in dist_ranges:
                dict_out[feature_name + '_count_' + str(dist_range)] = sum(1 for dist in all_dists if dist < dist_range)
    return dict_out

def airport_dist(lat, lng):
    '''
    Takes as input lat lng coords of the obs for which we want distances calculated,
    Returns a dictionary with the lat lng and distance.
    '''
    dict_out = dict()
    dict_out['lat'] = lat
    dict_out['lng'] = lng

    # airport coords from wikipedia
    airport = (42.363056, -71.006389)

    # calculate distance
    min_dist = geopy.distance.distance(
            (lat, lng),
            airport
            ).m
    # add to dictionary
    dict_out['airport_min_dist'] = min_dist
    return dict_out

def line_ft_dist(lat, lng, line_features = line_features):
    '''
    Takes as input:
        lat lng: an obs with lat lng coords for which we want distances calculated,
        line_features: a list of line features, each of which is a list of points.
    For each line feature, calculate the distances between the obs and each of the lines.
    Add entry to dictionary with the minimum distances.
    Returns a dictionary with the obs lat and lng, and the distances.
    '''
    dict_out = dict()
    dict_out['lat'] = lat
    dict_out['lng'] = lng

    for feature_name, feature_lines, in line_features.items():
        # print(feature_name)
        # convert list of lists of points to list of polylines
        line_list = [geometry.LineString(line_points) for line_points in feature_lines]
        npoint = [lat, lng]
        # convert coordinates to point object
        npoint_obj = geometry.Point(npoint)
        # empty list to store all distances between an obs row point and each feature line
        all_dists = list()
        for line_obj in line_list:
            # find nearest point on line to obs point
            nrst_pt = nearest_points(line_obj, npoint_obj)
            # find distance between obs point and nearest point on line
            nrst_dist = distance.distance(nrst_pt[0].coords, npoint).m
            all_dists.append(nrst_dist)
        # add the min distance between the obs row point and the feature lines
        dict_out[feature_name + '_min_dist'] = min(all_dists)
    return dict_out

# calculate distance
def dist_calc(lat, lng):
    '''
    Takes as input an obs with coors lat lng.
    Returns a dictionary with the obs lat lng and the distances.
    The airport coords are hard coded in the airport_dist function.
    Merges the dictionaries returned by each of the nested functions.
    '''
    latlng_dict = {'lat': lat, 'lng': lng}
    point_dict = point_ft_dist(lat, lng)
    airport_dict = airport_dist(lat, lng)
    line_dict = line_ft_dist(lat, lng)
    dict_out = {
        **latlng_dict,
        **point_dict,
        **airport_dict,
        **line_dict
    }
    return dict_out

def main():
    with futures.ProcessPoolExecutor() as executor:
        results = list(
            tqdm.tqdm(
                executor.map(dist_calc, noise.lat, noise.lng),
                total = len(noise)
                )
            )
    test_df = pd.DataFrame(results)
    test_df.to_csv('./out/noise-merge.csv')
    end = time.time()
    print("Took %f seconds..." %(end - start))
    # # took 22.201501 seconds

if __name__ == '__main__':
    main()
