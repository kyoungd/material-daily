from threading import Thread
import logging
from dbase import MarketDataDb, SynchronizeMarketData
from util import AlpacaAccess, RedisTimeFrame
from .alpacaDally import AlpacaDaily
from .alpacaHistorical import AlpacaHistorical
from util import RedisTimeFrame


class AlpacaCrypto(AlpacaDaily):

    def __init__(self, startdate=None, enddate=None, alpacaObject=None, symbolFile=None):
        symbolFile = './data/crypto.csv' if symbolFile is None else symbolFile
        super().__init__(startdate=None, enddate=None, alpacaObject=None, symbolFile=symbolFile)
        self.datatype = 'crypto'
    #
    # override getDataLine to use CryptoPrices instead of HistroicalPrices
    #
    def getDataLine(self, app: AlpacaHistorical, symbol:str, db: MarketDataDb):
        try:
            logging.info(f'AlpacaCrypto.getDataLine: {symbol}')
            timeframe = RedisTimeFrame.DAILY
            if self.startdate is not None and self.enddate is not None:
                data = app.CryptoPrices(
                    symbol, timeframe, starttime=self.startdate, endtime=self.enddate)
            else:
                data = app.CryptoPrices(symbol, timeframe)
            sync = SynchronizeMarketData(data, isCrypto=True)
            mdata = sync.Run()
            db.WriteMarket(symbol, mdata, datatype=self.datatype,
                           timeframe=timeframe)
        except Exception as e:
            logging.error(f'AlpacaCrypto.getDataLine: {symbol} - {e}')
            print(e)

    def Run(self):
        logging.info('Running AlpacaCrypto.Run')
        symbols = self.getSymbolFile()
        symbolHistoricals, symbolSnapshots = self.db.StockSymbols(
            symbols, self.datatype)

        if symbolHistoricals:
            self.getHistorical(symbolHistoricals)
        # there is no snapshot for crypto.  just write historical data
        if symbolSnapshots:
            self.getHistorical(symbolSnapshots)

    @staticmethod
    def All():
        app = AlpacaCrypto()
        app.Run()
