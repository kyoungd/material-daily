import pandas as pd
import talib as ta
import os
from datetime import datetime
from util import AllStocks, StockAnalysis, LocalMinMax, EnvFile

class rsiDivergence:
    def __init__(self):
        self.maxDays = int (EnvFile.Get('RSI_DIVERGENCE_DAYS', '14'))

    def getRsiMinmax(self, df):
        rsiv = ta.RSI(df['Close'][::-1], timeperiod=14)
        # add column to df
        df['Rsi'] = rsiv[::-1]
        app = LocalMinMax(df, colName = 'Rsi')
        return app.Run()

    @staticmethod
    def days_between(d1, d2):
        d1 = datetime.strptime(d1.iloc[0].split('T')[0], "%Y-%m-%d")
        d2 = datetime.strptime(d2.iloc[0].split('T')[0], "%Y-%m-%d")
        return abs((d2 - d1).days)

    @staticmethod
    def getFrame(df, oneDate):
        return df.loc[df['Date']==oneDate]

    @staticmethod
    def getSlope(one, two, column):
        days = rsiDivergence.days_between(one['Date'], two['Date'])
        slope = (two[column].iloc[0] - one[column].iloc[0]) / days
        return slope, days

    @staticmethod
    def getMinAndMax(df, dfRsiMinMax, isFirstMin):
        isItemMin = isFirstMin
        mins = []
        maxs = []
        for ix, row in dfRsiMinMax.iterrows():
            item = rsiDivergence.getFrame(df, row['Date'])
            data = { 'Close': item['Close'], 'Rsi': item['Rsi'], 'Date': item['Date'] }
            if isItemMin:
                mins.append(data)
            else:
                maxs.append(data)
            isItemMin = not isItemMin
        return mins, maxs

    def getTwoPoints(minmaxs, maxDays, isMin = None, isGrabLastOne=None):
        isMin = True if isMin else False
        isGrabLastOne = True if isGrabLastOne else False
        firstPt = minmaxs[0]
        secondPt = None
        for minmax in minmaxs:
            days = rsiDivergence.days_between(firstPt['Date'], minmax['Date'])
            if days == 0:
                continue
            elif secondPt is None:
                secondPt = minmax
                if isGrabLastOne:
                    return firstPt, secondPt
            elif days <= maxDays:
                if (isMin and minmax['Rsi'] < secondPt['Rsi']):
                    secondPt = minmax
                elif (not isMin and minmax['Rsi'] > secondPt['Rsi']):
                    secondPt = minmax
        return firstPt, secondPt

    def isMinDivergence(firstMin, secondMin, isMin = None):
        isMin = True if isMin else False
        slopeRsi, _ = rsiDivergence.getSlope(firstMin, secondMin, 'Rsi')
        slopeClose, _ = rsiDivergence.getSlope(firstMin, secondMin, 'Close')
        if isMin and slopeRsi > 0 and slopeClose < 0:
            return True
        if not isMin and slopeRsi < 0 and slopeClose > 0:
            return True
        return False

    def Run(self, df):
        maxDays = self.maxDays
        isFirstMin, dfRsiMinMax = self.getRsiMinmax(df)
        mins, maxs = rsiDivergence.getMinAndMax(df, dfRsiMinMax, isFirstMin)

        firstRsi = dfRsiMinMax.iloc[0]['Rsi']
        if firstRsi < 70 and firstRsi > 30:
            return False
        if firstRsi < 50:
            firstMin, secondMin = rsiDivergence.getTwoPoints(mins, maxDays, True, False)
            isDivergence = rsiDivergence.isMinDivergence(firstMin, secondMin)
            if isDivergence:
                return True    
            firstMin, secondMin = rsiDivergence.getTwoPoints(mins, maxDays, True, True)
            isDivergence = rsiDivergence.isMinDivergence(firstMin, secondMin, True)
            if isDivergence:
                return True
        else:
            firstMax, secondMax = rsiDivergence.getTwoPoints(maxs, maxDays, False, False)
            isDivergence = rsiDivergence.isMinDivergence(firstMax, secondMax)
            if isDivergence:
                return True    
            firstMax, secondMax = rsiDivergence.getTwoPoints(maxs, maxDays, False, True)
            isDivergence = rsiDivergence.isMinDivergence(firstMax, secondMax, False)
            if isDivergence:
                return True
        return False


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
