import pandas as pd
import numpy as np
import pandas as pd
import numpy as np
import talib
import os
from datetime import date
from util import AllStocks, StockAnalysis, EnvFile
import logging

class engulfingCandle:
    def __init__(self, df, minChangePercent, minChangeValue):
        data = df.loc[0:4]
        self.data = data[::-1]
        minCalcPrice = self.data.iloc[0].Close * minChangePercent
        self.minValue = minChangeValue if minCalcPrice < minChangeValue else minCalcPrice

    def CDLENGULFING(self, df):
        res = talib.CDLENGULFING(
            df.Open.values, df.High.values, df.Low.values, df.Close.values)
        return res

    def CDLENGULFING_MIN(self, df, result, minChange):
        for index, row in df.iterrows():
            if index > 0 and result[index] != 0:
                change = abs(df.Open[index] - df.Close[index-1])
                return True if change >= minChange else False
        return False

    def run(self):
        step1 = self.CDLENGULFING(self.data)
        result = self.CDLENGULFING_MIN(self.data, step1, self.minValue)
        return result


class FilterCandlePattern:
    def __init__(self):
        self.minEngulfingCandleChangePercent = float(
            EnvFile.Get('MIN_ENGULFING_CANDLE_CHANGE_PERCENT', '0.03'))
        self.minEngulfingCandleChangevalue = float(
            EnvFile.Get('MIN_ENGULFING_CANDLE_CHANGE_VALUE', '0.2'))
        self.sa = StockAnalysis()
        self.data = self.sa.GetJson

    def Run(self, symbol):
        isLoaded, df = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                filterEngulf = engulfingCandle(df, self.minEngulfingCandleChangePercent, self.minEngulfingCandleChangevalue)
                engulf = filterEngulf.run()
                self.sa.UpdateFilter(self.data, symbol, 'engulf', engulf)
            except Exception as e:
                self.sa.UpdateFilter(self.data, symbol, 'engulf', False)
                logging.error(f'filterCandlePattern.Run: {symbol} - {e}')
                print(f'filterCandlePattern.Run: {symbol} - {e}')
        return False

    @staticmethod
    def All():
        filter = FilterCandlePattern()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.data)

if __name__ == '__main__':
    FilterCandlePattern.All()
