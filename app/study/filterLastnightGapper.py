from alpaca_trade_api.rest import REST
import json
import os
from util import AlpacaAccess, StockAnalysis, EnvFile
from dbase import SecDb

class overnightGapper:
    conn: REST = None

    def __init__(self):
        self.sa = StockAnalysis()
        self.data = self.sa.GetJson
        self.db = SecDb()

    def getLastNightGapper(self, price1, price2):
        priceMin = float(EnvFile.Get('OG_MIN_PRICE', '0.30'))
        percentMin = float(EnvFile.Get('OG_MIN_PERCENT', '0.05'))
        priceMoveValue = abs(price2 - price1)
        priceMovePercent = priceMoveValue / price1
        return round(priceMovePercent * 100)

    def getSnapshotFromApi(self, symbols):
        data = AlpacaAccess.HistoricalSnapshots(symbols)
        if (data.status_code == 422):
            removeSymbols = json.loads(data.text)['message'].split(':')[1]
            rejectedSymbols = set()
            for symbol in removeSymbols.strip().split(','):
                rejectedSymbols.add(symbol)
            symbolList = symbols.difference(rejectedSymbols)
            data = AlpacaAccess.HistoricalSnapshots(symbolList)
        snapshots = json.loads(data.text)
        return snapshots

    def getSnapshotAtMarketOpen(self, symbols):
        snapshots = self.getSnapshotFromApi(symbols)
        for symbol in snapshots:
            try:
                isOk, snapshot = self.db.GetLastDaily(symbol)
                if (isOk):
                    # price1 = snapshot['close']
                    price1 = snapshots[symbol]['dailyBar']['c']
                    price2 = snapshots[symbol]['minuteBar']['c']
                    nightGap = self.getLastNightGapper(
                        price1, price2)
                    # print('{} {} {} {}'.format(symbol, price1, price2, nightGap))
                    self.sa.UpdateFilter(
                        self.data, symbol, 'ogap', nightGap)
                else:
                    self.sa.UpdateFilter(
                        self.data, symbol, 'ogap', 0)
            except Exception as e:
                try:
                    print(
                        'filterLastnightGapper.getSnapshotAtMarketClose(). ERROR: ' + symbol + ': ' + str(e))
                    self.sa.UpdateFilter(self.data, symbol, 'ogap', 0)
                except Exception as e:
                    print(e)

    def getSnapshotAtMarketClose(self, symbols):
        snapshots = self.getSnapshotFromApi(symbols)
        for symbol in snapshots:
            try:
                price2 = snapshots[symbol]['minuteBar']['c']
                self.db.SetLastDaily(symbol, price2)
            except Exception as e:
                try:
                    print('filterLastnigthGapper.getSnapshotAtMarketOpen(). ERROR: ' +
                          symbol + ': ' + str(e))
                except Exception as e:
                    print(e)
                self.db.SetLastDaily(symbol, 0)

class LastNightGapper:
    def __init__(self, isMarketClose, isDebug=None):
        self.og = overnightGapper()
        self.isDebug = True if isDebug else False
        self.func = self.og.getSnapshotAtMarketClose if isMarketClose else self.og.getSnapshotAtMarketOpen

    def symbolLoop(self, func, isDebug:bool):
        lineCount = 0
        symbols = set()
        for symbol in self.og.data:
            lineCount += 1
            symbols.add(symbol)
            if (lineCount % 20 == 0):
                self.func(symbols)
            if (isDebug and lineCount % 20 == 0):
                print(lineCount)
        self.func(symbols)

    def Run(self):
        self.symbolLoop(self.func, self.isDebug)

    @staticmethod
    def All(isMarketClose:bool):
        app = LastNightGapper(isMarketClose, isDebug=True)
        app.Run()
        if not isMarketClose:
            app.og.sa.WriteJson(app.og.data)


if __name__ == "__main__":
    # timeframe = RedisTimeFrame.DAILY
    # symbol = "AAPL"
    # app = LastNightGapper()
    # data = app.HistoricalPrices(symbol, timeframe)
    # app.WriteToFile(symbol, data)
    #
    LastNightGapper.All(True)
