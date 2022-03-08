import os
from util import StockAnalysis, AllStocks, TightMinMax, EnvFile
import pandas as pd
import os
import logging

class longWickCandle:
    def __init__(self, period = None):
        self.wickPeriodBarCount = int(EnvFile.Get('FILTER_WICK_PERIOD_BAR_COUNT', '5')) if period is None else period

    def isCanCalculate(self, df: pd.DataFrame, period:int):
        return False if len(df) < period else True

    def avgSwing(self, df: pd.DataFrame, period: int, swingFunc) -> float:
        swingTotal:float = 0
        swingPeriod:int = period * 4 if len(df) > period * 4 else len(df)
        swingMax:float = 0
        for _, row in df[:swingPeriod].iterrows():
            swing = swingFunc(row)
            swingMax = max(swingMax, swing)
            swingTotal += swing
        avgSwing:float = (swingTotal - swingMax) / (swingPeriod - 1)
        return avgSwing

    def avgHighLowSwing(self, df: pd.DataFrame, period:int) -> float:
        return self.avgSwing(df, period, lambda row: abs(row.High - row.Low))

    def avgVolumeSwing(self, df:pd.DataFrame, period: int) -> float:
        return self.avgSwing(df, period, lambda row: abs(row.Volume))

    def avgOpenCloseSwing(self, df: pd.DataFrame, period:int) -> float:
        return self.avgSwing(df, period, lambda row: abs(row.Close - row.Open))

    # maxWickRange = High - Low (wick range)
    def maxWickRange(self, symbol:str, df: pd.DataFrame, period:int) -> float:
        try:
            avgSwing:float = self.avgHighLowSwing(df, period)
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
            avgSwing:float = self.avgHighLowSwing(df, period)
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
            avgVolumeSwing:float = self.avgVolumeSwing(df, period)
            maxVolume:float = 0
            for _, row in df[:period].iterrows():
                maxVolume = max(maxVolume, row.Volume)
            volChange = maxVolume / avgVolumeSwing
            return volChange
        except Exception as e:
            logging.error(f'FilterLongWickCandle.volumeClimax: {symbol} - {e}')
            print(f'FilterLongWickCandle.volumeClimax: {symbol} - {e}')
            return 0

    def priceJump(self, symbol:str, df: pd.DataFrame, period:int) -> float:
        try:
            avgVolumeSwing:float = self.avgVolumeSwing(df, period)
            avgPriceSwing:float = self.avgOpenCloseSwing(df, period)
            maxPriceMove:float = 0
            for _, row in df[:period].iterrows():
                if avgVolumeSwing > row.Volume:
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
            volClimax = self.volumeClimax(symbol, df, period)
            pJump = self.priceJump(symbol, df, period)
            return wickRange, wickHeight, volClimax, pJump
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
                maxRange, maxHeight, volClimax, pJump = self.wick.Run(symbol, df)
                self.sa.UpdateFilter(self.jsonData, symbol, 'wr', round(maxRange*100))
                self.sa.UpdateFilter(self.jsonData, symbol, 'wh', round(maxHeight*100))
                self.sa.UpdateFilter(self.jsonData, symbol, 'vc', round(volClimax*100))
                self.sa.UpdateFilter(self.jsonData, symbol, 'pj', round(pJump*100))
            return False
        except Exception as e:
            self.sa.UpdateFilter(self.jsonData, symbol, 'wr', 0)
            self.sa.UpdateFilter(self.jsonData, symbol, 'wh', 0)
            self.sa.UpdateFilter(self.jsonData, symbol, 'vc', 0)
            self.sa.UpdateFilter(self.jsonData, symbol, 'pj', 0)
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
