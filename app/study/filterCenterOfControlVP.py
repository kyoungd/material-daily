import json
import logging
import pandas as pd
from util import StockAnalysis, AllStocks, EnvFile
from alpaca import AlpacaHistorical, AlpacaSnapshots
from dbase import MarketDataDb
from datetime import datetime, timedelta

class FilterCenterOfControlVP:
    def __init__(self):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        self.minRange = float(EnvFile.Get('VPCC_MIN_RANGE', '1'))
        self.maxRange = float(EnvFile.Get('VPCC_MAX_RANGE', '10'))
        self.vpMin = float(EnvFile.Get('VPCC_INRANGE_LOW', '0.2'))
        self.vpMax = float(EnvFile.Get('VPCC_INRANGE_HIGH', '0.8'))

    def getAllSymbols(self) -> list:
        data = self.jsonData
        symbols = []
        for key in data:
            if 'ogap' in data[key]:
                gap = data[key]['ogap']
                if self.maxRange > gap > self.minRange:
                    symbols.append({ 'symbol': key, 'og': gap })
        return symbols

    def Get1MinuteData(self, symbol:str) -> pd.DataFrame:
        isLoaded, df = AllStocks.Get1MinuteStockData(symbol)
        if isLoaded:
            return df
        else:
            return None

    def getLastMarketDate(self):
        app = AlpacaSnapshots()
        data = app.HistoricalSnapshots(['AAPL'])
        snapshots = json.loads(data.text)
        symbols = ''
        for symbol in snapshots:
            try:
                dailyBar = snapshots[symbol]['dailyBar']
                date = dailyBar['t'].split('T')[0]
                return date
            except Exception as e:
                logging.error(f'AlpacaSnapshot.getSnapshot(). ERROR: {e}')
                return None

    def getVolumeProfile(self, df:pd.DataFrame) -> dict:
        priceset:dict = {}
        for _, row in df.iterrows():
            key = round(row['c'], 2)
            priceset[key] = priceset[key] + row['v'] if key in priceset else row['v']
        dic2 = {}
        for i in sorted(priceset):
            dic2[i] = priceset[i]
        return(dic2)
        # return priceset

    def getVolumePercentile(self, vp:dict, percentile:float) -> float:
        total = sum(vp.values())
        accumulated = 0
        for key in vp:
            accumulated = accumulated + vp[key]
            if accumulated >= total * percentile:
                return key
        return 0

    def starttime(self, onedate:datetime.date):
        return onedate.strftime('%Y-%m-%d')

    def endtime(self, onedate:datetime.date):
        today = datetime.strptime(onedate, '%Y-%m-%d')
        tomorrow = today + timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')

    def Download1MinuteData(self, symbols:list):
        try:
            onedate = self.getLastMarketDate()
            stime = onedate
            etime = self.endtime(onedate)
            db = MarketDataDb()
            cur = db.conn.cursor()
            query = '''DELETE FROM public.market_data WHERE timeframe='1Min' AND NOT is_deleted'''
            cur.execute(query)
            alpa = AlpacaHistorical()
            for row in symbols:
                try:
                    data = alpa.HistoricalPrices(
                        symbol=row['symbol'], timeframe='1Min', starttime=stime, endtime=etime)
                    db.WriteMarket(row['symbol'], data, timeframe='1Min', )
                except Exception as e:
                    print(f'CenterOfControlVP.download1MinuteData() {row["symbol"]} - {e}')
                    logging.error(f'CenterOfControlVP.download1MinuteData() {row["symbol"]} - {e}')
        except Exception as e:
            print(f'CenterOfControlVP.download1MinuteData() - {e}')
            logging.error(f'CenterOfControlVP.download1MinuteData() - {e}')

    def getSnapshotCloses(self, symbolList:list) -> dict:
        symbols:set = set()
        for row in symbolList:
            symbols.add(row['symbol'])
        snapshots:list = []
        app = AlpacaSnapshots()
        app.DownloadSnapshotsAndRun(symbols, lambda s, x: snapshots.append({'symbol':s, 'data': x }))
        closes:dict = {}
        for snap in snapshots:
            key = snap['symbol']
            value = snap['data']['minuteBar']['c']
            closes[key] = value
        return closes
        
    def Run(self):
        symbols:list = self.getAllSymbols()
        closes:dict = self.getSnapshotCloses(symbols)
        for row in symbols:
            try:
                symbol = row['symbol']
                isLoaded, df = AllStocks.Get1MinuteStockData(symbol)
                price = closes[symbol]
                if isLoaded and price > 0:
                    vp = self.getVolumeProfile(df)
                    price20 = self.getVolumePercentile(vp, self.vpMin)
                    price80 = self.getVolumePercentile(vp, self.vpMax)
                    flag = (price >= price20 and price <= price80)
                    self.sa.UpdateFilter(self.jsonData, symbol, 'oc', flag)
                else:
                    self.sa.UpdateFilter(self.jsonData, symbol, 'oc', False)
            except Exception as e:
                print(f'CenterOfControlVP.Run() {row["symbol"]} - {e}')
                logging.error(f'CenterOfControlVP.Run() {row["symbol"]} - {e}')
                self.sa.UpdateFilter(self.jsonData, row['symbol'], 'oc', False)

    @staticmethod
    def All(delete1Minute=False):
        app = FilterCenterOfControlVP()
        if (delete1Minute):
            app.Download1MinuteData(app.getAllSymbols())
        app.Run()
        app.sa.WriteJson(app.jsonData)
