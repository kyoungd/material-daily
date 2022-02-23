import numpy as np
import pandas as pd
import os
import copy
from scipy.signal import argrelextrema
from .allstocks import AllStocks
from .environ import EnvFile

class TightMinMax:
    def __init__(self, df, tightMinMaxN = None, colName = None):
        self.colName = 'Close' if colName is None else colName
        self.df = df
        self.df = self.df.reset_index()
        n = int(EnvFile.Get('TIGHT_MINMAX_N', '2'))
        self.minMaxN = n if tightMinMaxN is None else tightMinMaxN

    def getRangeMax(self, df):
        rows = []
        for row in df.iterrows():
            open = row[1]['Open']
            close = row[1]['Close']
            rows.append(open if open > close else close)
        return rows

    def getRangeMin(self, df):
        rows = []
        for row in df.iterrows():
            open = row[1]['Open']
            close = row[1]['Close']
            rows.append(open if open < close else close)
        return rows

    def minMaxItem(self, onedate, close, onetype):
        return {'Date': onedate, 'Close': close, 'Type': onetype}

    def removeDuplicateMinMax(self, df):
        firstMin = False
        l_minmax = None
        minMaxSet = []
        for ix in range(len(df.index)):
            ldate = df.iloc[ix]['Date']
            lmin = df.iloc[ix]['min']
            lmax = df.iloc[ix]['max']
            if not np.isnan(lmin):
                value = lmin
                if l_minmax is None:
                    l_minmax = self.minMaxItem(ldate, value, 'min')
                    minMaxSet.append(l_minmax)
                    firstMin = True
                else:
                    newType = 'max'
                    if l_minmax['Type'] != newType:
                        l_minmax = self.minMaxItem(ldate, value, newType)
                        minMaxSet.append(l_minmax)
                    else:
                        if value < l_minmax['Close']:
                            minMaxSet.pop()
                            l_minmax = self.minMaxItem(ldate, value, newType)
                            minMaxSet.append(l_minmax)
            elif not np.isnan(lmax):
                value = lmax
                if l_minmax is None:
                    l_minmax = self.minMaxItem(ldate, value, 'max')
                    minMaxSet.append(l_minmax)
                    firstMin = False
                else:
                    newType = 'min'
                    if l_minmax['Type'] != newType:
                        l_minmax = self.minMaxItem(ldate, value, newType)
                        minMaxSet.append(l_minmax)
                    else:
                        if value > l_minmax['Close']:
                            minMaxSet.pop()
                            l_minmax = self.minMaxItem(ldate, value, newType)
                            minMaxSet.append(l_minmax)
        df1 = pd.DataFrame(minMaxSet)
        return firstMin, df1

    def getMinMax(self, df=None):
        if df is None:
            df = self.df
        n = self.minMaxN        # number of points to be checked before and after

        df['up'] = self.getRangeMax(df)
        df['down'] = self.getRangeMin(df)

        df['min'] = df.iloc[argrelextrema(df['down'].values, np.less_equal,
                            order=n)[0]]['down']
        df['max'] = df.iloc[argrelextrema(df['up'].values, np.greater_equal,
                            order=n)[0]]['up']

        isFirstMin, df1 = self.removeDuplicateMinMax(df)
        return isFirstMin, df1

    def Run(self):
        isFirstMin, df1 = self.getMinMax()
        return isFirstMin, df1


if __name__ == '__main__':
    symbol = 'AAPL'
    isLoaded, df = AllStocks.GetDailyStockData(symbol)
    if isLoaded:
        app = TightMinMax(df)
        firstMin, df = app.Run()
        print(df)
        print(firstMin)
    print('done')
