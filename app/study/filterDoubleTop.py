import pandas as pd
import numpy as np
import os
from datetime import date
from util import AllStocks, StockAnalysis, TightMinMax, EnvFile

class doubleTop:
    def __init__(self, keylevel:float, df:pd.DataFrame, isFirstMin:bool, doubleTopTolerance:float=0.1):
        self.keylevel:float = keylevel
        self.minlevel:float = keylevel * (1 - doubleTopTolerance)
        self.maxlevel:float = keylevel * (1 + doubleTopTolerance)
        self.dfMin:list = []
        self.dfMax:list = []
        self.isFirstMin:bool = isFirstMin
        for _, row in df.iterrows():
            if isFirstMin:
                self.dfMin.append(row)
            else:
                self.dfMax.append(row)
            isFirstMin = not isFirstMin
        self.topCount = 0
        self.bottomCount = 0

    def lookupTop(self):
        topCount = 0
        for row in self.dfMax:
            if row['Close'] > self.maxlevel:
                break
            elif row['Close'] >= self.minlevel and row['Close'] <= self.maxlevel:
                topCount += 1
            else:
                pass
        return topCount

    def lookupBottom(self):
        bottomCount = 0
        for row in self.dfMin:
            if row['Close'] < self.minlevel:
                break
            elif row['Close'] >= self.minlevel and row['Close'] <= self.maxlevel:
                bottomCount += 1
            else:
                pass
        return bottomCount

    def Run(self):
        topCount = self.lookupTop()
        bottomCount = self.lookupBottom()
        isDoubleTop = (topCount > 0 and self.isFirstMin) or (topCount > 1)
        isDoubleBottom = (bottomCount > 0 and not self.isFirstMin) or (bottomCount > 1)
        return (True if isDoubleTop or isDoubleBottom else False)



class FilterDoubleTop:
    def __init__(self):
        self.doubleTopTolerance = float(EnvFile.Get('FILTER_DOUBLE_TOP_TOLERANCE', '0.1'))
        self.sa = StockAnalysis()
        self.data = self.sa.GetJson

    def Run(self, symbol):
        try:
            _, dfDaily = AllStocks.GetDailyStockData(symbol)
            isLoaded, df = AllStocks.GetWeeklyStockData(symbol)
            if isLoaded:
                lastPrice = dfDaily['Close'][0]
                minmax = TightMinMax(df)
                isFirstMin, dfMinMax = minmax.Run()
                app = doubleTop(lastPrice, dfMinMax, isFirstMin, self.doubleTopTolerance)
                isDoubleTop = app.Run()
                self.sa.UpdateFilter(
                    self.data, symbol, 'dtop', isDoubleTop)
                return isDoubleTop
            else:
                return False
        except Exception as e:
            print('{} {}'.format(symbol, e))
            self.sa.UpdateFilter(
                self.data, symbol, 'dtop', False)
            return False

    @staticmethod
    def All():
        app = FilterDoubleTop()
        AllStocks.Run(app.Run, False)
        app.sa.WriteJson(app.data)


if __name__ == '__main__':
    FilterDoubleTop.All()
    print('----------------------------------- done -----------------------------------')
    # filter = FilterDoubleTop()
    # result = filter.Run('AAPL')
    # print(result)
