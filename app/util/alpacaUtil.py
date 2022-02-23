import alpaca_trade_api as alpaca
import os
import requests
from .environ import EnvFile

class AlpacaAccess:
    ALPACA_API_KEY = EnvFile.Get('ALPACA_API_KEY', 'AKAV2Z5H0NJNXYF7K24D')
    ALPACA_SECRET_KEY = EnvFile.Get(
        'ALPACA_SECRET_KEY', '262cAEeIRrL1KEZYKSTjZA79tj25XWrMtvz0Bezu')
    ALPACA_API_URL = EnvFile.Get(
        'ALPACA_API_URL', 'https://api.alpaca.markets')
    ALPACA_WS = EnvFile.Get(
        'ALPACA_WS', 'wss://stream.data.alpaca.markets/v2')
    # <- replace to SIP if you have PRO subscription
    ALPACA_FEED = EnvFile.Get('ALPACA_FEED', 'sip')
    ALPACA_SNAPSHOT_URL = EnvFile.Get(
        'ALPACA_SNAPSHOT_URL', 'https://data.alpaca.markets/v2/stocks/snapshots?symbols=%s')

    @staticmethod
    def connection():
        api = alpaca.REST(
            AlpacaAccess.ALPACA_API_KEY, AlpacaAccess.ALPACA_SECRET_KEY, AlpacaAccess.ALPACA_API_URL)
        return api

    @staticmethod
    def CustomHeader():
        return {'APCA-API-KEY-ID': AlpacaAccess.ALPACA_API_KEY,
                'APCA-API-SECRET-KEY': AlpacaAccess.ALPACA_SECRET_KEY}

    @staticmethod
    def HistoricalSnapshots(symbols):
        # split set into a string of symbols separated by commas
        symbolsString = ','.join(s for s in symbols)
        url = AlpacaAccess.ALPACA_SNAPSHOT_URL % (
            symbolsString)
        snapshots = requests.get(url, headers=AlpacaAccess.CustomHeader())
        return snapshots


class RedisTimeFrame:
    REALTIME = "0"
    SEC10 = "10SEC"
    MIN1 = "1Min"
    MIN2 = "2Min"
    MIN5 = "5Min"
    MIN30 = "30Min"
    HOUR = "Hour"
    DAILY = "1Day"
    WEEKLY = "Weekly"
