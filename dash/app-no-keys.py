# -*- coding: utf-8 -*-
# removed mapbox access token and google maps API key
import dash, requests, re
import dash_core_components as dcc
import dash_html_components as html
# import dash_table as dt
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import geopy.distance
from geopy import distance
import numpy as np

###############
import flask
server = flask.Flask(__name__)
###############


# data in ---------------------------------------
pred_grid_full = pd.read_csv('pred_grid_out.csv')
# set starting time of day
pred_grid = pred_grid_full[
    (pred_grid_full.hr_bkt == '11 am - 1 pm') &
    (pred_grid_full.wkday == 1)
    ]
park_locs = pd.read_csv('parks_clean.csv')
park_preds = pd.read_csv('parks_out.csv')


# functions ---------------------------------------
def translate_db(db):
    '''
    takes an single number as db level
    returns a string describing the noise level.
    '''
    db_refs = {
    30: 'a whisper',
    40: 'a library',
    50: 'light traffic', # refrigerator
    60: 'a restaurant', # air conditioner
    70: 'a vacuum cleaner', # shower / dishwasher
    80: 'a busy city street' # alarm clock/ garbage disposal
    }
    closest = min(db_refs, key = lambda x: abs(x - db))

    referant = db_refs[closest]

    difference = db - closest

    if difference < -2:
        comparison = 'quieter than the sound of'
    elif difference < 2:
        comparison = 'roughly the same volume as'
    elif difference < 6: 
        comparison = 'a little louder than the sound of'
    else:
        comparison = 'louder than'

    string_out = 'This is {} **{}**.'.format(comparison, referant)
    return string_out

def getcoord(address):
    '''
    Query Google Maps for an address
    '''
    addresst = address.replace('&', 'at').replace(' and ', ' at ').replace('#', '%23').replace(' ', '+')
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + addresst + '&key='
    response = requests.get(url)
    resp_json_payload = response.json()
    coord = resp_json_payload['results'][0]['geometry']['location']
    address_name = resp_json_payload['results'][0]['formatted_address']
    return coord, address_name

def calc_park_dist(user_coord):
    '''
    Calculate distance between user coords and all parks
    '''
    park_dists = []
    all_dists = [geopy.distance.distance(
                (user_coord['lat'], user_coord['lng']),
                (p_lat, p_lng)
                ).m for p_lat, p_lng in zip(park_locs.lat, park_locs.lng)]
    park_out = park_locs.assign(dists = all_dists)
    return park_out

def get_dir_url(user_coord, park_coord):
    '''
    returns a google maps link to directions from user to park
    '''
    base_url = 'https://www.google.com/maps/dir/?api=1&origin={}&destination={}&travelmode=walking'
    # %2C
    # format coords
    user_loc_str = str(user_coord[0]) + '%2C' + str(user_coord[1])
    park_loc_str = str(park_coord[0]) + '%2C' + str(park_coord[1])

    url_out = base_url.format(user_loc_str, park_loc_str)

    return url_out


# first plot ---------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


plot_data = [
    go.Scattermapbox(
        lat = list(pred_grid.lat),
        lon = list(pred_grid.lng),
        text = pred_grid.db.round(decimals = 0),
        mode='markers',
        hoverinfo = 'text',
        showlegend = False,
        marker = go.scattermapbox.Marker(
            colorscale='Viridis',
            size = 25,
            color = pred_grid.db,
            opacity = 0.2,
            showscale = True,
            cmax = 85,
            cmin = 25,
            colorbar = {
                'tickmode': 'array',
                'tickvals': [i for i in range(30, 90, 10)],
                'ticktext': [
                '30 - Whisper',
                '40 - Library',
                '50 - Light traffic', # refrigerator
                '60 - Restaurant', # air conditioner
                '70 - Vacuum cleaner', # shower / dishwasher
                '80 - Busy city street' # alarm clock/ garbage disposal
                ]
                }
        )
    )
]

plot_layout = go.Layout(
    width = 700,
    height = 700,
    autosize = True,
    margin=go.layout.Margin(
        l=10,
        r=10,
        b=10,
        t=10,
        pad=4
        ),
    hovermode='closest',
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat = 42.355,
            lon = -71.05495
        ),
        pitch = 0,
        zoom = 12.4
    ),
    annotations = [
        dict(
            x = 1.25,
            y = 0.98,
            align="left",
            valign="top",
            text = "Loudness (DB)",
            showarrow=False,
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="top"
        )
    ]
)

figure = dict(data = plot_data, layout = plot_layout)

# app layout ---------------------------------------

app.layout = html.Div([
    html.H1('NoiseMap'),

    # div containing controls div and map div
    html.Div([
        # controls div
        html.Div(
            style = {
            'padding': 5,
            'display': 'inline-block',
            'vertical-align': 'top',
            'width': 400
            },
            children = [
            html.Div(children='''
                This map shows the noise levels of different parts of Boston.
                Use the menus below to view noise estimates for weekdays and weekends, 
                at different times of day.
                ''',
                style={
                'textAlign': 'left',
                'padding': 10,
                'font-size': 18
                }),
            html.Div(
                dcc.Dropdown(
                    options = [
                    {'label': '12 am - 2 am', 'value': '12 am - 2 am'},
                    {'label': '3 am - 7 am', 'value': '3 am - 7 am'},
                    {'label': '8 am - 10 am', 'value': '8 am - 10 am'},
                    {'label': '11 am - 1 pm', 'value': '11 am - 1 pm'},
                    {'label': '2 pm - 4 pm', 'value': '2 pm - 4 pm'},
                    {'label': '5 pm - 8 pm', 'value': '5 pm - 8 pm'},
                    {'label': '9 pm - 11 pm', 'value': '9 pm - 11 pm'}
                    ],
                    value = '11 am - 1 pm',
                    id = 'hr_dropdown'
                    ),
                style = {
                'width': 150,
                'padding': 5,
                'display': 'inline-block'
                }
                ),
            html.Div(
                dcc.Dropdown(
                    options = [
                    {'label': 'Weekday', 'value': 1},
                    {'label': 'Weekend', 'value': 0}
                    ],
                    value = 1,
                    id = 'wkday_dropdown'
                    ),
                style = {
                'width': 150,
                'padding': 5,
                'display': 'inline-block'
                }
                ),

            html.Div(children='''
                You can also enter your address in the searchbox below to find the quietest park within 2 miles.
                ''',
                style={
                'textAlign': 'left',
                'padding': 10,
                'font-size': 18
                }),

            html.Div([
                dcc.Input(
                    placeholder='280 Summer St. Boston, MA',
                    value='',
                    type = 'text',
                    style={
                    'width': 250,
                    'vertical-align': 'bottom',
                    'padding': 5
                    },
                    id='address'),
                html.Div('',
                    style={
                    'padding': 5,
                    'display': 'inline-block'
                    }
                    ),
                html.Button(
                    id='submit',
                    children='Search',
                    style={
                    'width': 100,
                    'padding': 5,
                    'vertical-align': 'bottom',
                    'text-align': 'center',
                    'padding-top':'0%',
                    'display': 'inline-block'
                    }),
                html.Div('', style = {'padding': 10}),
                html.Div(
                    dcc.Markdown(
                        '',
                    id = 'quietest_text'
                    ),
                    # children = '',
                    style = {
                    'padding': 5,
                    'font-size': 18
                    }
                    )
                ]
                )
            ]
            ),
        # map div
        html.Div(
            dcc.Graph(
                id = 'noisemap',
                figure = figure,
                config={
                'displayModeBar': False
                }),
            style = {
            'padding': 5,
            'display': 'inline-block'
            }
            )
        ])
    ])

# app updates ---------------------------------------
# layout to keep plot in place
# called if user does not enter address
# or if user enters nonsense address
plot_layout_inplace = go.Layout(
    width = 700,
    height = 700,
    autosize = True,
    margin=go.layout.Margin(
    l=10,
    r=10,
    b=15,
    t=0,
    pad=4
    ),
    hovermode='closest',
    uirevision=True,
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat = 42.355,
            lon = -71.05495
        ),
        pitch = 0,
        zoom = 12.4
    ),
    annotations = [
        dict(
            x = 1.25,
            y = 0.98,
            align="left",
            valign="top",
            text = "Loudness (DB)",
            showarrow=False,
            xref="paper",
            yref="paper",
            xanchor="center",
            yanchor="top"
        )
    ]
)


@app.callback(
    [Output(component_id='noisemap', component_property='figure'),
    Output(component_id='quietest_text', component_property='children')],
    [Input('hr_dropdown', 'value'),
    Input('wkday_dropdown', 'value'),
    Input('submit', 'n_clicks')
    ],
    [State('address', 'value')]
)

def update_fig(hour_bkt, wkday, submit, address):
    pred_grid = pred_grid_full[
        (pred_grid_full.hr_bkt == hour_bkt) &
        (pred_grid_full.wkday == wkday)
    ]

    noise_data = go.Scattermapbox(
        lat = list(pred_grid.lat),
        lon = list(pred_grid.lng),
        text = pred_grid.db.round(decimals = 0),
        mode='markers',
        hoverinfo = 'text',
        showlegend = False,
        marker = go.scattermapbox.Marker(
            colorscale='Viridis',
            size = 25,
            color = pred_grid.db,
            opacity = 0.2,
            showscale = True,
            cmax = 85,
            cmin = 25,
            colorbar = {
                'tickmode': 'array',
                'tickvals': [i for i in range(30, 90, 10)],
                'ticktext': [
                '30 - Whisper',
                '40 - Library',
                '50 - Light traffic', # refrigerator
                '60 - Restaurant', # air conditioner
                '70 - Vacuum cleaner', # shower / dishwasher
                '80 - Busy city street' # alarm clock/ garbage disposal
                ]
                }
            )
    )

    if submit is not None:
        # geocode address to coords
        user_coord, address_name = getcoord(address)

        # check that address is in MA
        ma_check = re.search(r', MA \d+, USA', address_name)

        # if address is not in MA
        if ma_check is None:
            # leave plot in place
            plot_layout = plot_layout_inplace
            plot_data = [noise_data]

            # return error message
            park_text_out = '''
Sorry, address matching _{}_ found near Boston.
            '''.format(address)

        # if address is in MA
        else:
            # get park dists
            parkdists = calc_park_dist(user_coord)
            # filter for parks less than 2 miles
            # 3218.688 m == 2 miles 
            close_parks = parkdists[parkdists.dists < 3218]

            # get park preds
            close_park_preds = park_preds[park_preds.parkname.isin(close_parks.name)]
            # filter for current time
            close_park_preds = close_park_preds[
                (close_park_preds.hr_bkt == hour_bkt) &
                (close_park_preds.wkday == wkday)
            ]

            quietest_park = close_park_preds[
                close_park_preds.db == close_park_preds.db.min()
            ].to_dict(orient = 'records')[0]

            # redefine plot layout to center over user loc
            plot_layout = go.Layout(
                width = 700,
                height = 700,
                autosize = True,
                margin=go.layout.Margin(
                l=10,
                r=10,
                b=15,
                t=0,
                pad=4
                ),
                hovermode='closest',
                mapbox=go.layout.Mapbox(
                    accesstoken=mapbox_access_token,
                    bearing=0,
                    center=go.layout.mapbox.Center(
                        # this is the updated part
                        lat = user_coord['lat'],
                        lon = user_coord['lng']
                    ),
                    pitch = 0,
                    zoom = 12.4
                ),
                annotations = [
                    dict(
                        x = 1.25,
                        y = 0.98,
                        align="left",
                        valign="top",
                        text = "Loudness (DB)",
                        showarrow=False,
                        xref="paper",
                        yref="paper",
                        xanchor="center",
                        yanchor="top"
                    )
                ]
            )

            # add user loc as trace
            user_loc = go.Scattermapbox(
                    lat = [user_coord['lat']],
                    lon = [user_coord['lng']],
                    text = 'Your location: ' + address_name,
                    mode = 'markers',
                    hoverinfo = 'text',
                    showlegend = False,
                    marker = {
                        'size': 20,
                        'color': 'red'
                        }
            )

            # add quietest park as trace
            quietestpark_loc = go.Scattermapbox(
                    lat = [quietest_park['lat']],
                    lon = [quietest_park['lng']],
                    text = 'Quietest park within 2 miles: ' + quietest_park['parkname'],
                    mode = 'markers',
                    hoverinfo = 'text',
                    showlegend = False,
                    marker = {
                        'size': 20,
                        'color': 'orange'
                        }
            )

            plot_data = [noise_data, user_loc, quietestpark_loc]

            gmaps_url = get_dir_url(
                user_coord = (user_coord['lat'], user_coord['lng']),
                park_coord = (quietest_park['lat'], quietest_park['lng'])
                )

            park_text_out = '''
At the time you have selected,
the quietest park within 2 miles of {} is **{}**,
where the noise-level is estimated to be {} decibles. 

{} 

The red point on the map shows your location.
The orange point shows the location of the park.

[Click here for Google Maps directions.]({})
            '''.format(
                # this regular expression searches for ', MA'
                # and returns everything before
                # otherwise you get e.g. '280 Summer St, Boston, MA 02210, USA'
                re.findall(r'^(.*?), MA ', address_name)[0],
                quietest_park['parkname'],
                int(np.round(quietest_park['db'], decimals = 0)),
                translate_db(quietest_park['db']),
                gmaps_url
                    ),

    else:
        # define plot layout with uirevisions True
        # this preserves map position on update
        plot_layout = plot_layout_inplace
        plot_data = [noise_data]

        park_text_out = ''

    figure = dict(data = plot_data, layout = plot_layout)
    return [figure, park_text_out]

if __name__ == '__main__':
    app.run_server(debug = True, host = '0.0.0.0', port = 5000)