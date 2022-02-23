import talib
from threading import Thread
from dbase import MarketDataDb
import pandas as pd
import numpy as np
import json
from util import PushToServer, JsonFavorite, EnvFile
import os
import logging

class CorrelateAssets():

    def __init__(self, days = None, minAtr = None):
        self.minAtr = 7.5 if minAtr is None else minAtr
        self.db = MarketDataDb()
        days = 90 if days is None else days
        if days == 45:
            self.period = 30
            self.colume = 'atr45'
            self.urlCorrelates = EnvFile.Get('CORRELATE_45_URL', '')
            self.urlInvereses = EnvFile.Get('INVERSE_45_URL', '')
            self.fileCorrelates = EnvFile.Get('CORRELATE_45_FILE', '')
            self.fileInverese = EnvFile.Get('INVERSE_45_FILE', '')
        elif days == 90:
            self.period = 60
            self.colume = 'atr90'
            self.urlCorrelates = EnvFile.Get('CORRELATE_90_URL', '')
            self.urlInvereses = EnvFile.Get('INVERSE_90_URL', '')
            self.fileCorrelates = EnvFile.Get('CORRELATE_90_FILE', '')
            self.fileInverese = EnvFile.Get('INVERSE_90_FILE', '')
        elif days == 180:
            self.period = 120
            self.colume = 'atr180'
            self.urlCorrelates = EnvFile.Get('CORRELATE_180_URL', '')
            self.urlInvereses = EnvFile.Get('INVERSE_180_URL', '')
            self.fileCorrelates = EnvFile.Get('CORRELATE_180_FILE', '')
            self.fileInverese = EnvFile.Get('INVERSE_180_FILE', '')
        else:
            self.period = 60
            self.colume = 'atr90'
            self.urlCorrelates = None
            self.urlInvereses = None
            self.fileCorrelates = None
            self.fileInverese = None

    def buildCorrelationTable(self, results):
        df = pd.DataFrame()
        lastIx = 0
        for item in results:
            symbol, data = item
            item_df = pd.DataFrame(data)
            closes = item_df.c
            closes = closes.pct_change()
            close = closes.to_numpy()[0:self.period]
            df.insert(lastIx, symbol,close)
            lastIx += 1
        return df

    def getSymbols(self):
        sql = f'SELECT symbol, data FROM public.market_data WHERE timeframe=%s AND {self.colume}>=%s AND NOT is_deleted'
        params = (MarketDataDb.DefaultTimeframe(), self.minAtr)
        return self.db.SelectQuery(sql, params)

    def cleanUpRow(self, symbol, row):
        symbolList = []
        for key in row:
            if key != symbol:
                symbolList.append({key: row[key]})
        return symbolList

    def Run(self):
        try:
            logging.info('CorrelateAssets.Run()')
            isOk, symbols = self.getSymbols()
            df = self.buildCorrelationTable(symbols)
            results = df.corr(method='pearson')
            correlates = {}
            inverses = {}
            for _, row in results.iterrows():
                correlate = row.where(lambda x: x >= 0.75).dropna()
                inverse = row.where(lambda x: x <= -0.75).dropna()
                jsonCorr = self.cleanUpRow(row.name, correlate.to_dict())
                jsonInv = self.cleanUpRow(row.name, inverse.to_dict())
                if len(jsonCorr) > 0:
                    correlates[row.name] = jsonCorr
                if len(jsonInv) > 0:
                    inverses[row.name] = jsonInv
            return correlates, inverses
            # df_correlates = pd.DataFrame(correlates)
            # df_inverses = pd.DataFrame(inverses)
            # json_correlates = df_correlates.to_json()
            # json_inverses = df_inverses.to_json()
            # return json_correlates, json_inverses
        except Exception as e:
            logging.error(f'CorrelateAssets.Run() {e}')
            return None, None
    
    def pushToServer(self, json_correlates, json_inverses):
        if self.urlCorrelates is not None:
            PushToServer(content=json_correlates, dest=self.urlCorrelates)
        if self.urlInvereses is not None:
            PushToServer(content=json_inverses, dest=self.urlInvereses)

    def pushToFile(self, json_correlates, json_inverses):
        if self.fileCorrelates is not None:
            JsonFavorite(filename=self.fileCorrelates, readJsonFile=False).WriteJson(json_correlates)
        if self.fileInverese is not None:
            JsonFavorite(filename=self.fileInverese, readJsonFile=False).WriteJson(json_inverses)
        
    @staticmethod
    def All(isSendToServer = None, days = None, minAtr = None):
        isSendToServer = False if isSendToServer is None else isSendToServer
        days = 90 if days is None else days
        minAtr = 7.5 if minAtr is None else minAtr
        app = CorrelateAssets(days=days, minAtr=minAtr)
        corrs, invs = app.Run()
        if isSendToServer:
            app.pushToServer(corrs, invs)
        else:
            app.pushToFile(corrs, invs)
        print ('done')
