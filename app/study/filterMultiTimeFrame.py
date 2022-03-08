import pandas as pd
import numpy as np
import os
from datetime import date
from util import AllStocks, StockAnalysis, EnvFile


class multiTimeFrame:
    def __init__(self):
        pass

    def Run(self, dfDaily: pd.DataFrame, dfWeekly: pd.DataFrame):
        pass


class FilterMultiTimeFrame:
    def __init__(self):
        self.sa = StockAnalysis()
        self.data = self.sa.GetJson

    def Run(self, symbol):
        try:
            _, dfDaily = AllStocks.GetDailyStockData(symbol)
            isLoaded, dfWeekly = AllStocks.GetWeeklyStockData(symbol)
            if isLoaded:
                pass
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def All():
        app = FilterMultiTimeFrame()
        AllStocks.Run(app.Run, False)
        app.sa.WriteJson(app.data)


if __name__ == '__main__':
    FilterMultiTimeFrame.All()
    print('----------------------------------- done -----------------------------------')
    # filter = FilterKeyLevels()
    # result = filter.Run('AAPL')
    # print(result)
