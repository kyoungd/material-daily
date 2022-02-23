import pandas as pd
import numpy as np
import os
from datetime import date
from util import AllStocks, StockAnalysis, EnvFile


class KeyLevels:
    def __init__(self):
        pass

    def getSupport(self, df, i):
        supportPrice = 0
        if df['Low'][i] < df['Low'][i-1] and df['Low'][i] < df['Low'][i+1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]:
            supportPrice = df['Low'][i]

        return supportPrice

    def getResistance(self, df, i):
        resistancePrice = 0
        if df['High'][i] > df['High'][i-1] and df['High'][i] > df['High'][i+1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]:
            resistancePrice = df['High'][i]

        return resistancePrice

    def Run(self, df):
        allPrices = []
        for i in range(2, df.shape[0] - 2):
            supportPrice = self.getSupport(df, i)
            resistantPrice = self.getResistance(df, i)
            if supportPrice != 0:
                allPrices.append((i, supportPrice))
            elif resistantPrice != 0:
                allPrices.append((i, resistantPrice))

        # df['Date'] = pd.to_datetime(df.index)
        # df['Date'] = df['Date'].apply(mpl_dates.date2num)
        # df = df.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]

        # get rid of prices near to one another reduce noise

        mean = np.mean(df['High'] - df['Low'])  # rough estimate of volatility

        allPrices = []

        for i in range(2, df.shape[0] - 2):
            supportPrice = self.getSupport(df, i)
            resistantPrice = self.getResistance(df, i)
            if supportPrice != 0:
                if np.sum([abs(supportPrice-x) < mean for x in allPrices]) == 0:
                    allPrices.append((i, supportPrice))
            elif resistantPrice != 0:
                if np.sum([abs(resistantPrice-x) < mean for x in allPrices]) == 0:
                    allPrices.append((i, resistantPrice))

        sr_lines = []
        for item in allPrices:
            sr_lines.append((item[0], df.iloc[item[0]].name, item[1]))
        return sr_lines


class FilterKeyLevels:
    def __init__(self):
        self.keyLevelTolerance = float(EnvFile.Get(
            'FILTER_KEY_LEVEL_TOLERANCE', '0.02'))
        self.sa = StockAnalysis()
        self.data = self.sa.GetJson

    def filterKeyLevels(self, levels, lastPrice):
        for level in levels:
            priceLevel = level[2]
            priceDelta = abs(lastPrice * self.keyLevelTolerance)
            if lastPrice >= (priceLevel - priceDelta) and lastPrice <= (priceLevel + priceDelta):
                return True, priceLevel
        return False, 0

    def Run(self, symbol):
        try:
            _, dfDaily = AllStocks.GetDailyStockData(symbol)
            isLoaded, df = AllStocks.GetWeeklyStockData(symbol)
            if isLoaded:
                qpp = KeyLevels()
                levels = qpp.Run(df)
                lastPrice = dfDaily['Close'][0]
                isNearKeyLevel, keyPrice = self.filterKeyLevels(levels, lastPrice)
                if isNearKeyLevel:
                    print(f'filterKeyLevel.Run - near keylevel: {symbol} {lastPrice} {keyPrice}')
                self.sa.UpdateFilter(self.data, symbol, 'keylevel', isNearKeyLevel)
                self.sa.UpdateFilter(self.data, symbol, 'keylevels', keyPrice)
                return isNearKeyLevel
            else:
                return False
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def All():
        app = FilterKeyLevels()
        AllStocks.Run(app.Run, False)
        app.sa.WriteJson(app.data)


if __name__ == '__main__':
    FilterKeyLevels.All()
    print('----------------------------------- done -----------------------------------')
    # filter = FilterKeyLevels()
    # result = filter.Run('AAPL')
    # print(result)
