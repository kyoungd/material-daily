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
        self.factor3 = 1.2
        self.factor4 = 1.2
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

    def localMinMax(self, df: pd.DataFrame, index: int, barCount=None):
        barCount = 15 if barCount is None else barCount
        localMin = min(df.iloc[index]['Close'], df.iloc[index]['Open'])
        localMax = max(df.iloc[index]['Close'], df.iloc[index]['Open'])
        lowCount = 0
        highCount = 0
        for ix in range(index, barCount + index):
            row = df.iloc[ix]
            if row['Close'] <= localMin or row['Open'] <= localMin:
                lowCount += 1
            if row['Close'] >= localMax or row['Open'] >= localMax:
                highCount +=1
        return False if lowCount >= barCount-1 or highCount >= barCount + 1 else True

    def wyckoffDoji(self, df:pd.DataFrame, spreads:list, volumes:list, period:int) -> int:
        rangeLength = period - 2
        for ix in range(rangeLength):
            s1 = spreads[ix]
            s2 = spreads[ix+1]
            s3 = spreads[ix+2]
            if abs(s1) > 0.1:
                return 0
            if abs(s1) > abs(s2) or abs(s2) > abs(s2):
                return 0
            v1 = volumes[ix]
            v2 = volumes[ix+1]
            v3 = volumes[ix+2]
            if abs(v1) > abs(v2) or abs(v1) > abs(v3):
                return 0
            c1 = df.iloc[ix].Close
            c2 = df.iloc[ix+1].Close
            c3 = df.iloc[ix+2].Close
            o1 = df.iloc[ix].Open
            o2 = df.iloc[ix+1].Open
            o3 = df.iloc[ix+2].Open
            if c1 >= c2 and c2 > c3 and c2 > o2 and c3 > o3:
                h1 = df.iloc[ix].High
                h2 = df.iloc[ix+1].High
                h3 = df.iloc[ix+2].High
                if h1 >= h2 and self.localMinMax(df, ix):
                    return 10
            if c1 <= c2 and c2 < c3 and c2 < o2 and o3 < c3:
                l1 = df.iloc[ix].Low
                l2 = df.iloc[ix+1].Low
                l3 = df.iloc[ix+2].Low
                if l1 <= l2 and self.localMinMax(df, ix):
                    return 10
        return 0

    def isVsaOk(self, df:pd.DataFrame, spreads:list, volumes:list, period:int) -> int:
        rangeLength = period - 3
        for ix in range(rangeLength):
            s1 = spreads[ix]
            s2 = spreads[ix+1]
            s3 = spreads[ix+2]
            s4 = spreads[ix+3]
            v1 = volumes[ix]
            v2 = volumes[ix+1]
            v3 = volumes[ix+2]
            v4 = volumes[ix+3]
            # down thrust
            if abs(s2) < 0.2 and v2 > 3 and not self.isSameSign(s1, s2) :
                if self.localMinMax(df, ix):
                    return 1
            # selling climax
            if abs(s2) > 3 and v2 > 3 and not self.isSameSign(s1, s2) and abs(s2) > abs(s1) :
                if self.localMinMax(df, ix):
                    return 2
            if self.isSameSign(s4, s3) and self.isSameSign(s2, s3) and not self.isSameSign(s2, s1):
                # effort is less than result
                if (abs(s4) < abs(s3) < abs(s2)) and (v4 > v3 > v2):
                    return 3
                # effort is more than result
                if (abs(s4) > abs(s3) > abs(s2)) and (v4 < v3 < v2):
                    return 4

            if self.isSameSign(s2, s1) and self.isSameSign(s3, s2) and self.isSameSign(s4, s3):
                # no supply bar, pseudo down thrust, inverse downard thrust
                if (abs(s2) * self.factor5) < abs(s3) and (v2 * self.factor5) < v3 and (v2 * self.factor5) < v4:
                    if self.localMinMax(df, ix, 10):
                        return 5

            # if self.isSameSign(s1, s2):
            #     # effort is less than result
            #     if (abs(s2)*self.factor3) < abs(s1) and v2 > (v1 * self.factor3):
            #         return 3
            #     # effort is more than result
            #     if abs(s2) > (abs(s1) * self.factor4) and (v2 * self.factor4) < v1:
            #         return 4
            #     if self.isSameSign(s2, s3):
            #         # no supply bar, pseudo down thrust, inverse downard thrust
            #         if (abs(s1) * self.factor5) < abs(s2) and (v1 * self.factor5) < v2 and (v1 * self.factor5) < v3:
            #             return 5
            # # inverse downward thrust
            # if abs(s1) < 0.2 and v1 > 4:
            #     return 8
            # # failed effort selling climax
            # if abs(s2) > (abs(s3) * self.factor8) and v2 > (v3 * self.factor8) and (not self.isSameSign(s1, s2) and self.isAboutSameSize(s1, s2)):
            #     return 9
        return 0

    def Run(self, symbol: str, df: pd.DataFrame) -> int:
        period = self.averagingBarCount
        if self.isCanCalculate(df, period):
            avgV = self.avgVolumeSwing(df)
            avgS = self.avgOpenCloseSwing(df)
            spreads, volumes = self.getVariables(df, avgS, avgV)
            vsa = self.isVsaOk(df, spreads, volumes, self.barCount)
            vsa = vsa if vsa > 0 else self.wyckoffDoji(
                df, spreads, volumes, self.barCount)
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
