
import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime

# download meteo data
def download_weather_data(dataset_url):
    # 
    pass

# Init dash
app = dash.Dash(__name__)

# app layouts
app.layout = html.Div([
    html.Div([
        html.Label('Enter town:'),
        dcc.Input(id='input-region', value='', type='text'),

        html.Label('Enter your birthday:'),
        dcc.DatePickerSingle(id='input-birthday'),

        html.Button(id='submit-button', n_clicks=0, children='show')
    ]),

    dcc.Graph(id='temperature-graph')
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
