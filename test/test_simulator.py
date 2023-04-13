# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 07:54:43 2023

@author: IKU-Trader
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../Utilities'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../MarketData'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../CandlestickChart'))

import numpy as np
import pandas as pd


from time_utils import TimeUtils
from utils import Utils
from const import const
from market_data import MarketData
from data_server_stub import DataServerStub
from data_buffer import DataBuffer, ResampleDataBuffer
from candle_chart import CandleChart, makeFig

timeframe = 'M5'
symbol = 'GBPJPY'
bar_index = 10005
num_bars = 50
bar_index = 10005

def load():
   global server
   global buffer
    
   if timeframe[0].upper() != 'M':
       return (0, 'Bad ')
   minutes = int(timeframe[1:])
   candles, tohlc = MarketData.fxData(symbol, [2017], [1], 1)
   print('Data size:', len(tohlc[0]))
   server = DataServerStub('')
   server.importData(tohlc)
   tohcv2 = server.init(bar_index, step_sec=10)
   buffer = ResampleDataBuffer(tohcv2, [], minutes)
   return (0, str(server.size()))
    
    
def update():
    print(symbol, timeframe, num_bars, bar_index)
    candles = server.nextData()
    buffer.update(candles)
    _, dic = buffer.temporary()
    sliced = Utils.sliceDicLast(dic, num_bars)
    fig, ax = makeFig(1, 1, (12, 6)) 
    chart = CandleChart(fig, ax, '', '', write_time_range=True)
    chart.drawCandle(sliced[const.TIME], sliced[const.OPEN], sliced[const.HIGH], sliced[const.LOW], sliced[const.CLOSE], xlabel=True)
    

if __name__ == '__main__':
    load()
    for i in range(10):
        update()