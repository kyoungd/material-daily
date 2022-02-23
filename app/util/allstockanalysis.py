import json


class StockAnalysis:
    def __init__(self, userId=None, readJsonFile=True):
        self.filename = "./data/symbols.json" if userId == None else "../data/" + \
            userId + "./symbols.json"
        self.data = self.readJson() if readJsonFile else {}

    @property
    def GetJson(self):
        return self.data

    def readJson(self):
        with open(self.filename, 'r') as openfile:
            data = json.load(openfile)
        return data

    def WriteJson(self, data=None):
        self.data = data if data != None else self.data
        with open(self.filename, "w") as outfile:
            json.dump(self.data, outfile)

    def FindStocks(self, keyConditions):
        # for dictionary keys
        stocks = []
        for key in self.data.keys():
            data = self.data[key]
            conditionMet = eval(keyConditions)
            if conditionMet:
                stocks.append({'symbol': key, 'data': data})
        return stocks

    def UpdateFilter(self, data, symbol, filterName, filterValue):
        if symbol not in data.keys():
            data[symbol] = {}
        data[symbol][filterName] = filterValue

    def EmptyJson(self):
        self.data = {}
        self.WriteJson()


if __name__ == "__main__":
    sa = StockAnalysis()
    stocks = sa.FindStocks('data["ema50"] and data["keylevels"]')
    print(stocks)
