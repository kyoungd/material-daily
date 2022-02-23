from unittest import mock, TestCase
from study import FilterThreeBars
import pandas as pd


class TestFilterThreeBars(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def dataSetup(self, p0, p1, p2, p3):
        data = {'Date':
                ['2021-01-07T00:00:00.000000000', '2021-02-01T00:00:00.000000000',
                 '2021-03-12T00:00:00.000000000', '2021-04-23T00:00:00.000000000'],
                'Close':
                    [p0, p1, p2, p3]
                }
        df = pd.DataFrame(data)
        fib = FilterThreeBars()
        result = fib.ThreeBarLogic(df)
        return result

    def test_3BarBullSuccess(self):
        result = self.dataSetup(110.01, 120.01, 100.3, 0)
        self.assertEqual(result, True)

    def test_3BarBearSuccess(self):
        result = self.dataSetup(110.02, 100.02, 120.01, 0)
        self.assertEqual(result, True)

    def test_4BarBullSuccess(self):
        result = self.dataSetup(110.01, 120.01, 120.3, 100.3)
        self.assertEqual(result, True)

    def test_4BarBearSuccess(self):
        result = self.dataSetup(110.02, 100.02, 101.01, 120.01)
        self.assertEqual(result, True)

    def test_3BarBullFail(self):
        result = self.dataSetup(110.01, 120.01, 130.3, 0)
        self.assertEqual(result, False)

    def test_3BarBullFail_TooHigh(self):
        result = self.dataSetup(140.01, 120.01, 130.3, 0)
        self.assertEqual(result, False)

    def test_3BarBullFail_TooLow(self):
        result = self.dataSetup(110.01, 120.01, 130.3, 0)
        self.assertEqual(result, False)

    def test_4BarBullFail(self):
        result = self.dataSetup(110.01, 120.01, 130.3, 140.3)
        self.assertEqual(result, False)
