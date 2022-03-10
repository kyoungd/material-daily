import requests
import json
import logging
from scipy import stats, signal
import numpy as np
import pandas as pd
from util import StockAnalysis, AllStocks
from alpaca import AlpacaHistorical, AlpacaSnapshots

class FilterVolumeProfileDailySetup:
    def __init__(self):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        lastDate = self.getLastDate()
        self.starttime = lastDate + 'T00:00:00'
        self.endtime = lastDate + 'T23:59:59'

    def getLastDate(self):
        app = AlpacaSnapshots(favorites={}, minPrice=0, maxPrice=0, minVolume=0, maxVolume=0)
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

    def HistoricalPrices(self, symbol, timeframe, datatype=None, starttime=None, endtime=None):
        start = self.startime
        end = self.endtime
        tf = '1Min'
        url = AlpacaHistorical.ALPACA_URL % (
            symbol, start, end, tf)
        data = requests.get(url, headers=self.custom_header)
        return data

    def volumeProfiles(self, df):
        df.rename(columns={'Close': 'close'}, inplace=True)
        df.rename(columns={'Volume': 'volume'}, inplace=True)
        data = df
        volume = data['volume']
        close = data['close']

        kde_factor = 0.05
        num_samples = len(df)
        kde = stats.gaussian_kde(close, weights=volume, bw_method=kde_factor)
        xr = np.linspace(close.min(), close.max(), num_samples)
        kdy = kde(xr)
        ticks_per_sample = (xr.max() - xr.min()) / num_samples

        peaks, _ = signal.find_peaks(kdy)
        pkx = xr[peaks]
        pky = kdy[peaks]

        min_prom = kdy.max() * 0.3
        peaks, peak_props = signal.find_peaks(kdy, prominence=min_prom)
        pkx = xr[peaks]
        pky = kdy[peaks]

        return pkx

    def isNearVP(self, close, vpros):
        for vpro in vpros:
            if (abs(close - vpro) / close < self.nearMargin):
                return True, vpro
        return False, 0

    def Run(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        else:
            self.symbol = symbol
        isLoaded, tp = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                price = tp.Close[0]
                volProfiles = self.volumeProfiles(tp)
                isNear, vpro = self.isNearVP(price, volProfiles)
                self.sa.UpdateFilter(self.jsonData, self.symbol,
                                     'vpro', isNear)
                self.sa.UpdateFilter(self.jsonData, self.symbol,
                                     'vpros', round(float(vpro), 2))
            except Exception as e:
                print(e)
                self.sa.UpdateFilter(self.jsonData, self.symbol,
                                     'vpro', False)
                self.sa.UpdateFilter(self.jsonData, self.symbol,
                                     'vpros', 0)
        return False

    @staticmethod
    def All():
        filter = FilterVolumeProfileDailySetup()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.jsonData)


if __name__ == '__main__':
    FilterVolumeProfileDailySetup.All()
    print('---------- done ----------')

    # filter = FilterVolumeProfileDailySetup()
    # filter.Run('AAPL')
    # print('---------- done ----------')




