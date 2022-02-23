import json
import logging
import threading
from threading import Thread
import time
from dbase import MarketDataDb
from util import AlpacaAccess, RedisTimeFrame
from .alpacaHistorical import AlpacaHistorical
from .alpacaSnapshot import AlpacaSnapshots
from .alpacaSnapshotDaily import AlpacaSnapshotDaily
from util import RedisTimeFrame

class AlpacaDaily():

    def __init__(self, startdate=None, enddate=None, alpacaObject = None, symbolFile = None):
        self.symbolFile = './data/symbols.csv' if symbolFile is None else symbolFile
        self.alpaca = AlpacaHistorical if alpacaObject is None else alpacaObject
        self.db = MarketDataDb()
        self.startdate = startdate
        self.enddate = enddate

    def getSymbolFile(self):
        filename = self.symbolFile
        with open(filename, 'r') as f:
            lines = f.readlines()
        return lines

    def getDataLine(self, app:AlpacaHistorical, symbol, db:MarketDataDb):
        try:
            logging.info(f'AlpacaDaily.getDataLine: {symbol}')
            timeframe = RedisTimeFrame.DAILY
            if self.startdate is not None and self.enddate is not None:
                data = app.HistoricalPrices(
                    symbol, timeframe, starttime=self.startdate, endtime=self.enddate)
            else:
                data = app.HistoricalPrices(symbol, timeframe)
            db.WriteMarket(symbol, data, datatype='stock', timeframe=timeframe)
        except Exception as e:
            logging.error(f'AlpacaDaily.getDataLine: {symbol} - {e}')
            print(e)

    def getHistorical(self, symbols, isSerialRunOnly=None):
        isSerialRunOnly = False if isSerialRunOnly is None else isSerialRunOnly
        logging.info('Running AlpacaDaily.getHistorical')
        app = AlpacaHistorical()
        lineCount = 0
        for symbol in symbols:
            if isSerialRunOnly:
                self.getDataLine(app, symbol, self.db)
            else:
                lineCount += 1
                if lineCount % 100 == 0:
                    logging.info(f'{lineCount}/{len(symbols)}')
                Thread(target=self.getDataLine, args=(app, symbol, self.db)).start()
                while (threading.activeCount() > 10):
                    time.sleep(2)
        if not isSerialRunOnly and threading.activeCount() > 0:
            time.sleep(2)

    def Run(self):
        logging.info('Running AlpacaDaily.Run')
        symbols = self.getSymbolFile()
        symbolHistoricals, symbolSnapshots = self.db.StockSymbols(symbols, 'stock')
        logging.info(f' daily stocks: {len(symbolHistoricals)} historicals and {len(symbolSnapshots)} snapshots')
        if symbolHistoricals:
            self.getHistorical(symbolHistoricals)
        if symbolSnapshots:
            app = AlpacaSnapshotDaily(symbolSnapshots, datatype='stock')
            app.Run()

    @staticmethod
    def All():
        logging.info('Running AlpacaDaily()')
        app = AlpacaDaily()
        app.Run()
