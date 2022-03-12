import os
import pandas as pd
import os
import logging
from util import StockAnalysis, AllStocks, TightMinMax, EnvFile
from .filterAccDis import WyckoffAccumlationDistribution

class longWickCandle:
    def __init__(self, period = None):
        self.wickPeriodBarCount = int(EnvFile.Get('FILTER_WICK_PERIOD_BAR_COUNT', '25')) if period is None else period
        self.volumeAverageBarCount = int(EnvFile.Get('FILTER_VOLUME_AVERAGE_BAR_COUNT', '20'))
        self.wyckoff = WyckoffAccumlationDistribution()

    def isCanCalculate(self, df: pd.DataFrame, period:int):
        return False if len(df) < period else True

    def avgSwing(self, df: pd.DataFrame, swingFunc) -> float:
        swingTotal:float = 0
        swingPeriod:int = self.volumeAverageBarCount if len(df) > self.volumeAverageBarCount else len(df)
        swingMax:float = 0
        for _, row in df[:swingPeriod].iterrows():
            swing = swingFunc(row)
            swingMax = max(swingMax, swing)
            swingTotal += swing
        oneAvgSwing:float = (swingTotal - swingMax) / (swingPeriod - 1)
        return oneAvgSwing

    def avgHighLowSwing(self, df: pd.DataFrame) -> float:
        return self.avgSwing(df, lambda row: abs(row.High - row.Low))

    def avgVolumeSwing(self, df:pd.DataFrame) -> float:
        return self.avgSwing(df, lambda row: abs(row.Volume))

    def avgOpenCloseSwing(self, df: pd.DataFrame) -> float:
        return self.avgSwing(df, lambda row: abs(row.Close - row.Open))

    # maxWickRange = High - Low (wick range)
    def maxWickRange(self, symbol:str, df: pd.DataFrame, period:int) -> float:
        try:
            avgSwing:float = self.avgHighLowSwing(df)
            maxWickRange:float = 0
            for _, row in df[:period].iterrows():
                wickRange = row.High - row.Low
                maxWickRange = max(maxWickRange, wickRange)
            return (maxWickRange/avgSwing)
        except Exception as e:
            logging.error(f'FilterLongWickCandle.maxWickHeight: {symbol} - {e}')
            print(f'FilterLongWickCandle.maxWickHeight: {symbol} - {e}')
            return 0

    # maxWickHeight = (maxWickRange - maxWickPrice) / avgSwing (wick only range compared to the average wick range)
    def maxWickHeight(self, symbol:str, df: pd.DataFrame, period:int) -> float:
        try:
            avgSwing:float = self.avgHighLowSwing(df)
            maxWickHeight:float = 0
            for _, row in df[:period].iterrows():
                wickRange:float = row.High - row.Low
                priceRange:float = abs(row.Close - row.Open)
                wickHeight:float = wickRange - priceRange
                maxWickHeight = max(maxWickHeight, wickHeight)
            return (maxWickHeight/avgSwing)
        except Exception as e:
            logging.error(f'FilterLongWickCandle.maxWickHeight: {symbol} - {e}')
            print(f'FilterLongWickCandle.maxWickHeight: {symbol} - {e}')
            return 0

    def volumeClimax(self, symbol:str, df: pd.DataFrame, period:int) -> float:
        try:
            avgVolSwing:float = self.avgVolumeSwing(df)
            maxVolume:float = 0
            climaxIndex: int = 0
            for index, row in df[:period].iterrows():
                if maxVolume < row.Volume:
                    maxVolume = row.Volume
                    climaxIndex = index
            volChange = maxVolume / avgVolSwing
            return volChange, climaxIndex
        except Exception as e:
            logging.error(f'FilterLongWickCandle.volumeClimax: {symbol} - {e}')
            print(f'FilterLongWickCandle.volumeClimax: {symbol} - {e}')
            return 0, 0

    def priceJump(self, symbol:str, df: pd.DataFrame, period:int) -> float:
        try:
            avgVolSwing:float = self.avgVolumeSwing(df)
            avgPriceSwing:float = self.avgOpenCloseSwing(df)
            maxPriceMove:float = 0
            for _, row in df[:period].iterrows():
                if avgVolSwing > row.Volume:
                    maxPriceMove = max(maxPriceMove, abs(row.Close - row.Open))
            priceChange = maxPriceMove / avgPriceSwing            
            return priceChange
        except Exception as e:
            logging.error(f'FilterLongWickCandle.priceJump: {symbol} - {e}')
            print(f'FilterLongWickCandle.priceJump: {symbol} - {e}')
            return 0

    def Run(self, symbol:str, df: pd.DataFrame, period = None):
        period = self.wickPeriodBarCount if period is None else period
        if self.isCanCalculate(df, period):
            wickRange = self.maxWickRange(symbol, df, period)
            wickHeight = self.maxWickHeight(symbol, df, period)
            volClimax, climaxIndex = self.volumeClimax(symbol, df, period)
            pJump = self.priceJump(symbol, df, period)
            isAccDis = False if climaxIndex <= 0 else self.wyckoff.Run(symbol, df, volClimax, climaxIndex)
            return wickRange, wickHeight, volClimax, pJump, isAccDis
        else:
            return 0, 0


class FilterLongWickCandle:
    def __init__(self):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        self.wick = longWickCandle()

    def Run(self, symbol:str):
        try:
            isLoaded, df = AllStocks.GetDailyStockData(symbol)
            if isLoaded:
                maxRange, maxHeight, volClimax, pJump, isAccDis = self.wick.Run(symbol, df)
                self.sa.UpdateFilter(self.jsonData, symbol, 'wr', round(maxRange*100))
                self.sa.UpdateFilter(self.jsonData, symbol, 'wh', round(maxHeight*100))
                self.sa.UpdateFilter(self.jsonData, symbol, 'vc', round(volClimax*100))
                self.sa.UpdateFilter(self.jsonData, symbol, 'pj', round(pJump*100))
                self.sa.UpdateFilter(self.jsonData, symbol, 'ad', isAccDis)
            return False
        except Exception as e:
            self.sa.UpdateFilter(self.jsonData, symbol, 'wr', 0)
            self.sa.UpdateFilter(self.jsonData, symbol, 'wh', 0)
            self.sa.UpdateFilter(self.jsonData, symbol, 'vc', 0)
            self.sa.UpdateFilter(self.jsonData, symbol, 'pj', 0)
            self.sa.UpdateFilter(self.jsonData, symbol, 'ad', False)
            logging.error(f'FilterLongWickCandle.Run: {symbol} - {e}')
            print(f'FilterLongWickCandle.Run: {symbol} - {e}')
            return False

    @staticmethod
    def All():
        filter = FilterLongWickCandle()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.jsonData)


if __name__ == '__main__':
    FilterLongWickCandle.All()
    print('------------------------done ------------------------')

    # data = {'Date':
    #         ['2021-01-07T00:00:00.000000000', '2021-02-01T00:00:00.000000000',
    #          '2021-03-12T00:00:00.000000000', '2021-04-23T00:00:00.000000000',
    #          '2021-05-28T00:00:00.000000000', '2021-09-01T00:00:00.000000000'],
    #         'Close':
    #             [120.00,      100.01,      99.51623309,
    #              93.63782723, 91.50373968, 91.8385245]
    #         }
    # df = pd.DataFrame(data)
    # price = 110.01
    # isFirstMin = False
    # fib = fibonachiRetracement(price, isFirstMin, df)
    # result = fib.Run()
    # print(result)
