import pandas as pd
import numpy as np
import pickle

# import model
rfrst = pickle.load(open('/Users/Ben/Dropbox/Insight/modeling/model-5-rfrst.pkl', 'rb'))

# import X_train cols to match pred columns to those used when fitting the model
X_cols = pickle.load(open('/Users/Ben/Dropbox/Insight/modeling/model-5-x-cols.pkl', 'rb'))

# import parks
parks = pd.read_csv('/Users/Ben/Dropbox/Insight/data-merge/merge-aws/out/parks-merge.csv')
parks = parks.drop('Unnamed: 0', axis = 1)

# pred for day zero, hour zero
parks['minute'] = 0
parks['hour'] = 0
parks['day'] = 0
# cyclic encoding of hour
parks['hour_sin'] = np.sin(2 * np.pi * parks['hour'] / 23)
parks['hour_cos'] = np.cos(2 * np.pi * parks['hour'] / 23)
# cyclic encoding of day
parks['day_sin'] = np.sin(2 * np.pi * parks['day'] / 6)
parks['day_cos'] = np.cos(2 * np.pi * parks['day'] / 6)
# make pred
parks_out = parks.copy(deep = True)[['parkname', 'lat', 'lng', 'day', 'hour']]
parks_out['db'] = rfrst.predict(parks[X_cols])

for day in range(1, 7):
    parks['day'] = day
    # cyclic encoding of day
    parks['day_sin'] = np.sin(2 * np.pi * parks['day'] / 6)
    parks['day_cos'] = np.cos(2 * np.pi * parks['day'] / 6)

    for hour in range(1, 24):
        print(str(day) + ' ' + str(hour))

        parks['hour'] = hour
        # cyclic encoding of hour
        parks['hour_sin'] = np.sin(2 * np.pi * parks['hour'] / 23)
        parks['hour_cos'] = np.cos(2 * np.pi * parks['hour'] / 23)

        temp_pred = parks.copy(deep = True)
        temp_pred['db'] = rfrst.predict(parks[X_cols])
        parks_out = parks_out.append(temp_pred[['parkname', 'lat', 'lng', 'day', 'hour', 'db']])

parks_out_agg = parks_out.copy(deep = True)

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
parks_out_agg['wkday'] = [wkday_conv(day) for day in parks_out_agg.day]

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

parks_out_agg = parks_out_agg.assign(hr_bkt = lambda x: [hour_bucket(hour) for hour in parks_out_agg.hour])

parks_out_agg = parks_out_agg.drop(['day', 'hour'], axis = 1)
parks_out_agg = parks_out_agg.groupby(['parkname', 'lat', 'lng', 'wkday', 'hr_bkt']).mean()
parks_out_agg = parks_out_agg.round({'db': 2})

parks_out_agg.to_csv('/Users/Ben/Dropbox/Insight/dash/parks_out.csv', index = True)