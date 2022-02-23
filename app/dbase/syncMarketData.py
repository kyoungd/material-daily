import copy
import logging
from .marketData import MarketDataDb

class SynchronizeMarketData:
    def __init__(self, data, isCrypto=None):
        try:
            self.isCrypto = False if isCrypto is None else isCrypto
            self.db = MarketDataDb()
            _, result = self.db.ReadMarket(symbol='AAPL', datatype='stock', timeframe='1Day')
            self.home = result[0][::-1]
            self.data = data[::-1]
        except Exception as e:
            logging.error(f'SynchronizeMarketData.__init__: {e}')
            print(e)

    def startIndex(self, home, data):
        ixHome = 0
        ixData = 0
        while ixHome < len(home) and ixData < len(data):
            if data[ixData]['t'] < home[ixHome]['t']:
                ixData += 1
            elif data[ixData]['t'] > home[ixHome]['t']:
                ixHome += 1
            else:
                break
        return ixHome, ixData

    def synchronizeCommodity(self, home, data):
        try:
            syncValues = []
            ixHome, ixData = self.startIndex(home, data)
            lastValue = data[ixData]
            ixLastData = len(data) - 1
            while ixHome < len(home):
                dt = data[ixData]['t'].split('T')[0]
                ht = home[ixHome]['t'].split('T')[0]
                if ixData >= ixLastData:
                    lastValue['t'] = home[ixHome]['t']
                    syncValues.append(copy.deepcopy(lastValue))
                    ixHome += 1
                elif dt == ht:
                    lastValue = data[ixData]
                    syncValues.append(copy.deepcopy(lastValue))
                    ixData += 1
                    ixHome += 1
                elif dt < ht:
                    lastValue['t'] = home[ixHome]['t']
                    syncValues.append(copy.deepcopy(lastValue))
                    ixHome += 1
                else:
                    lastValue = data[ixData]
                    ixData += 1
            return syncValues
        except Exception as e:
            logging.error(f'SynchronizeMarketData.synchronizeCommodity: {e}')
            print(e)

    def syncrhonizeCrypto(self, home, data):
        try:
            syncValues = []
            ixHome = 0
            ixData = 0
            while ixHome < len(home) and ixData < len(data):
                dt = data[ixData]['t'].split('T')[0]
                ht = home[ixHome]['t'].split('T')[0]
                if dt == ht:
                    value = copy.deepcopy(data[ixData])
                    value['t'] = home[ixHome]['t']
                    syncValues.append(value)
                    ixData += 1
                    ixHome += 1
                elif dt < ht:
                    ixData += 1
                else:
                    value = copy.deepcopy(data[ixData])
                    value['t'] = home[ixHome]['t']
                    syncValues.append(value)
                    ixHome += 1
            return syncValues
        except Exception as e:
            logging.error(f'SynchronizeMarketData.syncrhonizeCrypto: {e}')
            print(e)

    def Run(self, data=None):
        data = self.data if data is None else data
        if len(data) == len(self.home):
            return self.data
        if self.isCrypto:
            result = self.syncrhonizeCrypto(self.home, data)
        else:
            result = self.synchronizeCommodity(self.home, data)
        return result[::-1]
