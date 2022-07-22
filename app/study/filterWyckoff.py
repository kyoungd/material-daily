import pandas as pd
import numpy as np
import logging

# IF CHOPPINESS INDEX >= 61.8 - -> MARKET IS CONSOLIDATING
# IF CHOPPINESS INDEX <= 38.2 - -> MARKET IS TRENDING
# https://medium.com/codex/detecting-ranging-and-trending-markets-with-choppiness-index-in-python-1942e6450b58

class WyckoffMethod:
    def __init__(self):
        self.lookback = 10
        self.high = None
        self.low = None
        self.limitspan = 13
        self.accummulationdays = 10
        self.minaccummulationdays = 9
        self.breakoutdays = 3
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

    def GetHighestLowestDf(self, df: pd.DataFrame, columnNameHigh:str, columneNameLow:str) -> set:
        iMax = df[columnNameHigh].idxmax()
        iMin = df[columneNameLow].idxmin()
        high = df.iloc[iMax][columnNameHigh]
        low = df.iloc[iMin][columneNameLow]
        return high, low

    def isRecentAccumulation(self, df):
        accumulations = df[:self.limitspan].loc(self.isAccumulating(df['ci']))
        if len(accumulations) >= self.minaccummulationdays:
            return True
        return False
    
    def Run(self, symbol:str, dataf:pd.DataFrame):
        df = dataf[::-1]
        df.reset_index()
        data = WyckoffMethod.get_ci(
            df['High'], df['Low'], df['Close'], self.lookback)
        df1 = df.assign(ci=data)
        df2 = df1[::-1]
        df2.reset_index()
        accumulations = df[:self.limitspan].loc(self.isAccumulating(df['ci']))
        if len(accumulations) < self.minaccummulationdays:
            return False
        return True

