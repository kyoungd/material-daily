import os
from util import StockAnalysis, AllStocks, TightMinMax, EnvFile
import pandas as pd
import os
import logging

class fibonachiRetracement:
    def __init__(self, close, isFirstMin, df):
        self.df = df
        self.close = close
        self.isFirstMin = isFirstMin
        minChange = float(EnvFile.Get(
            "FITLER_FIBONACHI_MIN_CHANGE_PERCENT", '0.04'))
        self.minimumChange = self.close * minChange
        self.tolerance50 = 0.45
        self.tolerance63 = 0.68

    def isFibonachiRetrace(self, close, priceFirst, priceSecond):
        priceMove = priceSecond - priceFirst
        if abs(priceMove) < self.minimumChange:
            return False, 0
        fibPrice50 = priceFirst + priceMove * self.tolerance50
        fibPrice63 = priceFirst + priceMove * self.tolerance63
        if (priceMove > 0) and (close > fibPrice50) and (close < fibPrice63):
            return True, abs(priceMove)
        elif (priceMove < 0) and (close < fibPrice50) and (close > fibPrice63):
            return True, abs(priceMove)
        else:
            return False, 0

    def retracement(self):
        price0 = self.df.iloc[0].Close
        price1 = self.df.iloc[1].Close
        price2 = price1 if len(self.df) < 3 else self.df.iloc[2].Close
        f1, m1 = self.isFibonachiRetrace(self.close, price0, price1)
        f2, m2 = self.isFibonachiRetrace(self.close, price1, price2)
        if f1 and f2:
            if m1 > m2:
                return True, {'fib1': price0, 'fib2': price1}
            else:
                return True, {'fib1': price1, 'fib2': price2}
        elif f1:
            return True, {'fib1': price0, 'fib2': price1}
        elif f2:
            return True, {'fib1': price1, 'fib2': price2}
        return False, {}

    def Run(self):
        return self.retracement()


class FilterFibonacciRetracement:
    def __init__(self):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson

    def Run(self, symbol):
        try:
            isLoaded, dfDaily = AllStocks.GetDailyStockData(symbol)
            close = dfDaily['Close'][0]  # last close price
            minMax = TightMinMax()
            isFirstMinimum, df = minMax.Run(symbol)
            if (df is None) or (len(df) < 2):
                return False
            fib = fibonachiRetracement(close, isFirstMinimum, df)
            result, fibs = fib.Run()
            self.sa.UpdateFilter(self.jsonData, symbol, 'fibonachi', result)
            self.sa.UpdateFilter(self.jsonData, symbol, 'fibs', fibs)
            return result
        except Exception as e:
            self.sa.UpdateFilter(self.jsonData, symbol, 'fibonachi', False)
            self.sa.UpdateFilter(self.jsonData, symbol, 'fibs', {})
            logging.error(f'FilterFibonacciRetracement.Run: {symbol} - {e}')
            print(symbol, e)
            return False

    @staticmethod
    def All():
        filter = FilterFibonacciRetracement()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.jsonData)


if __name__ == '__main__':
    FilterFibonacciRetracement.All()
    print('------------------------done ------------------------')

    # data = {'Date':
    #         ['2021-01-07T00:00:00.000000000', '2021-02-01T00:00:00.000000000',
    #          '2021-03-12T00:00:00.000000000', '2021-04-23T00:00:00.000000000',
    #          '2021-05-28T00:00:00.000000000', '2021-09-01T00:00:00.000000000'],
    #         'Close':
    #             [120.00, 100.01, 99.51623309,
    #              93.63782723, 91.50373968, 91.8385245]
    #         }
    # df = pd.DataFrame(data)
    # price = 110.01
    # isFirstMin = False
    # fib = fibonachiRetracement(price, isFirstMin, df)
    # result = fib.Run()
    # print(result)
