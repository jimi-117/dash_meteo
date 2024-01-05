import os
import requests
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import numpy as np
import pandas as pd
import gzip
import io
from dotenv import load_dotenv

import plotly.express as px

load_dotenv()

# global configs
GEONAMES_USER = os.getenv('geonames_api_username')
EARTH_RADIUS = 6371  # radius (km)

# pipeline
def get_geonames_api_url(api_name, town_name='', query='', country='FR', max_rows=10):
    return f'http://api.geonames.org/{api_name}JSON?name_startsWith={query}&placename={town_name}&country={country}&maxRows={max_rows}&username={GEONAMES_USER}'

def make_request(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def fetch_town_list(query):
    url = get_geonames_api_url('search', query=query)
    json_response = make_request(url)
    if json_response:
        towns = json_response['geonames']
        return [{'label': town['name'], 'value': town['name']} for town in towns]
    return []

def fetch_postal_code_and_coords(town_name):
    url = get_geonames_api_url('postalCodeSearch', town_name=town_name, max_rows=1)
    json_response = make_request(url)
    if json_response and json_response['postalCodes']:
        postal_code_info = json_response['postalCodes'][0]
        postal_code_prefix = postal_code_info['postalCode'][:2]
        latitude, longitude = postal_code_info['lat'], postal_code_info['lng']
        return postal_code_prefix, latitude, longitude
    return None, None, None

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return EARTH_RADIUS * c

# to make a func. to take 2nd nearest station to fill the month which contains null TX value.

def find_nearest_station(df, lat, lon):
    distances = df.apply(lambda row: haversine(lat, lon, row['LAT'], row['LON']), axis=1)
    return df.loc[distances.idxmin(), 'NUM_POSTE']

def download_temperatures(postal_code_prefix):
    url = f"https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/MENS/MENSQ_{postal_code_prefix}_previous-1950-2021.csv.gz"
    response = make_request(url)
    if response:
        gzip_file = gzip.GzipFile(fileobj=io.BytesIO(response.content))
        df = pd.read_csv(gzip_file, delimiter=';')
        return df[['NUM_POSTE', 'AAAAMM', 'LAT', 'LON', 'TX']]
    return None

fig = px.line()


# init Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Degemer Mat !'),
    
    dcc.Dropdown(
        id='town-name-input',
        placeholder="Enter your town...",
        search_value='',
        multi=False
    ),
    dcc.Dropdown(
        id='birth-year-dropdown',
        options=[{'label': str(year), 'value': year} for year in range(1900, 2022)],
        placeholder="Select your birthyear..."
    ),
    dcc.Graph(id='temperature-graph')
])

@app.callback(
    Output('town-name-input', 'options'),
    [Input('town-name-input', 'search_value')]
)
def update_town_list(search_value):
    if not search_value:
        raise PreventUpdate
    return fetch_town_list(search_value)

# may others callbacks...
# ...

if __name__ == '__main__':
    app.run_server(debug=True)
