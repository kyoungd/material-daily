import pandas as pd
from util import StockAnalysis, AllStocks, JsonFavorite, EnvFile
import talib
import os
import json
import logging

class FilterCorrelate:
    def __init__(self):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        corrFile = EnvFile.Get('CORRELATE_90_FILE', '---')
        invsFile = EnvFile.Get('INVERSE_90_FILE', '---')
        self.correlates = JsonFavorite(filename=corrFile).GetJson
        self.inverses = JsonFavorite(filename=invsFile).GetJson

    def customSort(self, k):
        return list(k.values())[0]

    def analyzieMatix(self, symbol, rows):
        rows.sort(key=self.customSort, reverse=True)
        symbols = []
        lineCount = 0
        for row in rows:
            lineCount += 1
            key = list(row.keys())[0]
            if key != symbol:
                symbols.append(key)
            if lineCount >= 5:
                return symbols
        return symbols

    def corrMatch(self, symbol, corrs, colname):
        try:
            matrix1 = corrs[symbol]
            analysis1 = self.analyzieMatix(symbol, matrix1)
            self.sa.UpdateFilter(
                self.jsonData, symbol, colname, analysis1)                
        except KeyError:
            self.sa.UpdateFilter(
                self.jsonData, symbol, colname, [])
        except Exception as e:
            logging.error(
                f'FilterCorrelate.corrMatch - {symbol} {colname} {e}')
            print(f'FilterCorrelate.corrMatch - {symbol} {colname} {e}')
            self.sa.UpdateFilter(
                self.jsonData, symbol, 'corr', [])


    def Run(self, symbol):
        isLoaded, df = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            self.corrMatch(symbol, self.correlates, 'corr')
            self.corrMatch(symbol, self.inverses, 'cinv')
        return False

    @staticmethod
    def All():
        filter = FilterCorrelate()
        AllStocks.Run(filter.Run)
        filter.sa.WriteJson(filter.jsonData)


if __name__ == '__main__':
    FilterCorrelate.All()
    print('---------- done ----------')
    # filter = FilterEma(symbol='AAPL', barCount=20)
    # up, down = filter.Run(filter.symbol)
    # print(up, down)
