import pandas as pd
from util import StockAnalysis, AllStocks
import talib
import os
import numpy as np

class FilterEma:
    def __init__(self, barCount, showtCount=None, longCount=None):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        self.trendLength = int(os.getenv('FILTER_TREND_LENGTH', '30'))
        self.trendAt = int(os.getenv('FILTER_TREND_AT', '5'))
        self.nearPercent = 0.05
        self.setBarCount(barCount)
        self.shortCount = int(os.getenv('FILTER_EMA_SHORT_COUNT', '14'))
        self.longCount = int(os.getenv('FILTER_EMA_LONG_COUNT', '50'))

    def setSymbol(self, symbol):
        self.symbol = symbol

    def setBarCount(self, barCount):
        self.barCount = barCount
        switcher = {
            20: 'ema20',
            50: 'ema50',
            200: 'ema200'
        }
        self.filterName = switcher.get(barCount, 'ema20')
        self.trendLength = 30

    def FilterOn(self, closes, outputShort, outputLong):
        # create dataframe with close and output
        idx = 0
        repeatCount = 0
        lastState = 0
        longs = iter(outputLong)
        prices = iter(closes)
        for short in outputShort:
            idx += 1
            long = next(longs)
            price = next(prices)
            if np.isnan(short) or np.isnan(long) or np.isnan(price):
                break
            if price > short and short > long:
                thisState = 1
            elif price < short and short < long:
                thisState = -1
            elif idx <= 5:
                thisState = None
                lastState = 0
                repeatCount = 0
            else:
                break
            if lastState == 0 or lastState == thisState:
                repeatCount += 1
            else:
                break
        return repeatCount

    def isNearEma(self, close, open, ema):
        isNear = True if abs(close - ema) / close <= self.nearPercent else False
        if isNear:
            return True
        return True if abs(open - ema) / open <= self.nearPercent else False

    def Run(self, symbol):
        isLoaded, tp = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                self.setSymbol(symbol)
                close = tp.Close.to_numpy()
                open = tp.Open.to_numpy()
                output = talib.EMA(close[::-1], timeperiod=self.barCount)
                self.sa.UpdateFilter(
                    self.jsonData, self.symbol, self.filterName, self.isNearEma(close[0], open[0], output[-1]))
            except Exception as e:
                print('filterEma.Run() {}'.format(e))
                self.sa.UpdateFilter(
                    self.jsonData, self.symbol, self.filterName, False)
        return False

    def Trending(self, symbol):
        isLoaded, tp = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                close = tp.Close.to_numpy()
                outputShort = talib.EMA(
                    close[::-1], timeperiod=self.shortCount)
                outputLong = talib.EMA(close[::-1], timeperiod=self.longCount)
                trendingDays = self.FilterOn(
                    close, outputShort[::-1], outputLong[::-1])
                self.sa.UpdateFilter(self.jsonData, symbol, 'td', trendingDays)
            except Exception as e:
                print('filterEma.Run() {}'.format(e))
                self.sa.UpdateFilter(self.jsonData, symbol, 'td', 0)
        return False

    def WriteFilter(self):
        self.sa.WriteJson(self.jsonData)

    @staticmethod
    def All():
        filter = FilterEma(20)
        AllStocks.Run(filter.Run, False)
        filter.setBarCount(50)
        AllStocks.Run(filter.Run, False)
        filter.setBarCount(200)
        AllStocks.Run(filter.Run, False)
        AllStocks.Run(filter.Trending, False)
        filter.WriteFilter()


if __name__ == '__main__':
    FilterEma.All()
    print('---------- done ----------')
    # filter = FilterEma(symbol='AAPL', barCount=20)
    # up, down = filter.Run(filter.symbol)
    # print(up, down)
