import logging
import yfinance as yf
from datetime import datetime

class YahooFin:

    @staticmethod
    def HistoricalPrices(symbol, timeframe=None):
        try:
            # logging.info(f'YahooFin.HistoricalPrices: {symbol}')
            timeframe = '1y' if timeframe is None else timeframe.lower()
            stock = yf.Ticker(symbol)

            hist = stock.history(period=timeframe)
            # show actions (dividends, splits)
            stock.actions

            result = []
            for _, row in hist.iterrows():
                # print(str(row.name))
                t = str(row.name).replace(' 00:00:00', 'T05:00:00Z')
                result.append({'t': t, 'o': row.Open, 'h': row.High,
                            'l': row.Low, 'c': row.Close, 'v': row.Volume})
            return result[::-1]
        except Exception  as e:
            logging.error(f'YahooFin.HistoricalPrices {e}')
            return []

    @staticmethod
    def SnapshotPrices(symbol, timeframe=None):
        try:
            logging.info('YahooFin.SnapshotPrices: {symbol}')
            timeframe = '1day' if timeframe is None else timeframe.lower()
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1day")
            for _, row in hist.iterrows():
                t = str(row.name).replace(' 00:00:00', 'T05:00:00Z')
                return {'t': t, 'o': row.Open, 'h': row.High, 'l': row.Low, 'c': row.Close, 'v': row.Volume}
        except Exception as e:
            logging.error(f'YahooFin.SnapshotPrices {e}')
            return {}
