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
sys.path.append(os.path.join(os.path.dirname(__file__), '../MarketData'))

import numpy as np
import pandas as pd
from dash import Dash, html, dcc, dash_table, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
from plotly.figure_factory import create_candlestick

from TimeUtils import TimeUtils
from Utils import Utils
from const import const
from MarketData import MarketData
from DataServerStub import DataServerStub
from DataBuffer import DataBuffer, ResampleDataBuffer

INTERVAL_MSEC = 200
TICKERS = ['GBPJPY', 'GBPAUD']
TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', 'H1', 'H2', 'H4']
BARSIZE = ['100', '200', '300', '400', '500']

INTERVAL_MSEC_LIST = [50, 100, 500, 1000]


app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

#
server = DataServerStub('')

# ----

timer = dcc.Interval(id='timer', interval=INTERVAL_MSEC_LIST[2], disabled=True)

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

timeframe = html.Div([ html.P('Time Frame',
                       style={'margin-top': '8px', 'margin-bottom': '4px'},
                       className='font-weight-bold'),
                       timeframe_dropdown])

load = html.Div([ html.Button(id='load_button', 
                              n_clicks=0, 
                              children='Load Data',
                              style={'margin-top': '4px', 'margin-left': '8px', 'margin-right': '16px'},
                              className='btn btn-primary'),
                  html.Div(id='load_response', 
                           children='0',
                           style={'margin-top': '4px', 'margin-left': '8px', 'margin-bottom': '4px'})])

barsize_dropdown = dcc.Dropdown(id='barsize_dropdown', 
                                multi=False, 
                                value=BARSIZE[1],
                                options=[{'label': x, 'value': x} for x in BARSIZE],
                                style={'width': '120px'})

barsize = dbc.Col([html.P('Display Bar Size',
                          style={'margin-bottom': '4px'}),
                           barsize_dropdown])

replay = html.Div([html.P('Replay'),
                   dbc.Row([
                            html.P('Timer Interval(msec)', style={'margin-top': '4px', 'margin-bottom': '4px'}),
                            dcc.Dropdown(id='timer_interval', 
                                     multi=False, 
                                     value = INTERVAL_MSEC_LIST[2],
                                     options = INTERVAL_MSEC_LIST,
                                     style={'width': '120px'}),
                            html.P('bar', style={'margin-top': '8px', 'margin-bottom': '0px'}),
                            dcc.Input(id="bar_index",
                                      type="number",
                                      placeholder="index",
                                      value = 10005,
                                      min=10000,
                                      step=1,
                                      style={'width':'120px', 'margin-top':'4px', 'margin-left': '12px'})]),
                            html.Button(id='play_button', n_clicks=0, children='Play',
                                                        style={'margin-top': '8px', 'margin-left': '0px'},
                                                        className='btn btn-primary'),
                            html.Button(id='stop_button', n_clicks=0, children='Stop',
                                                        style={'margin-top': '8px', 'margin-left': '4px'},
                                                        className='btn btn-primary')
                    ])

sidebar = html.Div([   setting_bar,
                        html.Div([ticker,
                                 timeframe,
                                 load,
                                 html.Hr(),
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

@app.callback([ Output('load_button', 'n_clicks'),
                Output('load_response', 'children')],
              [ Input('load_response', 'children'),
                Input('load_button', 'n_clicks')],
                State('symbol_dropdown', 'value'),
                State('timeframe_dropdown', 'value'),
                State('bar_index', 'value')
                )
def updateServer(response, n_clicks,  symbol, timeframe, bar_index):
    global server
    global buffer
    print(n_clicks)
    if n_clicks == 0:
        return (0, response)    
    if timeframe[0].upper() != 'M':
        return (0, 'Bad ')
    minutes = int(timeframe[1:])
    candles, tohlc = MarketData.fxData(symbol, None, None, 1)
    print('Data size:', len(tohlc[0]))
    server = DataServerStub('')
    server.importData(tohlc)
    tohcv2 = server.init(bar_index, step_sec=10)
    buffer = ResampleDataBuffer(tohcv2, [], minutes)
    return (0, str(server.size()))

@app.callback([Output('play_button', 'n_clicks'),
                Output('stop_button', 'n_clicks'),
                Output('timer', 'interval'),
                Output('timer', 'disabled')],
              [Input('play_button', 'n_clicks'),
                Input('stop_button', 'n_clicks')],
              [State('timer_interval', 'value'),
                State('timer', 'disabled')])
def stop_interval(n_play, n_stop, timer_interval, disabled):
    if n_play is None or n_stop is None:
        return (0, 0, timer_interval, disabled)
    if n_play == 0 and n_stop == 0:
        return (0, 0, timer_interval, disabled)
    if n_play > 0:
        print('Play')
        return (0, 0, timer_interval, False)
    if n_stop > 0:
        print('Stop')
        return (0, 0, timer_interval, True)

@app.callback(  Output('chart_output', 'children'),
                 Input('timer', 'n_intervals'),
                 State('symbol_dropdown', 'value'),
                 State('timeframe_dropdown', 'value'),
                 State('barsize_dropdown', 'value'),
                 State('bar_index', 'value')
)
def updateChart(interval, symbol, timeframe, display_bar_size, bar_index):
    try:
        if server.size() == 0:
            print('No data')
            return no_update
    except:
        print('No data')
        return no_update
    #print(interval)
    num_bars = int(display_bar_size)
    bar_index = int(bar_index)
    print(symbol, timeframe, num_bars, bar_index)
    candles = server.nextData()
    buffer.update(candles)
    _, dic = buffer.temporary()
    sliced = Utils.sliceDicLast(dic, num_bars)
    chart = createChart(symbol, timeframe, sliced)
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

