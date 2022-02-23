#!/usr/bin/python
import psycopg2
import logging
import pandas as pd
import json
import datetime
from util import RedisTimeFrame
from . import config

class MarketDataDb:
    connection = None

    def __init__(self):
        if MarketDataDb.connection is None:
            MarketDataDb.connection = self.db_connection()
        self.conn = MarketDataDb.connection

    def db_connection(self):
        conn = None
        try:
            # read connection parameters
            params = config()
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params)
            return conn
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(f'MarketDataDb.db_connection() - {error}')
            print(error)
            return None

    def SelectQuery(self, sql, params):
        try:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            result = cur.fetchall()
            if (result == None):
                return False, None
            else:
                return True, result
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(f'MarketDataDb.SelectQuery() - {error}')
            print(error)
            return False, None

    def UpdateQuery(self, sql, params):
        try:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            self.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(f'MarketDataDb.UpdateData() - {error}')
            print(error)
            return False

    @staticmethod
    def DefaultTimeframe(timeframe = None) -> str:
        return RedisTimeFrame.DAILY if timeframe is None else timeframe

    @staticmethod
    def DefaultDataType(self, datatype:str = None):
        return 'stock' if datatype is None else datatype

    def ReadMarket(self, symbol:str, datatype:str=None, timeframe:str=None) -> tuple:
        try:
            # logging.info(f'MarketDataDb.ReadMarket() - {symbol}')
            cur = self.conn.cursor()
            datatype = 'stock' if datatype is None else datatype
            timeframe = RedisTimeFrame.DAILY if timeframe is None else timeframe
            sql = """SELECT data, name, updated_at, id FROM public.market_data WHERE symbol=%s and datatype =%s and timeframe=%s"""

            # execute the SELECT statement
            cur.execute(sql, (symbol,datatype, timeframe))
            # get the generated id back
            result = cur.fetchone()
            if (result == None):
                return False, None
            else:
                return True, result
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(f'MarketDataDb.ReadMarket. {symbol} - {error}')
            print(error)
            return False, None

    # def ReadMarketById(self, id):
    #     try:
    #         cur = self.conn.cursor()
    #         sql = """SELECT data, symbol, atr45, atr90, atr180 FROM public.market_data WHERE symbol=%s and datatype =%s and timeframe=%s"""

    #         # execute the SELECT statement
    #         cur.execute(sql, (id))
    #         # get the generated id back
    #         result = cur.fetchone()
    #         if (result == None):
    #             return False, None
    #         else:
    #             return True, result
    #     except (Exception, psycopg2.DatabaseError) as error:
    #         print(error)
    #         return False, None

    def AppendMarket(self, symbol: str, newdata:dict, datatype:str=None, timeframe:str=None, name:str=None) -> bool:
        # logging.info(f'MarketDataDb.AppendMarket() - {symbol}')
        try:
            isOk, result = self.ReadMarket(symbol, datatype=datatype, timeframe=timeframe)
            if isOk:
                data = result[0]
                if data[0]['t'] == newdata['t']:
                    pass
                else:
                    combined = [newdata] + data                    
                    combinedData = json.dumps(combined) 
                    # firstItem = json.dumps(newdata)
                    # firstItem:list = []
                    # firstItem.append(newdata)
                    # combinedData:list = firstItem + result[0]
                    id = result[3]
                    return self.UpdateData(id, combinedData)
                    # return self.WriteMarket(symbol, combinedData, datatype=datatype, timeframe=timeframe, name=name)
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(f'MarketDataDb.AppendMarket() - {error}')
            print(error)
            return False

    def WriteMarket(self, symbol: str, data:list, datatype:str=None, timeframe:str=None, name:str=None) -> bool:
        try:
            cur = self.conn.cursor()
            timeframe = RedisTimeFrame.DAILY if timeframe is None else timeframe
            datatext = json.dumps(data)
            datatype = 'stock' if datatype is None else datatype
            name = '' if name is None else name
            time_now = datetime.datetime.now()
            sql = """INSERT INTO public.market_data(symbol, data, datatype, timeframe, name, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (symbol, datatype, timeframe) DO UPDATE SET data=%s, updated_at=%s"""
            # execute the INSERT statement
            cur.execute(sql, (symbol, datatext, datatype, timeframe, name, time_now, time_now, datatext, time_now))
            # get the generated id back
            # id = cur.fetchone()[0]
            self.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(f'MarketDataDb.WriteMarket() - {error}')
            print(error)
            return False

    def UpdateData(self, id:int, data:str) -> bool:
        try:
            cur = self.conn.cursor()
            time_now = datetime.datetime.now()
            sql = """UPDATE public.market_data SET data=%s, updated_at=%s WHERE id=%s"""
            cur.execute(sql, (data, time_now, id))
            self.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(f'MarketDataDb.UpdateData() - {error}')
            print(error)
            return False

    def StockSymbols(self, lines: list, datatype:str):
        newSymbols = []
        existingSymbols = []
        for line in lines:
            try:
                data = line.split(',')
                symbol = data[0].upper()
                if '.' in symbol:
                    continue
                else:
                    logging.info(f'MarketDataDb.StockSymbols() - {symbol}')
                    isExist, _ = self.ReadMarket(symbol, datatype=datatype)
                    if isExist:
                        existingSymbols.append(symbol)
                    else:
                        name = data[1].upper().replace('\n', '')
                        self.WriteMarket(symbol, {}, datatype=datatype, name=name)
                        newSymbols.append(symbol)
            except (Exception, psycopg2.DatabaseError) as error:
                logging.error(f'MarketDataDb.StockSymbols() - {error}')
                print(f'SockSymbols() - {error}')
        return newSymbols, existingSymbols

    def AllAVailableSymbols(self, timeframe:str = None) -> list:
        try:
            timeframe = RedisTimeFrame.DAILY if timeframe is None else timeframe
            cur = self.conn.cursor()
            sql = """SELECT id, data FROM public.market_data WHERE timeframe = %s AND NOT is_deleted"""
            # execute the SELECT statement
            cur.execute(sql, (timeframe,))
            # get the generated id back
            result = cur.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(f'MarketDataDb.AllAVailableSymbols() - {error}')
            print(error)
            return []
    
    def UpdateAtr(self, id, atr45, atr90, atr180):
        try:
            time_now = datetime.datetime.now()
            cur = self.conn.cursor()
            sql = """UPDATE public.market_data SET atr45=%s, atr90=%s, atr180=%s, updated_at=%s WHERE id=%s"""

            # execute the SELECT statement
            cur.execute(sql, (atr45, atr90, atr180, time_now, id))
            self.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(f'MarketDataDb.UpdateAtr() - {error}')
            print(error)
            return False

