import requests
import logging
from .allstocks import AllStocks
from .environ import EnvFile

class ProductionAssetDataSync:
    def __init__(self):
        self.prodUrl = EnvFile.Get('PROD_ASSET_URL', 'http://localhost:1337/api/assets')
        self.data = []
        self.dataCount = 0
        self.dataBlock = EnvFile.Get('PROD_ASSET_DATA_BLOCK', 100)

    def pushToServer(self):
        try:
            r = requests.post(self.prodUrl, json=self.data)
            # print(f"Status Code: {r.status_code}, Response: {r.json()}")
            logging.info(f"ProductionAssetDataSync.pushToServer. Status Code: {r.status_code}")
            print(f"Status Code: {r.status_code}")
        except Exception as e:
            logging.error(f"ProductionAssetDataSync.pushToServer. Exception: {e}")
            print(f"pushToServer. Exception: {e}")

    def Run(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        else:
            self.symbol = symbol
        isLoaded, df = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                self.data.append({'symbol': symbol, 'timeframe': '1Day', 'data': df.to_json(orient='records')})
                self.dataCount += 1
                if self.dataCount >= self.dataBlock:
                    self.pushToServer()
                    self.data = []
                    self.dataCount = 0
            except Exception as e:
                logging.error(f"ProductionAssetDataSync.Run. Exception: {e}")
                print(f"ProductionAssetDataSync.Run. Exception: {e}")
        return False

    @staticmethod
    def All():
        filter = ProductionAssetDataSync()
        AllStocks.Run(filter.Run, False)
        filter.pushToServer()
        print('complete.  exiting.')

if __name__ == '__main__':
    ProductionAssetDataSync.All()
    print('---------- done ----------')
