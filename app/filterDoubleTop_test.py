from unittest import mock, TestCase
from study import doubleTop
import pandas as pd


class TestFilterDoubleTop(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def dataSetup(self, price, isFirstMin, p0, p1, p2, p3, p4, p5):
        data = {'Date':
                ['2021-01-07T00:00:00.000000000', '2021-02-01T00:00:00.000000000',
                 '2021-03-12T00:00:00.000000000', '2021-04-23T00:00:00.000000000',
                 '2021-05-28T00:00:00.000000000', '2021-09-01T00:00:00.000000000'],
                'Close':
                    [p0, p1, p2,
                     p3, p4, p5]
                }
        df = pd.DataFrame(data)
        app = doubleTop(price, df, isFirstMin, 0.1)
        result = app.Run()
        return result

    def test_DoubleTopSucess1(self):
        result = self.dataSetup(100.1, False, 100, 80, 100, 70, 90, 70)
        self.assertEqual(result, True)

    def test_DoubleTopSucess2(self):
        result = self.dataSetup(100.1, True, 80, 100, 79, 95, 90, 102)
        self.assertEqual(result, True)

    def test_DoubleTopSucess3(self):
        result = self.dataSetup(100.1, True, 80, 100, 80, 81, 70, 82)
        self.assertEqual(result, True)

    def test_DoubleTopSucess4(self):
        result = self.dataSetup(80.1, False, 100, 80, 95, 101, 97, 92)
        self.assertEqual(result, True)

    def test_DoubleTopFail1(self):
        result = self.dataSetup(100.1, False, 80,70,80,70,80,70)
        self.assertEqual(result, False)

    def test_DoubleTopFail2(self):
        result = self.dataSetup(80.1, False, 100, 98, 104, 99, 104, 99)
        self.assertEqual(result, False)

    def test_DoubleTopFail3(self):
        result = self.dataSetup(80.1, True, 80, 110, 100, 110, 100, 110)
        self.assertEqual(result, False)

    def test_DoubleTopFail4(self):
        result = self.dataSetup(80.1, False, 80, 70, 100, 70, 80, 70)
        self.assertEqual(result, False)

    def test_DoubleTopFail4(self):
        result = self.dataSetup(80.1, True, 70, 100, 70, 80, 70, 80)
        self.assertEqual(result, False)
