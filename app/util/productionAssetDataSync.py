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

    def addData(self, symbol, timeframe, data):
        self.data.append({'symbol': symbol, 'timeframe': timeframe, 'data': data})
        self.dataCount += 1

    def pushToServer(self):
        try:
            r = requests.post(self.prodUrl, json=self.data)
            # print(f"Status Code: {r.status_code}, Response: {r.json()}")
            logging.info(f"ProductionAssetDataSync.pushToServer. Status Code: {r.status_code}")
            print(f"Status Code: {r.status_code}")
            print('complete.  exiting.')
        except Exception as e:
            logging.error(f"ProductionAssetDataSync.pushToServer. Exception: {e}")
            print(f"pushToServer. Exception: {e}")
            print('error.  exiting.')

    def Run(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        else:
            self.symbol = symbol
        isLoaded, tp = AllStocks.GetDailyStockData(symbol)
        if isLoaded:
            try:
                self.addData(symbol, '1Day', tp.to_json())
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

if __name__ == '__main__':
    ProductionAssetDataSync.All()
    print('---------- done ----------')
