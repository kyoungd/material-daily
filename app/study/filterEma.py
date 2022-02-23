import pandas as pd
from util import StockAnalysis, AllStocks
import talib
import os

class FilterEma:
    def __init__(self, barCount):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        self.trendLength = int(os.getenv('FILTER_TREND_LENGTH', '30'))
        self.trendAt = int(os.getenv('FILTER_TREND_AT', '5'))
        self.nearPercent = 0.05
        self.setBarCount(barCount)

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

    def FilterOn(self, close, output):
        # create dataframe with close and output
        df = pd.DataFrame(
            {'close': close[0:self.trendLength], 'ema': output[0:self.trendLength]})
        upCount = 0
        downCount = 0
        for index, row in df.iterrows():
            if row['close'] > row['ema']:
                upCount += 1
            elif row['close'] < row['ema']:
                downCount += 1
        return upCount, downCount

    def isNearEma(self, close, ema):
        return True if abs(close - ema) / close <= self.nearPercent else False

    def Run(self, symbol):
        isLoaded, tp = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                self.setSymbol(symbol)
                close = tp.Close.to_numpy()
                output = talib.EMA(close[::-1], timeperiod=self.barCount)
                upCount, downCount = self.FilterOn(close, output[::-1])
                self.sa.UpdateFilter(self.jsonData, self.symbol, 'trendup',
                                     True if upCount > self.trendAt else False)
                self.sa.UpdateFilter(self.jsonData, self.symbol, 'trenddown',
                                     True if downCount > self.trendAt else False)
                self.sa.UpdateFilter(
                    self.jsonData, self.symbol, self.filterName, self.isNearEma(close[0], output[-1]))
            except Exception as e:
                print('filterEma.Run() {}'.format(e))
                self.sa.UpdateFilter(
                    self.jsonData, self.symbol, 'trendup', False)
                self.sa.UpdateFilter(
                    self.jsonData, self.symbol, 'trenddown', False)
                self.sa.UpdateFilter(
                    self.jsonData, self.symbol, self.filterName, False)
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
        filter.WriteFilter()


if __name__ == '__main__':
    FilterEma.All()
    print('---------- done ----------')
    # filter = FilterEma(symbol='AAPL', barCount=20)
    # up, down = filter.Run(filter.symbol)
    # print(up, down)
