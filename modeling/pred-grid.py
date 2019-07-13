import pandas as pd
import numpy as np
import pickle

# import model
rfrst = pickle.load(open('/Users/Ben/Dropbox/Insight/modeling/model-5-rfrst.pkl', 'rb'))

# import X_train cols to match pred columns to those used when fitting the model
X_cols = pickle.load(open('/Users/Ben/Dropbox/Insight/modeling/model-5-x-cols.pkl', 'rb'))

# import pred grid
pred_grid = pd.read_csv('/Users/Ben/Dropbox/Insight/data-merge/pred_grid_crop.csv')
pred_grid = pred_grid.drop('Unnamed: 0', axis = 1)

# pred for day zero, hour zero
pred_grid['minute'] = 0
pred_grid['hour'] = 0
pred_grid['day'] = 0
# cyclic encoding of hour
pred_grid['hour_sin'] = np.sin(2 * np.pi * pred_grid['hour'] / 23)
pred_grid['hour_cos'] = np.cos(2 * np.pi * pred_grid['hour'] / 23)
# cyclic encoding of day
pred_grid['day_sin'] = np.sin(2 * np.pi * pred_grid['day'] / 6)
pred_grid['day_cos'] = np.cos(2 * np.pi * pred_grid['day'] / 6)
# make pred
pred_grid_out = pred_grid.copy(deep = True)[['lat', 'lng', 'day', 'hour']]
pred_grid_out['db'] = rfrst.predict(pred_grid[X_cols])

for day in range(1, 7):
    pred_grid['day'] = day
    # cyclic encoding of day
    pred_grid['day_sin'] = np.sin(2 * np.pi * pred_grid['day'] / 6)
    pred_grid['day_cos'] = np.cos(2 * np.pi * pred_grid['day'] / 6)

    for hour in range(1, 24):
        print(str(day) + ' ' + str(hour))

        pred_grid['hour'] = hour
        # cyclic encoding of hour
        pred_grid['hour_sin'] = np.sin(2 * np.pi * pred_grid['hour'] / 23)
        pred_grid['hour_cos'] = np.cos(2 * np.pi * pred_grid['hour'] / 23)

        temp_pred = pred_grid.copy(deep = True)
        temp_pred['db'] = rfrst.predict(pred_grid[X_cols])
        pred_grid_out = pred_grid_out.append(temp_pred[['lat', 'lng', 'day', 'hour', 'db']])

pred_grid_out_agg = pred_grid_out.copy(deep = True)

# extract day of the week
def wkday_conv(day):
    '''
    takes an integer from 0 to 6.
    if 0 - 4, then wkday = 1
    if 5 or 6, then wkday = 0
    '''
    if day < 5:
        wkday = 1
    else:
        wkday = 0
    return wkday
pred_grid_out_agg['wkday'] = [wkday_conv(day) for day in pred_grid_out_agg.day]

# bucket hours based on eda in noisenoise-spread-eda.ipynb
def hour_bucket(hour):
    hour_dict = {
    0: '12 am - 2 am',
    1: '12 am - 2 am',
    2: '12 am - 2 am',
    3: '3 am - 7 am',
    4: '3 am - 7 am',
    5: '3 am - 7 am',
    6: '3 am - 7 am',
    7: '3 am - 7 am',
    8: '8 am - 10 am',
    9: '8 am - 10 am',
    10: '8 am - 10 am',
    11: '11 am - 1 pm',
    12: '11 am - 1 pm',
    13: '11 am - 1 pm',
    14: '2 pm - 4 pm',
    15: '2 pm - 4 pm',
    16: '2 pm - 4 pm',
    17: '5 pm - 8 pm',
    18: '5 pm - 8 pm',
    19: '5 pm - 8 pm',
    20: '5 pm - 8 pm',
    21: '9 pm - 11 pm',
    22: '9 pm - 11 pm',
    23: '9 pm - 11 pm'
    }
    hour_out = hour_dict[hour]
    return hour_out
pred_grid_out_agg = pred_grid_out_agg.assign(hr_bkt = lambda x: [hour_bucket(hour) for hour in pred_grid_out_agg.hour])

pred_grid_out_agg = pred_grid_out_agg.drop(['day', 'hour'], axis = 1)
pred_grid_out_agg = pred_grid_out_agg.groupby(['lat', 'lng', 'wkday', 'hr_bkt']).mean()
pred_grid_out_agg = pred_grid_out_agg.round({'db': 2})

pred_grid_out_agg.to_csv('/Users/Ben/Dropbox/Insight/dash/pred_grid_out.csv', index = True)