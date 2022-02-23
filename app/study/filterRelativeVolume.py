import pandas as pd
import numpy as np
from util import StockAnalysis, AllStocks
import talib


class FilterRelativeVolume:
    def __init__(self, symbol=None):
        self.sa = StockAnalysis()
        self.jsonData = self.sa.GetJson
        self.baseDays = 5
        self.symbol = symbol

    def getRelativeVolume(self, volumeArray):
        # create dataframe with close and output

        # length of array
        if len(volumeArray) < self.baseDays + 1:   # not enough data
            return 0
        volumes = volumeArray[1:self.baseDays]
        avgVolume = np.average(volumes)
        volume = volumes[0]
        return volume / avgVolume

    def Run(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        else:
            self.symbol = symbol
        isLoaded, tp = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                volumes = tp.Volume.to_numpy()
                relVol = self.getRelativeVolume(volumes)
                # round up
                relVol = round(relVol * 100) - 100
                self.sa.UpdateFilter(
                    self.jsonData, self.symbol, 'relvol', relVol)
                self.sa.UpdateFilter(
                    self.jsonData, self.symbol, 'volume', int(volumes[0]))
            except Exception as e:
                print(e)
                self.sa.UpdateFilter(
                    self.jsonData, self.symbol, 'relvol', False)
                self.sa.UpdateFilter(
                    self.jsonData, self.symbol, 'volume', int(volumes[0]))
        return False

    def WriteFilter(self):
        self.sa.WriteJson(self.jsonData)

    @staticmethod
    def All():
        filter = FilterRelativeVolume()
        AllStocks.Run(filter.Run, False)
        filter.sa.WriteJson(filter.jsonData)


if __name__ == '__main__':
    FilterRelativeVolume.All()
    print('---------- done ----------')
