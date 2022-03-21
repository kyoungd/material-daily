import os
import pandas as pd
import os
import logging
import json
from util import StockAnalysis, AllStocks, TightMinMax, EnvFile


class volumeSpreadAnalysis:
    def __init__(self):
        self.barCount:int = 5
        self.averagingBarCount:int = 20
        self.factor3 = 1.8
        self.factor4 = 1.8
        self.factor5 = 1.8
        self.factor8 = 1.8

    def isCanCalculate(self, df: pd.DataFrame, period: int):
        return False if len(df) < period else True

    def avgSwing(self, df: pd.DataFrame, swingFunc) -> float:
        swingTotal: float = 0
        swingPeriod: int = self.averagingBarCount if len(
            df) > self.averagingBarCount else len(df)
        swingMax: float = 0
        for _, row in df[:swingPeriod].iterrows():
            swing = swingFunc(row)
            swingMax = max(swingMax, swing)
            swingTotal += swing
        oneAvgSwing: float = (swingTotal - swingMax) / (swingPeriod - 1)
        return oneAvgSwing

    def avgHighLowSwing(self, df: pd.DataFrame) -> float:
        return self.avgSwing(df, lambda row: abs(row.High - row.Low))

    def avgVolumeSwing(self, df: pd.DataFrame) -> float:
        return self.avgSwing(df, lambda row: abs(row.Volume))

    def avgOpenCloseSwing(self, df: pd.DataFrame) -> float:
        return self.avgSwing(df, lambda row: abs(row.Close - row.Open))

    def getVariables(self, df:pd.DataFrame, avgSpread: float, avgVolume:float):
        spreads = []
        volumes = []
        for _, row in df[0:5].iterrows():
            spread = (row.Close - row.Open) / avgSpread
            volume = row.Volume / avgVolume
            spreads.append(spread)
            volumes.append(volume)
        return spreads, volumes

    def isPositive(self, number: float):
        if number < 0:
            return False
        return True

    def isSameSign(self, number1: float, number2: float):
        if number1 > 0 and number2 > 0:
            return True
        if number1 < 0 and number2 < 0:
            return True
        return False

    def isAboutSameSize(self, number1: float, number2: float):
        newPercent = abs(number2) / number1 if number1 != 0 else 0
        if newPercent > 0.8 and newPercent <= 1.2:
            return True
        return False

    def isVsaOk(self, spreads:list, volumes:list, period:int) -> str:
        rangeLength = period - 2
        for ix in range(rangeLength):
            s1 = spreads[ix]
            s2 = spreads[ix+1]
            s3 = spreads[ix+2]
            v1 = volumes[ix]
            v2 = volumes[ix+1]
            v3 = volumes[ix+2]
            # down thrust
            if abs(s1) < 0.2 and v1 > 5:
                return 1
            # selling climax
            if abs(s1) > 3.5 and v1 > 5:
                return 2
            if self.isSameSign(s1, s2):
                # effort is less than result
                if (abs(s2)*self.factor3) < abs(s1) and v2 > (v1 * self.factor3):
                    return 3
                # effort is more than result
                if abs(s2) > (abs(s1) * self.factor4) and (v2 * self.factor4) < v1:
                    return 4
                if self.isSameSign(s2, s3):
                    # no supply bar, pseudo down thrust, inverse downard thrust
                    if (abs(s1) * self.factor5) < abs(s2) and (v1 * self.factor5) < v2 and (v1 * self.factor5) < v3:
                        return 5
            # inverse downward thrust
            if abs(s1) < 0.2 and v1 > 4:
                return 8
            # failed effort selling climax
            if abs(s2) > (abs(s3) * self.factor8) and v2 > (v3 * self.factor8) and (not self.isSameSign(s1, s2) and self.isAboutSameSize(s1, s2)):
                return 9
        return 0

    def Run(self, symbol: str, df: pd.DataFrame):
        period = self.averagingBarCount
        if self.isCanCalculate(df, period):
            avgV = self.avgVolumeSwing(df)
            avgS = self.avgOpenCloseSwing(df)
            spreads, volumes = self.getVariables(df, avgS, avgV)
            vsa = self.isVsaOk(spreads, volumes, self.barCount)
            return vsa
        else:
            return 0


class FilterVolumeSpreadAnalysis:
    def __init__(self):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        self.voa = volumeSpreadAnalysis()

    def Run(self, symbol: str):
        try:
            isLoaded, df = AllStocks.GetDailyStockData(symbol)
            if isLoaded:
                data = self.voa.Run(symbol, df)
                self.sa.UpdateFilter(self.jsonData, symbol, 'vs', data)
            return False
        except Exception as e:
            self.sa.UpdateFilter(self.jsonData, symbol, 'vs', 0)
            logging.error(f'FilterVolumeSpreadAnalysis.Run: {symbol} - {e}')
            print(f'FilterVolumeSpreadAnalysis.Run: {symbol} - {e}')
            return False

    @staticmethod
    def All():
        filter = FilterVolumeSpreadAnalysis()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.jsonData)


if __name__ == '__main__':
    FilterVolumeSpreadAnalysis.All()
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
