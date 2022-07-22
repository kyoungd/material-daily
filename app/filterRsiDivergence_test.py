from unittest import mock, TestCase
from datetime import date
from study import rsiDivergence
import pandas as pd
from util import UtilTest
from alpaca import AlpacaHistoricalBarData


class TestFilterRsiDivergence(TestCase):

    def getRealtimeData(self, symbol: str, startdate: str, enddate: str = None, timeframe: str = None):
        timeframe = '1Day' if timeframe is None else timeframe
        enddate = date.today().strftime("20%y-%m-%d") if enddate is None else enddate
        app = AlpacaHistoricalBarData(symbol, startdate, enddate, timeframe)
        return app.GetDataFrame()

    # this one should be True.  Let's debug RSI here.
    def testRsiDivergence_01(self):
        symbol:str = 'CC'
        startdate:str = '2021-05-01'
        enddate:str = '2022-05-20'
        isOk, df = self.getRealtimeData(symbol, startdate, enddate)
        self.assertTrue(isOk)
        close:float = df.iloc[0].Close
        filter = rsiDivergence()
        result = filter.Run(df)
        self.assertTrue(result)
