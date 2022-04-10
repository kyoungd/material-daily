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


class starCandle:
    def __init__(self, symbol:str, df:pd.DataFrame):
        data = df.loc[0:4]
        self.data = data[::-1]
        self.symbol = symbol

    def CDLEVENINGDOJISTAR(self, df):
        res = talib.CDLEVENINGDOJISTAR(
            df.Open.values, df.High.values, df.Low.values, df.Close.values)
        return res
    
    def CDLEVENINGSTAR(self, df):
        res = talib.CDLEVENINGSTAR(
            df.Open.values, df.High.values, df.Low.values, df.Close.values)
        return res

    def CDLMORNINGDOJISTAR(self, df):
        res = talib.CDLMORNINGDOJISTAR(
            df.Open.values, df.High.values, df.Low.values, df.Close.values)
        return res

    def CDLMORNINGSTAR(self, df):
        res = talib.CDLMORNINGSTAR(
            df.Open.values, df.High.values, df.Low.values, df.Close.values)
        return res

    def run(self):
        try:
            step1 = self.CDLEVENINGDOJISTAR(self.data)
            step2 = self.CDLEVENINGSTAR(self.data)
            step3 = self.CDLMORNINGDOJISTAR(self.data)
            step4 = self.CDLMORNINGSTAR(self.data)
            return sum(step1) + sum(step2) + sum(step3) + sum(step4)
        except Exception as e:
            logging.error(f'filterCandlePattern.starPattern.run: {self.symbol} - {e}')
            return 0

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
                filterStar = starCandle(symbol, df)
                engulf = filterEngulf.run()
                star = filterStar.run()
                self.sa.UpdateFilter(self.data, symbol, 'engulf', engulf)
                self.sa.UpdateFilter(self.data, symbol, 'st', True if star > 0 else False)
            except Exception as e:
                self.sa.UpdateFilter(self.data, symbol, 'engulf', False)
                self.sa.UpdateFilter(self.data, symbol, 'st', False)
                logging.error(f'filterCandlePattern.Run: {symbol} - {e}')
                print(f'filterCandlePattern.Run: {symbol} - {e}')
        return False

    @staticmethod
    def All():
        filter = FilterCandlePattern()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.data)

    @staticmethod
    def Test():
        symbol = 'TSLA'
        isLoaded, df = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            filter = starCandle(symbol, df)
            result = filter.run()
            print(result)

if __name__ == '__main__':
    pass
