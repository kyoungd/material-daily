import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from .allstocks import AllStocks, EnvFile
import os

class LocalMinMax:
    def __init__(self, df, tightMinMaxN = None, colName = None):
        self.colName = 'Close' if colName is None else colName
        self.df = df
        self.df = self.df.reset_index()
        if tightMinMaxN is None:
            self.minMaxN = int(EnvFile.Get('TIGHT_MINMAX_N', '4'))
        else:
            self.minMaxN = tightMinMaxN
    
    def Polyfit(self):
        # discrete dataset
        x_data = self.df.index.tolist()      # the index will be our x axis, not date
        y_data = self.df['Close']
        t_data = self.df['Date']

        # x values for the polynomial fit, 200 points
        x = np.linspace(0, max(self.df.index.tolist()),
                        max(self.df.index.tolist()) + 1)

        # polynomial fit of degree xx
        pol = np.polyfit(x_data, y_data, 30)
        y_pol = np.polyval(pol, x)

        data = y_pol

        # ___ detection of local minimums and maximums ___

        min_max = np.diff(np.sign(np.diff(data))).nonzero()[
            0] + 1          # local min & max
        l_min = (np.diff(np.sign(np.diff(data))) >
                 0).nonzero()[0] + 1      # local min
        l_max = (np.diff(np.sign(np.diff(data))) <
                 0).nonzero()[0] + 1      # local max

        # ___ package local minimums and maximums for return  ___

        # dfMin = None if len(l_min) < 0 else pd.DataFrame.from_dict(
        #     {'Date': t_data[l_min].values, 'Close': data[l_min]})
        # dfMax = pd.DataFrame.from_dict(
        #     {'Date': t_data[l_max].values, 'Close': data[l_max]})
        # return dfMin, dfMax

        l_minmax = np.sort(np.append(l_min, l_max))
        isFirstMinimum = True if l_min[len(
            l_min)-1] < l_max[len(l_max)-1] else False
        timeframes = t_data[l_minmax].values
        closes = data[l_minmax]
        df = pd.DataFrame.from_dict({'Date': timeframes, 'Close': closes})
        return isFirstMinimum, df

    def minMaxItem(self, onedate, close, onetype):
        return {'Date': onedate, f'{self.colName}': close, 'Type': onetype}

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
                        if value < l_minmax[self.colName]:
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
                        if value > l_minmax[self.colName]:
                            minMaxSet.pop()
                            l_minmax = self.minMaxItem(ldate, value, newType)
                            minMaxSet.append(l_minmax)
        df1 = pd.DataFrame(minMaxSet)
        return firstMin, df1


    def TightMinMiax(self, df=None):
        if df is None:
            df = self.df
        n = self.minMaxN        # number of points to be checked before and after

        df['min'] = df.iloc[argrelextrema(df[self.colName].values, np.less_equal,
                            order=n)[0]][self.colName]
        df['max'] = df.iloc[argrelextrema(df[self.colName].values, np.greater_equal,
                            order=n)[0]][self.colName]

        isFirstMin, df1 = self.removeDuplicateMinMax(df)
        return isFirstMin, df1


    def Run(self):
        isFirstMin, df1 = self.TightMinMiax()
        return isFirstMin, df1


if __name__ == '__main__':
    symbol = 'AAPL'
    isLoaded, df = AllStocks.GetDailyStockData(symbol)
    if isLoaded:
        app = LocalMinMax(df)
        firstMin, df = app.Run()
        print(df)
        print(firstMin)
    print('done')
