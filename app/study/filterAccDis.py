import pandas as pd
import numpy as np
import logging

# IF CHOPPINESS INDEX >= 61.8 - -> MARKET IS CONSOLIDATING
# IF CHOPPINESS INDEX <= 38.2 - -> MARKET IS TRENDING
# https://medium.com/codex/detecting-ranging-and-trending-markets-with-choppiness-index-in-python-1942e6450b58

class WyckoffAccumlationDistribution:
    def __init__(self):
        self.lookback = 10
        self.barCountDistribution = 3
        self.barCountVolClimaxRebound = 2
        self.barCountAccumulation = 7
        self.minVolumeClimax = 5.0  # minimum volume climax - 600%
        self.isConsolidating = 61.8
        self.isTrending = 38.2

    # IF CHOPPINESS INDEX >= 61.8 - -> MARKET IS CONSOLIDATING
    def isAccumulating(self, value):
        return value > self.isConsolidating

    def isDistributing(self, value):
        return value < self.isTrending

    # **** Tricky part ****
    # Because it uses previous data for choppiness, you cannot take an average of the chopiness.
    # The average is already built-in to the calculation.  So evaluate any of the data falls
    # into consolidating or trending regions.
    # 
    @staticmethod
    def get_ci(high, low, close, lookback):
        tr1 = pd.DataFrame(high - low).rename(columns={0: 'tr1'})
        tr2 = pd.DataFrame(abs(high - close.shift(1))).rename(columns={0: 'tr2'})
        tr3 = pd.DataFrame(abs(low - close.shift(1))).rename(columns={0: 'tr3'})
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis=1, join='inner').dropna().max(axis=1)
        atr = tr.rolling(1).mean()
        highh = high.rolling(lookback).max()
        lowl = low.rolling(lookback).min()
        ci = 100 * np.log10((atr.rolling(lookback).sum()) /
                            (highh - lowl)) / np.log10(lookback)
        return ci
    
    def trimIndexes(self, ci:list, startIndex:int, endIndex:int):
        if startIndex < 0:
            startIndex = 0
        if endIndex > len(ci):
            endIndex = len(ci)
        if startIndex >= endIndex:
            startIndex = endIndex - 1
        return startIndex, endIndex

    def isDistributionPhase(self, ci: list, volClimaxIndex: int):
        startIndex = volClimaxIndex - self.barCountDistribution - 1
        endIndex = startIndex + self.barCountDistribution
        startIndex, endIndex = self.trimIndexes(ci, startIndex, endIndex)
        for i in range(startIndex, endIndex):
            if self.isDistributing(ci[i]):
                return True
        return False

    def isAccumulationValid(self, ci:list, volClimaxIndex:int):
        endIndex = volClimaxIndex - self.barCountVolClimaxRebound
        startIndex = endIndex - self.barCountAccumulation
        startIndex, endIndex = self.trimIndexes(ci, startIndex, endIndex)
        for value in ci[startIndex:endIndex]:
            if self.isAccumulating(value):
                return True
        return False
        
    def Run(self, symbol:str, df:pd.DataFrame, volClimax:float, volClimaxIndex:int):
        try:
            if volClimax > self.minVolumeClimax:
                data = WyckoffAccumlationDistribution.get_ci(
                    df['High'], df['Low'], df['Close'], self.lookback)
                data = data.dropna()
                ci = data.to_numpy()[::-1]
                isDistribute = self.isDistributionPhase(ci, volClimaxIndex)
                isAccumulate = self.isAccumulationValid(ci, volClimaxIndex)
                return isDistribute and isAccumulate
            return False
        except Exception as e:
            logging.error(f'WyckoffAccumlationDistribution.Run: {symbol} - {e}')
            print(f'WyckoffAccumlationDistribution.Run: {symbol} - {e}')
            return False


    def RunWickoff(self, symbol:str, dataf:pd.DataFrame):
        df = dataf[::-1]
        df.reset_index()
        data = WyckoffAccumlationDistribution.get_ci(
            df['High'], df['Low'], df['Close'], self.lookback)
        data = data.dropna()
        