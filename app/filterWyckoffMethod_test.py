import pandas as pd
from unittest import mock, TestCase
from datetime import date
from util import UtilTest
from alpaca import AlpacaHistoricalBarData
from study import WyckoffMethod

class TestFilterWyckoffMethod(TestCase):

    def getRealtimeData(self, symbol: str, startdate: str, enddate: str = None, timeframe: str = None):
        timeframe = '1Day' if timeframe is None else timeframe
        enddate = date.today().strftime("20%y-%m-%d") if enddate is None else timeframe
        app = AlpacaHistoricalBarData(symbol, startdate, enddate, timeframe)
        return app.GetDataFrame()

    def testWyckoffMethod_01(self):
        symbol = 'EXC'
        startdate = '2001-06-01'
        isOk, df = self.getRealtimeData(symbol, startdate)
        self.assertTrue(isOk)
        close = df.iloc[0].Close
        filter = WyckoffMethod()
        result = filter.Run(symbol, df)
        self.assertTrue(result)
