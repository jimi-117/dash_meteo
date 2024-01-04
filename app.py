import requests
import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# Fonction to get name list of towns from GeoNames API
def fetch_town_list(query):
    # GeoNames user name
    username = 'shom'
    # GeoNames API URL
    geonames_api_url = f'http://api.geonames.org/searchJSON?name_startsWith={query}&country=FR&maxRows=10&username={username}'
    response = requests.get(geonames_api_url)
    if response.status_code == 200:
        towns = response.json()['geonames']
        return [{'label': town['name'], 'value': town['name']} for town in towns]
    else:
        return []
    
# Pulldown list for birthyear
years = [{'label': str(year), 'value': year} for year in range(1900, 2022)]

# Init dash
app = dash.Dash(__name__)

# app layouts
app.layout = html.Div([
    dcc.Dropdown(
        id='town-name-input',
        placeholder="Enter your town...",
        search_value='',  # suggestions
        multi=False  # Mono-choice
    )
])


@app.callback(
    Output('temperature-graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('input-region', 'value'),
     dash.dependencies.State('input-birthday', 'value')]
)
def update_graph(n_clicks, input_region, input_birthday):
    if n_clicks > 0 and input_region and input_birthday:
        # 地点を特定し、気温データを取得するロジック
        # ...

        # データからグラフを生成する
        # ...

        # グラフオブジェクトを返す
        return {
            'data': [{
                'x': x_data,  # date
                'y': y_data,  # temparture
                'type': 'scatter',  # graph type
                'mode': 'lines+markers',  # graph mode
                'name': 'Avg temp'  # legend
            }],
            'layout': {
                'title': 'Movement average temparture'
            }
        }
    # Blank graph if no data
    return {'data': []}

# run app
if __name__ == '__main__':
    app.run_server(debug=True)
