import shutil
import urllib.request as request
from contextlib import closing
import pandas as pd

with closing(request.urlopen('ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt')) as r:
    with open('nasdaqlisted.txt', 'wb') as f:
        shutil.copyfileobj(r, f)

with closing(request.urlopen('ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt')) as r:
    with open('otherlisted.txt', 'wb') as f:
        shutil.copyfileobj(r, f)


def write_symbolfile(symbolList, filename, isNewFile):
    with open(filename, 'w' if isNewFile else 'a') as f:
        for symbol in symbolList:
            f.write(symbol + '\n')


def getSymbolList(f):
    exchange = f.readlines()
    # parse text data
    exchangeList = [x.split('|') for x in exchange]
    exchangeSymbols = ["{},{}".format(x[0], x[1].strip(','))
                       for x in exchangeList]
    return exchangeSymbols


def Run():
    # read text file
    with open('nasdaqlisted.txt') as f:
        exchangeList = getSymbolList(f)
        write_symbolfile(
            exchangeList[1:len(exchangeList)-1], './data/symbols.csv', True)
        print('nasdaqlisted.txt done')

    with open('otherlisted.txt') as f:
        exchangeList = getSymbolList(f)
        write_symbolfile(
            exchangeList[1:len(exchangeList)-1], './data/symbols.csv', False)
        print('otherlisted.txt done')

    print('done')
