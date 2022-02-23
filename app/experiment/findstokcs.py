from allstockanalysis import StockAnalysis
import json


def readJson():
    with open('study/findstocks.json', 'r') as openfile:
        data = json.load(openfile)
    return data


if __name__ == '__main__':
    print('{filteratr": true, "atr": 20.52, "close": 567.06, "avgatr": 24.66, "trendup": false, "trenddown": false, "keylevel": false, "fibonachi": true, "threebars": false}')
    print(' ------ ')
    # command line arguments
    try:
        jsonData = readJson()
        sa = StockAnalysis()
        while True:
            print('  ')
            print(' ----------------------------------')
            print('{filteratr": true, "atr": 20.52, "close": 567.06, "avgatr": 24.66, "trendup": false, "trenddown": false, "keylevel": false, "fibonachi": true, "threebars": false}')
            print('input condition commands')
            dataIn = str(input())
            data = dataIn.split(' ')
            command = ""
            for key in data:
                if key in jsonData.keys():
                    command += jsonData[key] if command == "" else " " + \
                        jsonData[key]
                else:
                    command += key if command == "" else " " + key
            result = sa.FindStocks(command)
            print(result)
    except Exception as e:
        print(e)
