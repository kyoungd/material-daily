import json
import threading
from threading import Thread
import time
import logging
from datetime import datetime, timedelta
from enum import Enum
import requests
from alpaca_trade_api.rest import REST, TimeFrame
from .yahooFin import YahooFin
from util import AlpacaAccess, RedisTimeFrame

custom_header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
response = requests.get('https://www.dev2qa.com', headers=custom_header)


class TimePeriod(Enum):
    REALTIME = "0"
    Min1 = "1Min"
    Min5 = "5Min"
    Min10 = "10Min"
    Min15 = "15Min"
    Min30 = "30Min"
    Hour = "Hour"
    Hour4 = "4Hour"
    Day = "Day"
    Week = "Week"


class AlpacaHistorical:
    ALPACA_URL = 'https://data.alpaca.markets/v2/stocks/%s/bars?start=%s&end=%s&timeframe=%s'
    CRYPTO_URL = 'https://data.alpaca.markets/v1beta1/crypto/%sUSD/bars?start=%s&end=%s&timeframe=%s&exchanges=CBSE'
    CsvHeader = "Date, Open, High, Low, Close, Adj Close, Volume"
    conn: REST = None

    def __init__(self):
        self.custom_header = AlpacaAccess.CustomHeader()

    def timeframe_start(self, timeframe):
        switcher = {
            RedisTimeFrame.REALTIME: datetime.now() - timedelta(minutes=30),
            RedisTimeFrame.MIN1: datetime.now() - timedelta(minutes=30),
            RedisTimeFrame.MIN2: datetime.now() - timedelta(minutes=60),
            RedisTimeFrame.MIN5: datetime.now() - timedelta(minutes=150),
            RedisTimeFrame.MIN30: datetime.now() - timedelta(days=2),
            RedisTimeFrame.HOUR: datetime.now() - timedelta(days=28),
            RedisTimeFrame.DAILY: datetime.now() - timedelta(days=360),
            RedisTimeFrame.WEEKLY: datetime.now() - timedelta(days=1080),
        }
        dt = switcher.get(timeframe, datetime.now())
        date_string = dt.isoformat('T') + 'Z'
        return date_string
        # return "2021-02-08"

    def timeframe_end(self, timeframe):
        dt = datetime.now()
        date_string = dt.isoformat('T') + 'Z'
        return date_string
        # return "2021-02-10"

    def columnName(self, datatype):
        switcher = {
            "open": "o",
            "close": "c",
            "high": "h",
            "low": "l",
            "volume": "v"
        }
        return switcher.get(datatype, 'c')

    def reverseArray(self, arrayData):
        return arrayData[::-1]

    def column(self, matrix, i):
        return [row[i] for row in matrix]

    def adjustPrices(self, data, datatype):
        result = json.loads(data.text)
        bars = result['bars']
        if bars is None:
            return []
        data = self.reverseArray(bars)
        if datatype is None:
            return data
        else:
            dtype = self.columnName(datatype)
            prices = self.column(data, dtype)
            return prices

    def HistoricalPrices(self, symbol, timeframe, datatype=None, starttime=None, endtime=None):
        start = self.timeframe_start(
            timeframe) if starttime is None else starttime
        end = self.timeframe_end(timeframe) if endtime is None else endtime
        tf = '1Min' if RedisTimeFrame.REALTIME == timeframe else timeframe
        url = AlpacaHistorical.ALPACA_URL % (
            symbol, start, end, tf)
        data = requests.get(url, headers=self.custom_header)
        bars = self.adjustPrices(data, datatype)
        return bars

    def CryptoPrices(self, symbol, timeframe, datatype=None, starttime=None, endtime=None):
        start = self.timeframe_start(
            timeframe) if starttime is None else starttime
        end = self.timeframe_end(timeframe) if endtime is None else endtime
        tf = '1Min' if RedisTimeFrame.REALTIME == timeframe else timeframe
        url = AlpacaHistorical.CRYPTO_URL % (
            symbol, start, end, tf)
        data = requests.get(url, headers=self.custom_header)
        bars = self.adjustPrices(data, datatype)
        return bars

    def CommodityPrices(self, symbol, timeframe, datatype=None, starttime=None, endtime=None):
        # logging.info(f'AlpacaHistorical.CommodityPrices {symbol} {timeframe} {datatype}')
        bars = YahooFin.HistoricalPrices(symbol)
        return bars

    def WriteToFile(self, symbol, data):
        text = "{}, {}, {}, {}, {}, {}, {}"
        historicalText = [text.format(x['t'], x['o'], x['h'], x['l'], x['c'], x['c'], x['v'])
                          for x in data]
        filename = './data/stocks/' + symbol + '.csv'
        with open(filename, 'w') as f:
            f.write(self.CsvHeader + '\n')
            for line in historicalText:
                f.write(line + '\n')


class AlpacaHistoricalData(AlpacaHistorical):
    def __init__(self, startdate=None, enddate=None):
        super().__init__()
        self.startdate = startdate
        self.enddate = enddate

    def getDataLine(self, app, line, fw):
        try:
            timeframe = RedisTimeFrame.DAILY
            symbol = line.split(',')[0]
            if self.startdate is not None and self.enddate is not None:
                data = self.HistoricalPrices(symbol, timeframe, starttime=self.startdate, endtime=self.enddate)
            else:
                data = app.HistoricalPrices(symbol, timeframe)
            app.WriteToFile(symbol, data)
            fw.write(line)
        except Exception as e:
            logging.error(f'AlpacaHistoricalData.getDataLine {symbol} - {e}')
            print(e)

    def Run(self, filename=None, isDebug=False):
        # logging.info('AlpacaHistoricalData.Run')
        filename = './data/symbols.csv' if filename == None else filename
        with open(filename, 'r') as f:
            lines = f.readlines()
            # print(lines)
        logging.error(f'AlpacaHistoricalData.Run - lines {len(lines)}')
        with open(filename, "w") as fw:
            fw.write(self.CsvHeader + '\n')
            timeframe = RedisTimeFrame.DAILY
            app = AlpacaHistorical()
            lineCount = 0
            for line in lines:
                if (isDebug):
                    lineCount += 1
                    print(lineCount)
                Thread(target=self.getDataLine, args=(app, line, fw)).start()
                while (threading.activeCount() > 10):
                    time.sleep(2)
            if threading.activeCount() > 0:
                time.sleep(2)

    @staticmethod
    def All(startdate=None, enddate=None):
        if (startdate is None and enddate is None):
            app = AlpacaHistoricalData()
            app.Run(isDebug=True)
        elif (startdate and enddate is None):
            # convert string to datetime
            enddate = datetime.strptime(startdate, '%Y-%m-%d')
            startdate = enddate - timedelta(days=400)
            app = AlpacaHistoricalData(startdate, enddate)
            app.Run(isDebug=True)
        elif (startdate and enddate):
            enddate = datetime.strptime(enddate, '%Y-%m-%d')
            startdate = datetime.strptime(startdate, '%Y-%m-%d')
            app = AlpacaHistoricalData(startdate, enddate)
            app.Run(isDebug=True)

if __name__ == "__main__":

    AlpacaHistoricalData.All()
    # timeframe = RedisTimeFrame.DAILY
    # symbol = "AAPL"
    # app = AlpacaHistorical()
    # data = app.HistoricalPrices(symbol, timeframe)
    # app.WriteToFile(symbol, data)
    #
    #
    print('done')
