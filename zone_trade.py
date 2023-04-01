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
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from Utils import Utils
from TimeUtils import TimeUtils
from DataBuffer import ResampleDataBuffer
from MarketData import MarketData
from CandleChart import CandleChart, BandPlot, makeFig, gridFig, Colors
from TA import TechnicalAnalysis as ta
from TAKit import TAKit
from const import const


def plotChart(dic: dict):
    fig, axes = gridFig([8, 1], (30, 5))
    chart1 = CandleChart(fig, axes[0], '')
    chart1.drawCandle(dic[const.TIME], dic[const.OPEN], dic[const.HIGH], dic[const.LOW], dic[const.CLOSE])
    chart1.drawLine(dic[const.TIME], dic['SMA5'])
    chart1.drawLine(dic[const.TIME], dic['SMA20'], color='green')
    chart1.drawLine(dic[const.TIME], dic['SMA60'], color='blue')
    chart1.drawMarkers(dic[const.TIME], dic[const.LOW], -0.05, dic['SIGNAL'], 1, '^', 'green', overlay=1, markersize=20)
    chart1.drawMarkers(dic[const.TIME], dic[const.LOW], -0.05, dic['SIGNAL'], 2, '^', 'green', overlay=2, markersize=20)
    chart1.drawMarkers(dic[const.TIME], dic[const.HIGH], 
                       50, dic['SIGNAL'], -1, '^', 'red', overlay=1, markersize=20)
    chart1.drawMarkers(dic[const.TIME], dic[const.HIGH], 50, dic['SIGNAL'], -2, '^', 'red', overlay=2, markersize=20)
    chart2 = BandPlot(fig, axes[1], 'MA Trend', date_format=CandleChart.DATE_FORMAT_DAY_HOUR)
    colors = {ta.UPPER_TREND: 'red',
              ta.UPPER_SUB_TREND: Colors.light_red,
              ta.UPPER_DIP: 'black',
              ta.LOWER_TREND: 'green',
              ta.LOWER_SUB_TREND: Colors.light_green,
              ta.LOWER_DIP: 'black',
              ta.NO_TREND: 'gray'}
    chart2.drawBand(dic[const.TIME], dic['MA_TREND'], colors=colors)


def displayChart(data: ResampleDataBuffer, years, months, from_hour, to_hour):
    time = data.dic[const.TIME]
    t0 = t1 = None
    for year in years:
        for month in months:
            for day in range(1, 32):
                try:
                    t0 = TimeUtils.pyTime(year, month, day, from_hour, 0, 0, TimeUtils.TIMEZONE_TOKYO)
                    t1 = TimeUtils.pyTime(year, month, day, to_hour, 0, 0, TimeUtils.TIMEZONE_TOKYO)
                    if to_hour < from_hour:
                        t1 += timedelta(days=1)                        
                except:
                    continue
                n, begin, end = TimeUtils.sliceTime(time, t0, t1)
                if n < 50:
                    continue
                dic = Utils.sliceDic(data.dic, begin, end)
                plotChart(dic)


def main():
    data = MarketData.gbpaud_data(TAKit.matrend(), [2022], np.arange(1, 13), 5)
    dic = data.dic
    print(dic.keys())
    time = dic[const.TIME]
    print(time[0], '--', time[-1])
    displayChart(data, [2022], np.arange(1, 2), 7, 2)
   
    
if __name__ == '__main__':
    main()