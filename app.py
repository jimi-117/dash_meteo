import os
import requests
import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import io
import gzip

load_dotenv()

# geonames username
geonames_user = os.getenv('geonames_api_username')

# Function to fetch the list of towns from the GeoNames API
def fetch_town_list(query):
    username = geonames_user
    geonames_api_url = f'http://api.geonames.org/searchJSON?name_startsWith={query}&country=FR&maxRows=10&username={username}'
    response = requests.get(geonames_api_url)
    if response.status_code == 200:
        towns = response.json()['geonames']
        return [{'label': town['name'], 'value': town['name']} for town in towns]
    else:
        return []

# Function to fetch the first two digits of the postal code, and latitude and longitude
def fetch_postal_code_and_coords(town_name):
    username = geonames_user
    # Note: Setting maxRows to 1 to get only the first result
    geonames_api_url = f'http://api.geonames.org/postalCodeSearchJSON?placename={town_name}&country=FR&maxRows=1&username={username}'
    response = requests.get(geonames_api_url)
    if response.status_code == 200:
        postal_codes = response.json()['postalCodes']
        if postal_codes:
            postal_code_info = postal_codes[0]
            # Extracting the first two digits of the postal code
            postal_code_prefix = postal_code_info['postalCode'][:2]
            # Getting latitude and longitude
            latitude = postal_code_info['lat']
            longitude = postal_code_info['lng']
            return postal_code_prefix, latitude, longitude
    return None, None, None

# The radius of the Earth in kilometers
EARTH_RADIUS = 6371
# Define the Haversine formula to calculate distance between two latitude-longitude points
def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Difference in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    km = EARTH_RADIUS * c
    return km

# Function to find the nearest weather station to a given latitude and longitude
def find_nearest_station(df, lat, lon):
    # Apply the Haversine function to calculate distances to each station in the DataFrame
    distances = df.apply(lambda row: haversine(lat, lon, row['LAT'], row['LON']), axis=1)
    # Find the index of the smallest distance
    nearest_station = df.loc[distances.idxmin(), 'NUM_POSTE']
    return nearest_station



# Dropdown list for birthyear
years = [{'label': str(year), 'value': year} for year in range(1900, 2022)]

# Initialize Dash
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    dcc.Dropdown(
        id='town-name-input',
        placeholder="Enter your town...",
        search_value='',  # suggestions
        multi=False  # Mono-choice
    ),
    dcc.Dropdown(
        id='birth-year-dropdown',
        options=years,
        placeholder="Select your birthyear..."
    ),
    # You might want to add here other elements to display the fetched data
])

@app.callback(
    Output('town-name-input', 'options'),
    [Input('town-name-input', 'search_value')]
)
def update_town_list(search_value):
    if not search_value:
        raise PreventUpdate
    return fetch_town_list(search_value)

# Presumably you'll have another callback here to update the graph
# ...

if __name__ == '__main__':
    app.run_server(debug=True)

