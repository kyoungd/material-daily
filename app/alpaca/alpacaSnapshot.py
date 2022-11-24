
from alpaca_trade_api.rest import REST, TimeFrame
from enum import Enum
import requests
from sympy import EX
from util import AlpacaAccess, JsonFavorite, EnvFile
import logging
import json
import os
import logging

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


class AlpacaSnapshots:
    ALPACA_URL = 'https://data.alpaca.markets/v2/stocks/snapshots?symbols=%s'
    conn: REST = None

    def __init__(self, favorites=None, minPrice=None, maxPrice=None, minVolume=None, maxVolume=None):
        self.custom_header = AlpacaAccess.CustomHeader()
        self.MinPrice = minPrice if minPrice is not None else int(EnvFile.Get(
            'SNAPSHOT_MIN_PRICE', '3'))
        self.MaxPrice = maxPrice if maxPrice is not None else int(EnvFile.Get(
            'SNAPSHOT_MAX_PRICE', '25'))
        self.MinVolume = minVolume if minVolume is not None else int(EnvFile.Get(
            'SNAPSHOT_MIN_VOLUME', '1000000'))
        self.MaxVolume = maxVolume if maxVolume is not None else int(EnvFile.Get(
            'SNAPSHOT_MAX_VOLUME', '2000000000'))
        if favorites is None:
            jsonfile = JsonFavorite()
            self.favorites = jsonfile.data
        else:
            self.favorites = favorites

    def HistoricalSnapshots(self, symbols):
        # split set into a string of symbols separated by commas
        symbolsString = ','.join(s for s in symbols)
        url = AlpacaSnapshots.ALPACA_URL % (
            symbolsString)
        snapshots = requests.get(url, headers=self.custom_header)
        return snapshots

    def inFavorites(self, symbol):
        if self.favorites is None:
            return False
        return symbol in self.favorites.keys()

    def withinPriceVolumeRange(self, price, volume, minPrice, maxPrice, minVolume, maxVolume):
        if (price < minPrice):
            return False
        elif (price > maxPrice):
            return False
        elif (volume < minVolume):
            return False
        elif (volume > maxVolume):
            return False
        else:
            return True

    def downloadSnapshotBatch(self, symbols:list):
        data = self.HistoricalSnapshots(symbols)
        if (data.status_code == 422):
            removeSymbols = json.loads(data.text)['message'].split(':')[1]
            rejectedSymbols = set()
            for symbol in removeSymbols.strip().split(','):
                rejectedSymbols.add(symbol)
            symbolList = symbols.difference(rejectedSymbols)
            data = self.HistoricalSnapshots(symbolList)
        snapshots = json.loads(data.text)
        return snapshots

    def executeSnapshots(self, data, func):
        for symbol in data:
            try:
                func(symbol, data[symbol])
            except Exception as e:
                logging.error(f'AlpacaSnapshot.executeSnapshots(). ERROR: {e}')
                print(f'AlpacaSnapshot.executeSnapshots(). ERROR: {symbol} {e}')

    def DownloadSnapshotsAndRun(self, symbols:list, func):
        try:
            batch = []
            for symbol in symbols:
                batch.append(symbol)
                if len(batch) % 20 == 0:
                    data = self.downloadSnapshotBatch(batch)
                    self.executeSnapshots(data, func)
                    batch = []
            if len(batch) > 0:
                data = self.downloadSnapshotBatch(batch)
                self.executeSnapshots(data, func)
        except Exception as e:
            logging.error(f'AlpacaSnapshot.DownloadSnapshots(). ERROR: {symbol} {e}')
            print(f'AlpacaSnapshot.DownloadSnapshots(). ERROR: {symbol} {e}')

    def getSnapshot(self, symbols, dicts):
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
        symbols = ''
        for symbol in snapshots:
            try:
                price = snapshots[symbol]['dailyBar']['c']
                volume = snapshots[symbol]['dailyBar']['v']
                if self.inFavorites(symbol):
                    pass
                elif self.withinPriceVolumeRange(price, volume, self.MinPrice, self.MaxPrice, self.MinVolume, self.MaxVolume):
                    pass
                else:
                    dicts.pop(symbol)
            except Exception as e:
                logging.error(f'AlpacaSnapshot.getSnapshot(). ERROR: {e}')
                print('getSnapshot(). ERROR: {} {} {}'.format(
                    symbol, str(e), data.status_code))
                print(snapshots[symbol])
                try:
                    dicts.pop(symbol)
                except Exception as e:
                    pass

    def Run(self, filename=None, isDebug=False):
        try:
            logging.info('AlpacaSnapshot.Run()')
            filename = './data/symbols.csv' if filename == None else filename
            with open(filename, 'r') as f:
                lines = f.readlines()
                # print(lines)
            dicts = {}
            for line in lines[1:]:
                dicts[line.split(',')[0]] = line.split(',')[1].strip('\n')
            lineCount = 0
            symbols = set()
            for line in lines[1:]:
                symbol = line.split(',')[0]
                if '.' in symbol:
                    dicts.pop(symbol)
                    print('Skipping {}'.format(symbol))
                else:
                    symbols.add(symbol)
                    lineCount += 1
                    if (lineCount % 100 == 0):
                        self.getSnapshot(symbols, dicts)
                        symbols.clear()
                        if (isDebug):
                            print(f'alpacaSnapshot.Run - {lineCount}')
            self.getSnapshot(symbols, dicts)
            with open(filename, "w") as fw:
                for key in dicts.keys():
                    content = dicts[key].strip('\n')
                    fw.write('{},{}\n'.format(key, content))
        except Exception as e:
            logging.error(f'AlpacaSnapshot.Run(). ERROR: {e}')
            print('AlpacaSnapshot.Run(). ERROR: {}'.format(str(e)))
            return False

    @staticmethod
    def All(isDebug=None):
        isDebug = True if isDebug else False
        app = AlpacaSnapshots()
        app.Run(None, isDebug)
        print('done - alpaanapshot.py')

    @staticmethod
    def LastProcessDate():
        app = AlpacaSnapshots()
        snapshots = app.downloadSnapshotBatch(['AAPL', 'MSFT'])
        for symbol in snapshots:
            try:
                datetimeStr = snapshots[symbol]['dailyBar']['t']
                dateStr = datetimeStr.split('T')[0]
                return dateStr
            except Exception as e:
                logging.error(f'AlpacaSnapshot.LastProcessDate(). ERROR: {e}')
                print('AlpacaSnapshot.LastProcessDate(). ERROR: {}'.format(str(e)))
                return None

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
