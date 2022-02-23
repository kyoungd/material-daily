
from alpaca_trade_api.rest import REST, TimeFrame
from enum import Enum
import requests
from dbase import MarketDataDb
from util import AlpacaAccess, JsonFavorite
from .alpacaSnapshot import AlpacaSnapshots
import logging
import json
import os

class AlpacaSnapshotDaily(AlpacaSnapshots):
    def __init__(self, symbols, datatype, favorites=None, minPrice=None, maxPrice=None, minVolume=None, maxVolume=None):
        super().__init__(favorites, minPrice, maxPrice, minVolume, maxVolume)
        self.datatype = datatype
        self.symbols = symbols
        self.db = MarketDataDb()

    def AppendSnapshots(self, dicts, datatype):
        for key in dicts:
            self.db.AppendMarket(key, dicts[key], datatype=datatype)

    def getSnapshot(self, symbols: set, dicts: dict):
        data = self.HistoricalSnapshots(symbols)
        if (data.status_code == 422):
            removeSymbols = json.loads(data.text)['message'].split(':')[1]
            rejectedSymbols = set()
            for symbol in removeSymbols.strip().split(','):
                rejectedSymbols.add(symbol)
                dicts.pop(symbol)
            symbolList = symbols.difference(rejectedSymbols)
            data = self.HistoricalSnapshots(symbolList)
        snapshots = json.loads(data.text)
        for symbol in snapshots:
            try:
                dicts[symbol] = snapshots[symbol]['dailyBar']
            except Exception as e:
                try:
                    logging.error(
                        f'AlpacaSnapshotDaily.getSnapshotForDaily(). ERROR: {e}')
                    print('getSnapshot(). ERROR: {} {} {}'.format(
                        symbol, str(e), data.status_code))
                    print(snapshots[symbol])
                    dicts.pop(symbol)
                except Exception as e:
                    pass

    def Run(self, symbols=None):
        symbols = self.symbols  if symbols is None else symbols
        try:
            dicts = {}
            for symbol in symbols:
                dicts[symbol] = ''
            lineCount = 0
            symbolSet = set()
            for symbol in symbols:
                symbolSet.add(symbol)
                lineCount += 1
                if (lineCount % 100 == 0):
                    self.getSnapshot(symbolSet, dicts)
                    symbolSet.clear()
                    print(f'alpacaSnapshotDaily.Run - {lineCount}')
            if len(symbolSet) > 0:
                self.getSnapshot(symbolSet, dicts)
            self.AppendSnapshots(dicts, self.datatype)
        except Exception as e:
            logging.error(f'AlpacaSnapshotDaily.RunDaily(). ERROR: {e}')
            print('AlpacaSnapshotDaily.Run(). ERROR: {}'.format(str(e)))
            return False

    @staticmethod
    def All(symbols):
        isDebug = True if isDebug else False
        app = AlpacaSnapshotDaily(symbols)
        app.Run()
        print('done - AlpacaSnapshotDaily.py')


if __name__ == "__main__":
    # timeframe = RedisTimeFrame.DAILY
    # symbol = "AAPL"
    # app = AlpacaSnapshots()
    # data = app.HistoricalPrices(symbol, timeframe)
    # app.WriteToFile(symbol, data)
    #
    # AlpacaAccess.All(True)
    #
    print('done')
