# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 15:31:39 2023

@author: IKU-Trader
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../Utilities'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../TechnicalAnalysis'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../CandlestickChart'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../MarketData'))

import pandas as pd
from Utils import Utils
from TimeUtils import TimeUtils
from DataBuffer import ResampleDataBuffer
from MarketData import MarketData
from CandleChart import CandleChart, BandPlot, makeFig, Colors
from STA import TechnicalAnalysis as ta
from TAKit import TAKit
from const import const


def displayChart(data: ResampleDataBuffer):
    t0 = TimeUtils.pyTime(2022, 9, 8,  7, 0, 0, TimeUtils.TIMEZONE_TOKYO)
    t1 = TimeUtils.pyTime(2022, 9, 8, 18, 0, 0, TimeUtils.TIMEZONE_TOKYO)
    time = data.dic[const.TIME]
    n, begin, end = TimeUtils.sliceTime(time, t0, t1)
    if n < 50:
        return
    sliced = Utils.sliceDic(data.dic, begin, end)
    fig, ax = makeFig(1, 1, (10, 5))
    chart = CandleChart(fig, ax, '')
    chart.drawCandle(sliced[const.TIME], sliced[const.OPEN], sliced[const.HIGH], sliced[const.LOW], sliced[const.CLOSE])
    

def main():
    data = MarketData.gbpaud_data(TAKit.matrend(), [2022], [9], 5)
    dic = data.dic
    time = dic[const.TIME]
    print(time[0], '--', time[-1])
    displayChart(data)
   
    
if __name__ == '__main__':
    main()