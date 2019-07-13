'''
Pull noise observations from NoiseTube api.
First, I define get_noise which iterates queries for a given cityID
until it runs out of observations to download.
This returns a dataframe with all the observations for that city.

Then I loop through a set of cities.
'''

# NoiseTube scrape
# setup
import requests
import math
import pandas as pd

def get_noise(cityID):
	api_params = {
		'apikey' : '',
		'cityID' : cityID,
		# maxreturn is capped at 500
		'max' : 500
	}

	base_url = 'http://www.noisetube.net/api/search.json?key={apikey}&city={cityID}&max={max}'
	url = base_url.format(**api_params)

	# the first pull
	response = requests.get(url)
	noise_json = response.json()

	# name df to store
	noise = pd.DataFrame.from_records(noise_json)
	noise.made_at = pd.to_datetime(noise.made_at)

	base_url_until = 'http://www.noisetube.net/api/search.json?key={apikey}&city={cityID}&until={until}&max={max}'

	counter = 0
	while True:
		# update api params to pull from before the oldest in the last call
		oldest = min(noise.made_at).strftime('%Y-%m-%dT%H:%M:%S%z')
		api_params['until'] = oldest
		url = base_url_until.format(**api_params)

		# show counter
		print(str(counter) + ': ' + oldest)

		# the next pull
		response = requests.get(url)
		noise_json = response.json()

		# check if empty
		# ie you've hit the last record
		if len(noise_json) == 0:
			print('empty json\n' +
				'likely hit last record\n' +
				str(len(noise))
				)
			return(noise)
		# else append to dataframe
		else:
			# json to df
			new_pull = pd.DataFrame.from_records(noise_json)
			new_pull.made_at = pd.to_datetime(new_pull.made_at)

			# append to main df
			noise = noise.append(new_pull).reset_index(drop = True)

'''
Noise tube cities, their ID, and expected sample size:

Boston, 3, 109288
Cambridge, 926, 846
Summerville, 1463, 55441
Brookline, 2212, 1288
Chelsea, 2887, unknown
Winthrop, 2267, 50956
'''
cities = {
	'boston' : 3,
	'cambridge' : 926,
	'summerville' : 1463,
	'brookline' : 2212,
	'chelsea' : 2887,
	'winthrop' : 2267
}

for city, cityID in cities.items():
	print('starting pull for ' + city)
	noise = get_noise(cityID)
	noise.to_csv('/Users/Ben/Dropbox/Insight/noisetube-scrape/' + 
		city + '-noise-tube.csv')
