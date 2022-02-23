from util import AllStocks

def isLoadFile(symbol):
    isLoaded, tp = AllStocks.GetDailyStockData(symbol)
    return isLoaded

def RemoveNoDataStocks():
    AllStocks.Run(isLoadFile, isSymbolsRewrite=True)

if __name__ == '__main__':
    RemoveNoDataStocks()
