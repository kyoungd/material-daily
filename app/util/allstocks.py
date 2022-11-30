from requests.structures import CaseInsensitiveDict
import pandas as pd
import logging
import requests
from .environ import EnvFile
from dbase import MarketDataDb
from .redisHash import JwtSysOp

class AllStocks:
    favorites:dict = {}

    @staticmethod
    def DownloadFavorites():
        # call rest api http get with bearer token and request.get
        try:
            url:token = EnvFile.Get("URL_GET_ALL_FAVORITES", "https://simp-admin.herokuapp.com/api/api/favorites")
            jwt = JwtSysOp.run()
            print(jwt)
            token:str = EnvFile.Get("ADMIN_SYSOPS_TOKEN", "")
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            headers["Authorization"] = f"Bearer {token}"
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                result = resp.json()
                AllStocks.favorites = result["data"]["attributes"]
                logging.info("Downloaded all favorites ")
            else:
                logging.error(f"Error downloading favorites {resp.status_code}")
        except Exception as e:
            print(f'allstocks.RunFromFile() failed - {e}')
            logging.error(f'allstocks.RunFromFile() failed - {e}')

    @staticmethod
    def IsFavorite(symbol):
        if symbol in AllStocks.favorites:
            return True
        return False

    @staticmethod
    def RunFromFile(func, isSymbolsRewrite=False, filename=None):
        try:
            filename = './data/symbols.csv' if filename == None else filename
            with open(filename, 'r') as f:
                lines = f.readlines()
                # print(lines)
            dicts = {}
            for line in lines[1:]:
                dicts[line.split(',')[0]] = line.split(',')[1].strip('\n')
            for line in lines[1:]:
                symbol = line.split(',')[0]
                filterOk = func(symbol)
                if not filterOk:
                    dicts.pop(symbol)
            if isSymbolsRewrite:
                with open(filename, "w") as fw:
                    for key in dicts.keys():
                        fw.write('{},{}\n'.format(key, dicts[key]))
        except Exception as e:
            print(f'allstocks.RunFromFile() failed - {e}')
            logging.error(f'allstocks.RunFromFile() failed - {e}')
            return False, None

    @staticmethod
    def RunFromDb(func):
        try:
            symbolFilterVolatility01 = float(
                EnvFile.Get('SYMBOL_FILTER_VOLATILITY_01', 10))
            symbolFilterVolatility03 = float(
                EnvFile.Get('SYMBOL_FILTER_VOLATILITY_03', 15))
            symbolFilterVolatility30 = float(
                EnvFile.Get('SYMBOL_FILTER_VOLATILITY_30', 20))

            db = MarketDataDb()
            query = """SELECT symbol FROM public.market_data WHERE timeframe='1Day' AND NOT is_deleted AND (volatility01>=%s OR volatility03>=%s OR volatility30>=%s)"""
            isOk, result = db.SelectQuery(
                query, (symbolFilterVolatility01, symbolFilterVolatility03, symbolFilterVolatility30))
            symbols = result
            for row in symbols:
                if not AllStocks.IsFavorite(row[0]):
                    symbol = row[0]
                    func(symbol)
            for symbol in AllStocks.favorites.keys():
                func(symbol)
        except Exception as e:
            print(f'allstocks.RunFromDb() failed - {e}')
            logging.error(f'allstocks.RunFromDb() failed - {e}')
            return False, None

    @staticmethod
    def RunFromDbAll(func):
        try:
            db = MarketDataDb()
            query = """SELECT symbol FROM public.market_data WHERE timeframe='1Day' AND NOT is_deleted"""
            isOk, result = db.SelectQuery(query, ())
            if isOk:
                symbols = result
                lineCount = 0
                for symbol in symbols:
                    lineCount += 1
                    if (lineCount % 100) == 0:
                        print(lineCount)
                    func(symbol[0])
            else:
                logging.error('allstocks.RunFromDbAll SelectQuery failed: ')
                print('allstocks.RunFromDbAll SelectQuery failed: ')
        except Exception as e:
            logging.error('allstocks.RunFromDbAll SelectQuery failed: ')
            print('allstocks.RunFromDbAll SelectQuery failed: ')

    @staticmethod
    def Run(func, isSymbolsRewrite=False, filename=None):
        AllStocks.RunFromDb(func)

    @staticmethod
    def stockFile(symbol):
        datapath = EnvFile.Get(
            'STOCK_DATA_PATH', './data/stocks')
        return datapath + '/' + symbol + '.csv'

    @staticmethod
    def GetDailyStockData(symbol):
        return AllStocks.GetDailyStockDataFromDb(symbol)

    @staticmethod
    def GetDailyStockDataFromDb(symbol):
        try:
            db = MarketDataDb()
            sql = """SELECT data FROM public.market_data WHERE symbol=%s AND timeframe='1Day' AND NOT is_deleted"""
            params = (symbol,)
            isOk, results = db.SelectQuery(sql, params)
            if isOk:
                df:pd.DataFrame = pd.DataFrame(results[0][0])
                df.rename(columns={'t': 'Date', 'o': 'Open',
                                'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'}, inplace=True)
                return True, df
            return False, None
        except Exception as e:
            logging.error(f'allstocks.GetDailyStockDataFromDb failed - {e}')
            print(f'allstocks.GetDailyStockDataFromDb failed - {e}')
            return False, None

    @staticmethod
    def GetDailyStockDataFromFile(symbol):
        try:
            filename = AllStocks.stockFile(symbol)
            df = pd.read_csv(filename)
            df.rename(columns={' Open': 'Open',
                               ' High': 'High', ' Low': 'Low', ' Close': 'Close', ' Volume': 'Volume', ' Adj Close': 'Adj Close'}, inplace=True)
            return True, df
        except Exception as e:
            logging.error(f'allstocks.GetDailyStockDataFromFile() failed - {e}')
            print(f'allstocks.GetDailyStockDataFromFile() failed - {e}')
            return False, None

    @staticmethod
    def GetWeeklyStockData(symbol):
        try:
            isLoadedOk, df = AllStocks.GetDailyStockData(symbol)
            if not isLoadedOk:
                return False, None
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            df.sort_index(inplace=True)

            def take_first(array_like):
                return array_like[0]

            def take_last(array_like):
                return array_like[-1]
            how = {'Open': 'first',
                   'High': 'max',
                   'Low': 'min',
                   'Close': 'last',
                   'Volume': 'sum'}
            output = df.resample('W').agg(how)

            # output = df.resample('W',                                 # Weekly resample
            #                      how={'Open': take_first,
            #                           'High': 'max',
            #                           'Low': 'min',
            #                           'Close': take_last,
            #                           'Volume': 'sum'},
            #                      loffset=pd.offsets.timedelta(days=-6))  # to put the labels to Monday

            output = output[['Open', 'High', 'Low',
                            'Close', 'Volume']]
            return isLoadedOk, output
        except Exception as e:
            logging.error(f'allstocks.GetWeeklyStockData() failed - {e}')
            print(f'allstocks.GetWeeklyStockData() failed - {e}')
            return False, None

    @staticmethod
    def Get1MinuteStockData(symbol):
        try:
            db = MarketDataDb()
            sql = """SELECT data FROM public.market_data WHERE symbol=%s AND timeframe='1Min' AND NOT is_deleted"""
            params = (symbol,)
            isOk, results = db.SelectQuery(sql, params)
            if isOk:
                df: pd.DataFrame = pd.DataFrame(results[0][0])
                return True, df
            return False, None
        except Exception as e:
            logging.error(f'allstocks.Get1MinuteStockData() failed - {e}')
            print(f'allstocks.Get1MinuteStockData() failed - {e}')
            return False, None

if __name__ == '__main__':
    result1 = AllStocks.DownloadFavorites()
    print(result1)
    result2 = AllStocks.GetWeeklyStockData('AAPL')
    print(result2)
