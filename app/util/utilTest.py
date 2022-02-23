from .allstocks import AllStocks
from .allstockanalysis import StockAnalysis
from dbase import MarketDataDb

class UtilTest:
    def __init__(self):
        self.db = MarketDataDb()

    def cleanUpLastDay(self, symbol):
        try:
            isLoaded, df = AllStocks.GetDailyStockData(symbol)
            if isLoaded:
                df.rename(columns={'Date':'t', 'Open':'o',
                          'High':'h', 'Low':'l', 'Close':'c', 'Volume':'v'}, inplace=True)

                data = df[1:].to_json(orient='records')
                query = """UPDATE public.market_data SET data=%s WHERE symbol=%s AND timeframe=%s AND NOT is_deleted"""
                params = (data, symbol, '1Day')
                self.db.UpdateQuery(query, params)
        except Exception as e:
            print(f'FilterTest.Run: {symbol} {e}')
            print(e)
        
    @staticmethod
    def RunRemoveLastDay():
        app = UtilTest()
        AllStocks.RunFromDbAll(app.cleanUpLastDay)
