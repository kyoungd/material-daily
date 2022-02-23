import json
from typing import Dict


class symbolsCsvFile:
    def __init__(self, filename, userId=None, readJsonFile=True) -> None:
        self.userId = userId
        self.filename = "./data/{}".format(
            filename) if userId == None else "../data/{}/{}".format(userId, filename)

    def ReadFile(self, filename=None) -> Dict:
        filename = self.filename if filename == None else filename
        with open(filename, 'r') as f:
            lines = f.readlines()
            # print(lines)
        dicts = {}
        for line in lines[1:]:
            dicts[line.split(',')[0]] = line.split(',')[1].strip('\n')
        return dicts

    def WriteFile(self, dicts, filename=None) -> None:
        filename = self.filename if filename == None else filename
        with open(filename, "w") as fw:
            fw.write('{},{}\n'.format("filename", "company name"))
            for key in dicts.keys():
                fw.write('{},{}\n'.format(key, dicts[key]))


class SymbolsFile(symbolsCsvFile):
    def __init__(self) -> None:
        super().__init__("symbols.csv")

    def ResolveSymbols(self, favorites: Dict) -> Dict:
        symbols = self.ReadFile()
        for favorite in favorites:
            # if key exist in dictionary
            if favorite.key not in symbols.keys():
                symbols[favorite.key] = favorite.value
            if favorite["symbol"] not in symbols.data.keys():
                symbols.data[favorite["symbol"]] = favorite["data"]
        symbols.WriteFile()
