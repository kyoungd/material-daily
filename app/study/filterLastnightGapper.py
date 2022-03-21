from alpaca_trade_api.rest import REST
import json
import logging
import os
from util import AlpacaAccess, StockAnalysis, EnvFile, AllStocks

class overnightGapper:
    conn: REST = None

    def __init__(self):
        self.sa = StockAnalysis()
        self.data = self.sa.GetJson

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
                # price1 = snapshot['close']
                price1 = snapshots[symbol]['dailyBar']['c']
                price2 = snapshots[symbol]['minuteBar']['c']
                nightGap = abs(price2 - price1) / min(price1, price2)
                # print('{} {} {} {}'.format(symbol, price1, price2, nightGap))
                self.sa.UpdateFilter(
                    self.data, symbol, 'ogap', round(nightGap*100))
            except Exception as e:
                print(
                    f'filterLastnightGapper.getSnapshotAtMarketOpen(). ERROR: {symbol} - {e}')
                logging.error(
                    f'filterLastnightGapper.getSnapshotAtMarketOpen(). ERROR: {symbol} - {e}')
                self.sa.UpdateFilter(self.data, symbol, 'ogap', 0)

class LastNightGapper:
    def __init__(self, isDebug=None):
        self.og = overnightGapper()
        self.isDebug = True if isDebug else False
        self.func = self.og.getSnapshotAtMarketOpen

    def allAvailableSymbols(self):
        symbols = []
        AllStocks.Run(symbols.add)
        return symbols

    def symbolLoop(self, func, isDebug:bool):
        allSymbols = []
        AllStocks.Run(allSymbols.append)
        lineCount = 0
        symbols = set()
        for symbol in allSymbols:
            lineCount += 1
            symbols.add(symbol)
            if (lineCount % 20 == 0):
                self.func(symbols)
                symbols = set()
                if (isDebug):
                    print(f'filterLastnightGaopper.symbolLoop() - {lineCount}')
        if (len(symbols) > 0):
            self.func(symbols)

    def Run(self):
        self.symbolLoop(self.func, self.isDebug)

    @staticmethod
    def All():
        app = LastNightGapper(isDebug=True)
        app.Run()
        app.og.sa.WriteJson(app.og.data)


if __name__ == "__main__":
    # timeframe = RedisTimeFrame.DAILY
    # symbol = "AAPL"
    # app = LastNightGapper()
    # data = app.HistoricalPrices(symbol, timeframe)
    # app.WriteToFile(symbol, data)
    #
    LastNightGapper.All()
