#!/usr/bin/python
import psycopg2
from . import config
import pandas as pd
import json
import datetime

class SecDb:
    def __init__(self):
        self.conn = self.db_connection()

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
            print(error)
            return None

    def get_cik(self, symbol):
        try:
            cur = self.conn.cursor()

            sql = """SELECT cik FROM site_sec where symbol=%s"""
            # execute the SELECT statement
            cur.execute(sql, (symbol,))
            # get the generated id back
            result = cur.fetchone()
            if (result == None):
                return False, None
            else:
                return True, result[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return False, None

    def save_cik(self, symbol, cik):
        try:
            """ insert a new vendor into the vendors table """
            cur = self.conn.cursor()

            sql = """INSERT INTO public.site_sec(symbol, cik) VALUES(%s, %s) ON CONFLICT (symbol) DO UPDATE SET cik=%s"""
            # execute the INSERT statement
            cur.execute(sql, (symbol, cik, cik))
            # get the generated id back
            # id = cur.fetchone()[0]
            self.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return False


    def GetLastDaily(self, symbol):
        try:
            cur = self.conn.cursor()

            sql = """SELECT market_close, market_close_at FROM site_sec where symbol=%s"""
            # execute the SELECT statement
            cur.execute(sql, (symbol,))
            # get the generated id back
            result = cur.fetchone()
            if (result == None):
                return False, None
            else:
                return True, {'close': result[0], 'dt': result[1]}
        except (Exception, psycopg2.DatabaseError) as error:
            print('databaseAccess.GetLastDaily() {}'.format(error))
            return False, None
        pass

    def SetLastDaily(self, symbol, close: float, dt = None):
        try:
            if dt is None:
                dt = datetime.datetime.now()
            """ insert a new vendor into the vendors table """
            cur = self.conn.cursor()

            sql = """INSERT INTO public.site_sec(symbol, cik, market_close, market_close_at) VALUES(%s, '0', %s, %s) ON CONFLICT (symbol) DO UPDATE SET market_close=%s, market_close_at=%s;"""
            # execute the INSERT statement
            cur.execute(sql, (symbol, close, dt, close, dt))
            # get the generated id back
            # id = cur.fetchone()[0]
            self.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print('databaseAccess.SetLastDaily() {}'.format(error))
            return False
    
    def GetFloats(self, symbol:str)->set:
        try:
            cur = self.conn.cursor()

            sql = """SELECT float_percent, float_volume FROM site_sec where symbol=%s"""
            # execute the SELECT statement
            cur.execute(sql, (symbol,))
            # get the generated id back
            result = cur.fetchone()
            if (result == None or result[0] is None or result[1] is None):
                return False, (0,0)
            else:
                return True, (float(result[0]), float(result[1]))
        except (Exception, psycopg2.DatabaseError) as error:
            print('databaseAccess.getFloats() {}'.format(error))
            return False, (0,0)

    def SetFloats(self, symbol:str, floatP: float, floatV: float, dt:datetime = None) -> bool:
        try:
            if dt is None:
                dt = datetime.datetime.now()
            """ insert a new vendor into the vendors table """
            cur = self.conn.cursor()

            sql = """INSERT INTO public.site_sec(symbol, cik, float_percent, float_volume) VALUES(%s, '0', %s, %s) ON CONFLICT (symbol) DO UPDATE SET float_percent=%s, float_volume=%s;"""
            # execute the INSERT statement
            cur.execute(sql, (symbol, floatP, floatV, floatP, floatV))
            # get the generated id back
            # id = cur.fetchone()[0]
            self.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print('databaseAccess.setFloats() {}'.format(error))
            return False
