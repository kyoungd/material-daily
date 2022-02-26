import pandas as pd
import numpy as np
import pandas as pd
import numpy as np
import talib
import os
from datetime import date
from util import AllStocks, StockAnalysis, EnvFile
import logging

class calculateATR:
    def __init__(self):
        self.atrTimeperiod = int(EnvFile.Get('ATR_TIME_PERIOD', '14'))
        self.atrMovementBars = int(EnvFile.Get('ATR_MOVEMENT_BARS', '30'))
        self.atrMovementPercent = int(
            EnvFile.Get('ATR_MOVEMENT_PERCENT', '5'))

    def filterOn(self, tp):
        high = tp.High.to_numpy()
        low = tp.Low.to_numpy()
        close = tp.Close.to_numpy()
        output = talib.ATR(high[::-1], low[::-1], close[::-1], timeperiod=14)
        end = len(output)
        start = end - self.atrTimeperiod
        avgValue = np.mean(output[start:end])
        lastValue = output[-1]
        return avgValue, lastValue

    def Run(self, symbol):
        isLoaded, tp = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                _avg, _last = self.filterOn(tp)
                return {'avg': _avg, 'last': _last, 'close': tp['Close'][0]}
            except Exception as e:
                logging.error(f'filterAtr.calculateATR.Run: {symbol} - {e}')
                print(f'filterAtr.calculateATR.Run: {symbol} - {e}')
        return {'avg': 0, 'last': 0, 'close': 0}


class FilterAtr:
    def __init__(self):
        self.sa = StockAnalysis()
        self.data = self.sa.GetJson
        self.filter = calculateATR()
        self.atrFilterRate = int(EnvFile.Get('ATR_FILTER_RATE', '5'))

    def cleanUp(self, oneValue):
        if np.isnan(oneValue):
            return 0
        return round(oneValue, 2)

    def Run(self, symbol):
        try:
            result = self.filter.Run(symbol)
            changeRate = (result['avg'] / result['close']) * 100
            if result['close'] < 10:
                change = changeRate * 10
            elif result['close'] < 20:
                change = changeRate * 8
            elif result['close'] < 40:
                change = changeRate * 6
            elif result['close'] < 60:
                change = changeRate * 4
            elif result['close'] < 80:
                change = changeRate * 2
            elif result['close'] < 100:
                change = changeRate * 1.5
            elif result['close'] < 200:
                change = changeRate
            elif result['close'] < 500:
                change = changeRate / 1.5
            else:
                change = changeRate / 2
            filterState = True if change < self.atrFilterRate else False
            self.sa.UpdateFilter(self.data, symbol, 'FilterAtr', filterState)
            self.sa.UpdateFilter(self.data, symbol, 'atr',
                                self.cleanUp(result['last']))
            self.sa.UpdateFilter(self.data, symbol, 'close',
                                self.cleanUp(result['close']))
            aatr = result['avg'] / result['close'] if result['close'] > 0 else 0
            self.sa.UpdateFilter(self.data, symbol, 'avgatr', self.cleanUp(aatr))
            # self.sa.UpdateFilter(self.data, symbol, 'avgatr',
            #                     self.cleanUp(result['avg']))
            return True
        except Exception as e:
            logging.error(f'filterAtr.FilterAtr.Run: {symbol} - {e}')
            print(f'filterAtr.FilterAtr.Run: {symbol} - {e}')
            return False

    @staticmethod
    def All():
        filter = FilterAtr()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.data)


if __name__ == '__main__':
    FilterAtr.All()
    print('------------------------------ done ------------------------------')

    # filter = FilterKeyLevels()
    # result = filter.Run('AAPL')
    # print(result)
