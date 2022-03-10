import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20, 10)

# IF CHOPPINESS INDEX >= 61.8 - -> MARKET IS CONSOLIDATING
# IF CHOPPINESS INDEX <= 38.2 - -> MARKET IS TRENDING
# https://medium.com/codex/detecting-ranging-and-trending-markets-with-choppiness-index-in-python-1942e6450b58

def get_historical_data(symbol, start_date):
    api_key = 'YOUR API KEY'
    api_url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=5000&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df['values']).iloc[::-1].set_index('datetime').astype(float)
    df = df[df.index >= start_date]
    df.index = pd.to_datetime(df.index)
    return df


tsla = get_historical_data('TSLA', '2020-01-01')
print(tsla)


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


tsla['ci_14'] = get_ci(tsla['high'], tsla['low'], tsla['close'], 14)
tsla = tsla.dropna()
print(tsla)

ax1 = plt.subplot2grid((11, 1,), (0, 0), rowspan=5, colspan=1)
ax2 = plt.subplot2grid((11, 1,), (6, 0), rowspan=4, colspan=1)
ax1.plot(tsla['close'], linewidth=2.5, color='#2196f3')
ax1.set_title('TSLA CLOSING PRICES')
ax2.plot(tsla['ci_14'], linewidth=2.5, color='#fb8c00')
ax2.axhline(38.2, linestyle='--', linewidth=1.5, color='grey')
ax2.axhline(61.8, linestyle='--', linewidth=1.5, color='grey')
ax2.set_title('TSLA CHOPPINESS INDEX 14')
plt.show()

