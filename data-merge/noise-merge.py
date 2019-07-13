import pandas as pd
import numpy as np

ntube = pd.read_csv('/Users/Ben/Dropbox/Insight/noisetube-scrape/noise-tube-boxed.csv')
ntube = ntube.drop('city', axis = 1)
ntube = ntube.rename(index = str, columns = {'loudness': 'db'})
# noise tube records for about 3 seconds per measurement
ntube = ntube.assign(dur = lambda x: x.n_agg * 3)
nscore = pd.read_csv('/Users/Ben/Dropbox/Insight/noisescore/noise-score-boxed.csv')
nscore = nscore.rename(index = str, columns = {'decibelMean': 'db'})
# noise score records for about 10s per measurement
nscore['dur'] = 10

noise = pd.concat([ntube, nscore]).reset_index(drop = True)
noise = noise.drop('Unnamed: 0', axis = 1)

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
noise['wkday'] = [wkday_conv(day) for day in noise.day]

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
noise = noise.assign(hr_bkt = lambda x: [hour_bucket(hour) for hour in noise.hour])

# cyclic encoding of hour
noise['hour_sin'] = np.sin(2 * np.pi * noise['hour'] / 23)
noise['hour_cos'] = np.cos(2 * np.pi * noise['hour'] / 23)
# cyclic encoding of day
noise['day_sin'] = np.sin(2 * np.pi * noise['day'] / 6)
noise['day_cos'] = np.cos(2 * np.pi * noise['day'] / 6)

noise.to_csv('/Users/Ben/Dropbox/Insight/data-merge/merge-aws/coord-in/noise-merged.csv')