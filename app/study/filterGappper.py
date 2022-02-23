import pandas as pd
import pandas as pd
import numpy as np
import os
from datetime import date
from util import AllStocks, StockAnalysis, EnvFile


class FilterGapper:
    def __init__(self):
        self.gapPercent = float(EnvFile.Get('FILTER_OVERNIGHT_GAP_PERCENT', '0.08'))
        self.gapMargin = float(EnvFile.Get('FILTER_OVERNIGHT_GAP_MARGIN', '0.7'))
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson

    def filterOn(self, tp:pd.DataFrame):
        gapUp = []
        gapDown = []
        Closes = tp.Close.to_numpy()
        arr = np.concatenate((Closes[1:], Closes[:1]), axis=0)
        tp['Closes'] = arr
        for idx, row in tp.iterrows():
            if idx < len(tp) - 1:
                gap = row['Closes'] - row['Open']
                if abs(gap) > row['Closes'] * self.gapPercent:
                    if row['Open'] > row['Closes']:
                        gapUp.append({'Date': row['Date'], 'Open': row['Open'], 'Closes': row['Closes']})
                    else:
                        gapDown.append({'Date': row['Date'], 'Open': row['Open'], 'Closes': row['Closes']})
        return gapUp, gapDown

    def gapUpMinMax(self, gap:dict):
        priceMovement = abs(gap['Open'] - gap['Closes']) * self.gapMargin
        minPrice = gap['Open'] - priceMovement
        maxPrice = gap['Open'] * (1 + self.gapPercent)
        return minPrice, maxPrice

    def gapUpNearClose(self, gaps:list, price:float):
        filtered = []
        for gap in gaps:
            minPrice, maxPrice = self.gapUpMinMax(gap)
            if price >= minPrice and price <= maxPrice:
                filtered.append(gap)
        return filtered

    def gapDownMinMax(self, gap:dict):
        priceMovement = abs(gap['Open'] - gap['Closes']) * self.gapMargin
        minPrice = gap['Open'] * (1 - self.gapPercent)
        maxPrice = gap['Open'] + priceMovement
        return minPrice, maxPrice

    def gapDownNearClose(self, gaps:list, price:float):
        filtered = []
        for gap in gaps:
            minPrice, maxPrice = self.gapDownMinMax(gap)
            if price >= minPrice and price <= maxPrice:
                filtered.append(gap)
        return filtered

    def gapUpPriceMovementCheck(self, gaps:list, tp:pd.DataFrame):
        filtered = []
        for gap in gaps:
            minPrice, _ = self.gapDownMinMax(gap)
            isGapFilled = False
            for idx, row in tp.iterrows():
                if row['Date'] >= gap['Date'] and row['Low'] <= minPrice:
                    isGapFilled = True
            if not isGapFilled:
                filtered.append(gap)
        return filtered

    def gapDownPriceMovementCheck(self, gaps:list, tp:pd.DataFrame):
        filtered:list = []
        for gap in gaps:
            _, maxPrice = self.gapDownMinMax(gap)
            isGapFilled = False
            for idx, row in tp.iterrows():
                if row['Date'] >= gap['Date'] and row['High'] >= maxPrice:
                    isGapFilled = True
            if not isGapFilled:
                filtered.append(gap)
        return filtered

    def overnightGapperLogic(self, tp:pd.DataFrame):
        gapUp, gapDown = self.filterOn(tp)
        gapUp = self.gapUpNearClose(gapUp, tp.Close.iloc[0])
        gapUp = self.gapUpPriceMovementCheck(gapUp, tp)
        gapDown = self.gapDownNearClose(gapDown, tp.Close.iloc[0])
        gapDown = self.gapDownPriceMovementCheck(gapDown, tp)
        # merge array gapUp and gapDown into one array
        return gapUp + gapDown
        # gaps = []
        # gaps.append(gapUp)
        # gaps.append(gapDown)
        # return gaps

    def Run(self, symbol:str):
        isLoaded, tp = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                gaps = self.overnightGapperLogic(tp)
                self.sa.UpdateFilter(self.jsonData, symbol, 'gap',
                                     True if len(gaps) > 0 else False)
                self.sa.UpdateFilter(self.jsonData, symbol, 'gaps', gaps)
            except Exception as e:
                print(e)
        return isLoaded

    @staticmethod
    def All():
        filter = FilterGapper()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.jsonData)

if __name__ == '__main__':
    FilterGapper.All()
    print('---------- done ----------')
