# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 19:33:03 2023

@author: IKU-Trader
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 20:41:14 2023

@author: IKU-Trader
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../Utilities'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../PyMT5'))

import numpy as np
import pandas as pd
from dash import Dash, html, dcc, dash_table, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.figure_factory import create_candlestick

from PyMT5 import PyMT5
from TimeUtils import TimeUtils
from const import const

INTERVAL_MSEC = 200
TICKERS = ['DOWUSD', 'NASUSD', 'JPXJPY', 'XAUUSD', 'WTIUSD', 'USDJPY','EURJPY', 'GBPJPY', 'AUDJPY']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1']
BARSIZE = ['50', '100', '150', '200', '300', '400', '500']

INTERVAL_MSEC_LIST = [50, 100, 500, 1000]



server = PyMT5(TimeUtils.TIMEZONE_TOKYO)
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])


# ----

timer = dcc.Interval(id='timer', interval=INTERVAL_MSEC_LIST[2], disabled=False)

setting_bar = dbc.Row( [html.H5('Control',
                        style={'margin-top': '2px', 'margin-left': '24px'})
                        ],
                        style={"height": "3vh"},
                        className='bg-primary text-white')

ticker_dropdown = dcc.Dropdown(id='symbol_dropdown',
                               multi=False,
                               value=TICKERS[0],
                               options=[{'label': x, 'value': x} for x in TICKERS],
                               style={'width': '140px'})

ticker = html.Div([ html.P('Ticker Symbol',
                           style={'margin-top': '8px', 'margin-bottom': '4px'}, 
                           className='font-weight-bold'),
                           ticker_dropdown])
 
timeframe_dropdown = dcc.Dropdown(id='timeframe_dropdown', 
                                  multi=False, 
                                  value=TIMEFRAMES[1], 
                                  options=[{'label': x, 'value': x} for x in TIMEFRAMES],
                                  style={'width': '120px'})

timeframe =  html.Div([ html.P('Time Frame',
                        style={'margin-top': '16px', 'margin-bottom': '4px'},
                        className='font-weight-bold'),
                        timeframe_dropdown])

barsize_dropdown = dcc.Dropdown(id='barsize_dropdown', 
                                multi=False, 
                                value=BARSIZE[2],
                                options=[{'label': x, 'value': x} for x in BARSIZE],
                                style={'width': '120px'})

barsize = html.Div([html.P('Display Bar Size',
                    style={'margin-top': '16px', 'margin-bottom': '4px'},
                    className='font-weight-bold'),
                    barsize_dropdown])


replay = html.Div([html.P('Replay'),
                    dbc.Row([
                        html.Button('LoadData', id='load_button'),
                        dcc.Dropdown(id='timer_interval', 
                                     multi=False, 
                                     value = INTERVAL_MSEC_LIST[2],
                                     options = INTERVAL_MSEC_LIST,
                                     style={'width': '120px'}),
                        dcc.Input(id="index", type="number", placeholder="index",
                                            min=0, step=1,
                                            style={'margin-top': '8px'}),
                        html.Button('Play', id='play_button'),
                        html.Button('Stop', id='stop_button')])
                    ])

sidebar =  html.Div([   setting_bar,
                        html.Div([ticker,
                                 timeframe,
                                 barsize,
                                 html.Hr(),
                                 replay],
                        style={'height': '100vh', 'margin': '2px'})])
    
contents = html.Div([   dbc.Row([html.H5('MetaTrader5', style={'margin-top': '2px', 'margin-left': '20px'})],
                                style={"height": "3vh"}, className='bg-primary text-white'),
                        dbc.Row([html.Div(id='chart_output')]),
                        timer
                    ])

app.layout = dbc.Container([dbc.Row([dbc.Col(sidebar, width=2, className='bg-light'),
                                     dbc.Col(contents, width=9)],
                                     style={"height": "80vh"})],
                            fluid=True)



@app.callback(  Output('chart_output', 'children'),
                 Input('timer', 'n_intervals'),
                 State('symbol_dropdown', 'value'),
                 State('timeframe_dropdown', 'value'),
                 State('barsize_dropdown', 'value')
)
def updateChart(interval, symbol, timeframe, num_bars):
    #print(interval)
    num_bars = int(num_bars)
    print(symbol, timeframe, num_bars)
    dic = server.download(symbol, timeframe, num_bars)
    chart = createChart(symbol, timeframe, dic)
    return chart
  
def createChart(symbol, timeframe, dic):
    fig = create_candlestick(dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE])
    time = dic[const.TIME]
    #print(symbol, timeframe, dic)
    xtick0 = (5 - time[0].weekday()) % 5
    tfrom = time[0].strftime('%Y-%m-%d %H:%M')
    tto = time[-1].strftime('%Y-%m-%d %H:%M')
    if timeframe == 'D1' or timeframe == 'H1':
        form = '%m-%d'
    else:
        form = '%d/%H:%M'
    fig['layout'].update({
                            'title': symbol + '　' +  tfrom + '  ...  ' + tto,
                            'width': 1100,
                            'height': 400,
                            'xaxis':{
                                        'title': '',
                                        'showgrid': True,
                                        'ticktext': [x.strftime(form) for x in time][xtick0::5],
                                        'tickvals': np.arange(xtick0, len(time), 5)
                                    },
                            'yaxis':{
                                        'title': '',
                                        'tickformat': 'digit'
                                    },
                            'margin': {'l':2, 'r':10, 'b' :40, 't':70, 'pad': 2},
                            'paper_bgcolor': '#f7f7ff' # RGB
                        })
    
    #print(fig)
    return dcc.Graph(id='stock-graph', figure=fig)



def createTable(df):
    table = dash_table.DataTable(style_cell={'textAlign':'center', 
                                             'maxWidth':'80px', 
                                             'minWidth':'40px', 
                                             'whiteSpace':'normal' ,
                                             'height': 'auto',
                                             'font_family': 'sans-serif',
                                             'font_size': '12px'},
                                 style_data={'color':'black','backgroundColor':'white'},
                                 style_data_conditional=[{'if':{'row_index':'odd'},'backgroundColor':'rgb(220,220,220)'}],
                                 style_header={'backgroundColor':'rgb(72,72,128)','color':'white','fontWeight':'bold'},
                                 fixed_rows={'headers':True},   
                                 style_table={'minWidth':'90%'},
                                 columns=[{'name':col, 'id':col} for col in df.columns],
                                 data=df.to_dict('records'),
                                 page_size=10,
                                 export_format='csv')
    return table

if __name__ == '__main__':
    app.run_server(debug=True, port=3000)

