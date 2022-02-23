import pandas as pd
import os
from .filterFibonacciRetracement import fibonachiRetracement
from util import AllStocks, StockAnalysis, EnvFile


class filterThreeBarsRetrace:
    def __init__(self):
        self.minChange = float(EnvFile.Get(
            'FILTER_THREEBAR_MIN_CHANGE_PERCENT', '0.02'))
        self.minChangePrice = float(EnvFile.Get(
            'FILTER_THREEBAR_MIN_CHANGE_PRICE', '0.20'))

    def isThreeBars(self, p0, p1, p2):
        minPriceChange = self.minChange * p0
        if minPriceChange < self.minChangePrice:
            minPriceChange = self.minChangePrice
        if abs(p1 - p2) < minPriceChange:
            return False
        if p0 > p1 and p1 < p2:
            return True
        if p0 < p1 and p1 > p2:
            return True
        return False

    def makeDataFrame(self, p0, p1, p2):
        data = {'Date':
                ['2021-01-07T00:00:00.000000000', '2021-02-01T00:00:00.000000000',
                 '2021-03-12T00:00:00.000000000'],
                'Close':
                    [p0, p1, p2]
                }
        df = pd.DataFrame(data)
        return df

    def threeBarsDf(self, dfDaily):
        p0 = dfDaily['Close'][0]  # last close price
        p1 = dfDaily['Close'][1]
        p2 = dfDaily['Close'][2]
        p3 = dfDaily['Close'][3]
        dfs = []
        if self.isThreeBars(p0, p1, p2):
            df = self.makeDataFrame(p0, p1, p2)
            dfs.append(df)
        if self.isThreeBars(p0, p2, p3):
            df = self.makeDataFrame(p0, p2, p3)
            dfs.append(df)
        if self.isThreeBars(p0, p1, p3):
            df = self.makeDataFrame(p0, p1, p3)
            dfs.append(df)
        return dfs

    def ThreeBarLogic(self, dfDaily):
        dfs = self.threeBarsDf(dfDaily)
        if len(dfs) <= 0:
            return False
        for df in dfs:
            isFirstMin = df['Close'][0] < df['Close'][1]
            price = df['Close'][0]
            fib = fibonachiRetracement(price, isFirstMin, df)
            if fib.Run():
                return True
        return False

    def Run(self, symbol):
        try:
            isLoaded, dfDaily = AllStocks.GetDailyStockData(symbol)
            result = self.ThreeBarLogic(dfDaily)
            return result
        except Exception as e:
            print(e)
            return False


class FilterThreeBars:
    def __init__(self):
        self.sa = StockAnalysis()
        self.data = self.sa.GetJson
        self.filter = filterThreeBarsRetrace()

    def Run(self, symbol):
        result = self.filter.Run(symbol)
        self.sa.UpdateFilter(self.data, symbol, 'threebars', result)

    @ staticmethod
    def All():
        app = FilterThreeBars()
        AllStocks.Run(app.Run, False)
        app.sa.WriteJson(app.data)


if __name__ == '__main__':
    FilterThreeBars.All()
    print('------------------------------ done ------------------------------')
