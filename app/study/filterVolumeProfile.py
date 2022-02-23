from scipy import stats, signal
import numpy as np
import pandas as pd
from util import StockAnalysis, AllStocks


class FilterVolumeProfile:
    def __init__(self):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        self.nearMargin = 0.05

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
        filter = FilterVolumeProfile()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.jsonData)


if __name__ == '__main__':
    FilterVolumeProfile.All()
    print('---------- done ----------')

    # filter = FilterVolumeProfile()
    # filter.Run('AAPL')
    # print('---------- done ----------')
