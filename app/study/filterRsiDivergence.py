import pandas as pd
import talib as ta
import os
from datetime import datetime
from util import AllStocks, StockAnalysis, LocalMinMax, EnvFile, TightMinMax


class rsiDivergence:
    def __init__(self):
        self.maxDays = int (EnvFile.Get('RSI_DIVERGENCE_DAYS', '14'))
        self.fMinMax = TightMinMax(tightMinMaxN=4)

    def isSameSign(self, number1: float, number2: float):
        if number1 > 0 and number2 > 0:
            return True
        if number1 < 0 and number2 < 0:
            return True
        return False

    def slope(self, x1: int, y1: float, x2: int, y2: float) -> float:
        if x2 != x1:
            m = (y2 - y1) / (x2 - x1)
            return m
        return 0

    def getRsiMinMax(self, df):
        rsiv = ta.RSI(df['Close'][::-1], timeperiod=14)
        # add column to df
        df['Rsi'] = rsiv[::-1]
        app = LocalMinMax(df if len(df) < 30 else df[0:30], colName='Rsi', tightMinMaxN=4)
        return app.Run()

    def getMinMax(self, df:pd.DataFrame):
        app = LocalMinMax(
            df if len(df) < 30 else df[0:30], colName='Close', tightMinMaxN=4)
        return app.Run()

    def highEnoughRsi(self, dfRsi:pd.DataFrame):
        for _, row in dfRsi.iterrows():
            if row.Rsi > 70 or row.Rsi < 30:
                return True
        return False
    
    def Run(self, df:pd.DataFrame):
        isFirstMinRsi, dfRsi = self.getRsiMinMax(df)
        firstRsi = dfRsi.iloc[0]['Rsi']
        if not self.highEnoughRsi(dfRsi):
            return False
        isFirstMinClose, dfClose = self.getMinMax(df)
        date1 = datetime.strptime(dfRsi.iloc[0].Date.split('T')[0], '%Y-%m-%d')
        date2 = datetime.strptime(
            dfClose.iloc[0].Date.split('T')[0], '%Y-%m-%d')
        delta = date1 - date2
        print(delta.days)
        if self.maxDays >= abs(delta.days):
            if len(dfRsi) >= 3 and len(dfClose) >= 3:
                m1 = self.slope(0, dfRsi.iloc[2].Rsi, 1, dfRsi.iloc[0].Rsi)
                m2 = self.slope(0, dfClose.iloc[2].Close, 1, dfClose.iloc[0].Close)
                if not self.isSameSign(m1, m2):
                    return True
        return False


# class rsiDivergenceBackup:
#     def __init__(self):
#         self.maxDays = int (EnvFile.Get('RSI_DIVERGENCE_DAYS', '14'))

#     def getRsiMinmax(self, df):
#         rsiv = ta.RSI(df['Close'][::-1], timeperiod=14)
#         # add column to df
#         df['Rsi'] = rsiv[::-1]
#         app = LocalMinMax(df, colName = 'Rsi', tightMinMaxN=4)
#         return app.Run()

#     @staticmethod
#     def days_between(d1, d2):
#         d1 = datetime.strptime(d1.iloc[0].split('T')[0], "%Y-%m-%d")
#         d2 = datetime.strptime(d2.iloc[0].split('T')[0], "%Y-%m-%d")
#         return abs((d2 - d1).days)

#     @staticmethod
#     def getFrame(df, oneDate):
#         return df.loc[df['Date']==oneDate]

#     @staticmethod
#     def getSlope(one, two, column):
#         days = rsiDivergence.days_between(one['Date'], two['Date'])
#         slope = (two[column].iloc[0] - one[column].iloc[0]) / days
#         return slope, days

#     @staticmethod
#     def getMinAndMax(df, dfRsiMinMax, isFirstMin):
#         isItemMin = isFirstMin
#         mins = []
#         maxs = []
#         for ix, row in dfRsiMinMax.iterrows():
#             item = rsiDivergence.getFrame(df, row['Date'])
#             data = { 'Close': item['Close'], 'Rsi': item['Rsi'], 'Date': item['Date'] }
#             if isItemMin:
#                 mins.append(data)
#             else:
#                 maxs.append(data)
#             isItemMin = not isItemMin
#         return mins, maxs

#     def getTwoPoints(minmaxs, maxDays, isMin = None, isGrabLastOne=None):
#         isMin = True if isMin else False
#         isGrabLastOne = True if isGrabLastOne else False
#         firstPt = minmaxs[0]
#         secondPt = None
#         for minmax in minmaxs:
#             days = rsiDivergence.days_between(firstPt['Date'], minmax['Date'])
#             if days == 0:
#                 continue
#             elif secondPt is None:
#                 secondPt = minmax
#                 if isGrabLastOne:
#                     return firstPt, secondPt
#             elif days <= maxDays:
#                 if (isMin and minmax['Rsi'] < secondPt['Rsi']):
#                     secondPt = minmax
#                 elif (not isMin and minmax['Rsi'] > secondPt['Rsi']):
#                     secondPt = minmax
#         return firstPt, secondPt

#     def isMinDivergence(firstMin, secondMin, isMin = None):
#         isMin = True if isMin else False
#         slopeRsi, _ = rsiDivergence.getSlope(firstMin, secondMin, 'Rsi')
#         slopeClose, _ = rsiDivergence.getSlope(firstMin, secondMin, 'Close')
#         if isMin and slopeRsi > 0 and slopeClose < 0:
#             return True
#         if not isMin and slopeRsi < 0 and slopeClose > 0:
#             return True
#         return False

#     def Run(self, df):
#         maxDays = self.maxDays
#         isFirstMin, dfRsiMinMax = self.getRsiMinmax(df)
#         mins, maxs = rsiDivergence.getMinAndMax(df, dfRsiMinMax, isFirstMin)

#         firstRsi = dfRsiMinMax.iloc[0]['Rsi']
#         if firstRsi < 70 and firstRsi > 30:
#             return False
#         if firstRsi < 50:
#             firstMin, secondMin = rsiDivergence.getTwoPoints(mins, maxDays, True, False)
#             isDivergence = rsiDivergence.isMinDivergence(firstMin, secondMin)
#             if isDivergence:
#                 return True    
#             firstMin, secondMin = rsiDivergence.getTwoPoints(mins, maxDays, True, True)
#             isDivergence = rsiDivergence.isMinDivergence(firstMin, secondMin, True)
#             if isDivergence:
#                 return True
#         else:
#             firstMax, secondMax = rsiDivergence.getTwoPoints(maxs, maxDays, False, False)
#             isDivergence = rsiDivergence.isMinDivergence(firstMax, secondMax)
#             if isDivergence:
#                 return True    
#             firstMax, secondMax = rsiDivergence.getTwoPoints(maxs, maxDays, False, True)
#             isDivergence = rsiDivergence.isMinDivergence(firstMax, secondMax, False)
#             if isDivergence:
#                 return True
#         return False


class FilterRsiDivergence:
    def __init__(self):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        self.filter = rsiDivergence()

    def Run(self, symbol):
        isAssigned = False
        try:
            isLoaded, dfDaily = AllStocks.GetDailyStockData(symbol)
            if isLoaded:
                isDivergence = self.filter.Run(dfDaily)
                self.sa.UpdateFilter(self.jsonData, symbol, 'rsi', isDivergence)
            else:
                self.sa.UpdateFilter(self.jsonData, symbol, 'rsi', False)
        except Exception as e:
            print(f'FilterRsiDivergence - {e}')
            self.sa.UpdateFilter(self.jsonData, symbol, 'rsi', False)

    @staticmethod
    def All():
        filter = FilterRsiDivergence()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.jsonData)
