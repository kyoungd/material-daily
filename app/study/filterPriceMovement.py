import pandas as pd
import pandas as pd
import numpy as np
import logging
from util import AllStocks, StockAnalysis, EnvFile
from dbase import MarketDataDb
from datetime import datetime

class FilterPriceMovement:
    def __init__(self, isSaveToDb: bool = None):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        self.db = MarketDataDb()
        self.isSaveToDb = True if isSaveToDb == None else isSaveToDb 
        self.priceMultiplierFactor = float(EnvFile.Get('FILTER_PRICE_MULTIPLIER', '0.02'))

    def priceMultiplier(self, price):
        return 1 + (price - 3) * self.priceMultiplierFactor

    def priceMovement(self, df: pd.DataFrame, period: int = 30):
        try:
            priceMove = 0 
            for index, row in df.iterrows():
                if index >= period:
                    return round(priceMove / period * 100, 2)
                close = row['Close']
                priceDiff = row['High'] - row['Low']
                pricePercent = priceDiff / close
                priceMove += pricePercent * self.priceMultiplier(close)
            return round(priceMove / len(df.index) * 100, 2)
        except Exception as e:
            logging.error(f'FilterPriceMovement.priceMovement: {e}')
            print(f'FilterPriceMovement.priceMovement: {e}')
            return 0

    def writeToDb(self, symbol: str, df: pd.DataFrame):
        close = df.iloc[0]['Close']
        volume = df.iloc[0]['Volume']
        if close < 3 or close > 100 or volume < 500000:
            price01 = 0
            price03 = 0
            price30 = 0
        else:
            price01 = self.priceMovement(df, 1)
            price03 = self.priceMovement(df, 3)
            price30 = self.priceMovement(df, 30)
        time_now = datetime.now()
        query = """UPDATE public.market_data SET volatility01=%s, volatility03=%s, volatility30=%s, updated_at=%s, close=%s, volume=%s WHERE symbol=%s AND timeframe=%s AND NOT is_deleted"""
        params = (price01, price03, price30, time_now, float(close), int(volume), symbol, '1Day')
        self.db.UpdateQuery(query, params)

    def Run(self, symbol: str):
        isLoaded, df = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                value = self.priceMovement(df)
                self.sa.UpdateFilter(self.jsonData, symbol, 'pm', value)
                if self.isSaveToDb:
                    self.writeToDb(symbol, df)
            except Exception as e:
                logging.error(f'FilterPriceMovement.Run: {symbol} - {e}')
                print(f'FilterPriceMovement.Run: {symbol} - {e}')
                self.sa.UpdateFilter(self.jsonData, symbol, 'pm', 0)
        return isLoaded

    @staticmethod
    def All(isSaveToDb: bool = None):
        isSaveToDb = False if isSaveToDb is None else isSaveToDb
        filter = FilterPriceMovement(True)
        AllStocks.RunFromDbAll(filter.Run)
        filter.sa.WriteJson(filter.jsonData)
