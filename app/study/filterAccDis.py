import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np

# IF CHOPPINESS INDEX >= 61.8 - -> MARKET IS CONSOLIDATING
# IF CHOPPINESS INDEX <= 38.2 - -> MARKET IS TRENDING
# https://medium.com/codex/detecting-ranging-and-trending-markets-with-choppiness-index-in-python-1942e6450b58

class WyckoffAccumlationDistribution:
    def __init__(self):
        self.lookback = 10
        self.barCountDistribution = 3
        self.barCountVolClimaxRebound = 2
        self.barCountAccumulation = 5
        self.minVolumeClimax = 600
        self.isConsolidating = 61.8
        self.isTrending = 38.2

    # IF CHOPPINESS INDEX >= 61.8 - -> MARKET IS CONSOLIDATING
    def isAccumulating(self, value):
        return value > self.isConsolidating

    def isDistributing(self, value):
        return value < self.isTrending

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

    def isDistributionPhase(self, ci:list, volClimaxIndex:int):
        startIndex = volClimaxIndex - self.barCountDistribution - 1
        barCount = self.barCountDistribution
        ciValue = ci[startIndex:barCount].sum() / barCount
        return self.isDistributing(ciValue)
        
    def isAccumulationValid(self, ci:list, volClimaxIndex:int):
        startIndex = volClimaxIndex - self.barCountVolClimaxRebound - self.barCountAccumulation
        barCount = self.barCountAccumulation
        ciValue = ci[startIndex:barCount].sum() / barCount
        return self.isAccumulating(ciValue)
        
    def Run(self, symbol:str, df:pd.DataFrame, volClimax:float, voClimaxIndex:int):
        if volClimax > self.minVolumeClimax:
            data = WyckoffAccumlationDistribution.get_ci(
                df['high'], df['low'], df['close'], self.lookback)
            data = data.dropna()
            ci = data.to_series()
            isDistribute = self.isDistributionPhase(ci, voClimaxIndex)
            isAccumulate = self.isAccumulationValid(ci, voClimaxIndex)
            return isDistribute and isAccumulate
        return False
