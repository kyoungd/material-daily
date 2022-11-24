import json
import logging
import os
from .environ import EnvFile

class JsonFavorite:
    def __init__(self, filename=None, userId=None, readJsonFile=None) -> None:
        readJsonFile = True if readJsonFile is None else readJsonFile
        filename = 'favorites.json' if filename == None else filename
        self.userId = userId
        folderPath = EnvFile.Get('DATA_FOLDER_PATH', 
            '/home/young/Desktop/code/trading/material-daily/data')
        self.filename = f'{folderPath}/{filename}' if userId is None else f'{folderPath}/{userId}/{filename}'
        self.data = self.readJson() if readJsonFile else {}

    @property
    def GetJson(self):
        return self.data

    def readJson(self):
        try:
            with open(self.filename, "r") as openfile:
                data = json.load(openfile)
            return data
        except Exception as e:
            logging.error(
                f'JsonFavorite.readJson Error reading json file: {self.filename} {e}')
            print(
                f'JsonFavorite.readJson Error reading json file: {self.filename} {e}')
            raise Exception(e)

    def WriteJson(self, data=None):
        try:
            self.data = data if data != None else self.data
            with open(self.filename, "w") as outfile:
                json.dump(self.data, outfile)
        except Exception as e:
            logging.error(
                f'JsonFavorite.WriteJson Error Writing json file: {self.filename} {e}')
            print(
                f'JsonFavorite.WriteJson Error Writing json file: {self.filename} {e}')
            raise Exception(e)

    def IsFileExists(self):
        return os.path.exists(self.filename)

    def EmptyJson(self):
        self.data = {}
        self.WriteJson()

