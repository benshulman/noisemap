from pyproj import Proj, transform
import pandas as pd

def xy_to_latlng(
    in_coord, # array-like input coords in xy
    inProj = Proj(init = 'epsg:26986'), # Mass x y coord system
    outProj = Proj(init = 'epsg:4326') # lat lng coord system 
    ):
    '''
    Converts points from the xy coordinate system used by MassGIS
    to latitude and and longitude.
    Takes as input an array-like input with the xy coordinates
    for a point.
    Returns a tuple with lat lng coorinates.
    '''
    lng, lat = transform(inProj, outProj, in_coord[0], in_coord[1])
    return (lat, lng)

def box_filter(
    in_df, # input df with columns for lat an lng
    lat = 'lat', # lat lng col names
    lng = 'lng',
    bounds = [[42.22, -71.21], [42.429, -70.94]]):
    '''
    takes in a dataframe and filter rows to keep only points
    within a specified bounding box.
    '''
    out_df = in_df[(
        # bottom
        (in_df[lat] > bounds[0][0]) &
        # top
        (in_df[lat] < bounds[1][0]) &
        # left
        (in_df[lng] > bounds[0][1]) &
        # right
        (in_df[lng] < bounds[1][1])
        )].reset_index(drop = True)
    return out_df