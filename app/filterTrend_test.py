from unittest import mock, TestCase, main
from study import trendMinMax
import pandas as pd


class TestFilterTrend(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def dataSetup(self, p01:float, p02:float, p11:float, p12:float, 
                        p21:float, p22:float, p31:float, p32:float, 
                        p41:float, p42:float, p51:float, p52:float, 
                        p61:float, p62:float, isFirstMin:bool, price:float):
        data = {'Date':
                ['2021-12-31T00:00:00.000000000', '2021-12-30T00:00:00.000000000',
                 '2021-12-29T00:00:00.000000000', '2021-12-28:00:00.000000000',
                 '2021-12-27T00:00:00.000000000', '2021-12-26T00:00:00.000000000',
                 '2021-12-25T00:00:00.000000000', '2021-12-24T00:00:00.000000000',
                 '2021-12-23T00:00:00.000000000', '2021-12-22T00:00:00.000000000',
                 '2021-12-21T00:00:00.000000000', '2021-12-20T00:00:00.000000000',
                 '2021-12-19T00:00:00.000000000', '2021-12-18T00:00:00.000000000'
                 ],
                'Close':
                    [p01, p02, p11, p12, p21, p22, p31, p32, p41, p42, p51, p52, p61, p62]
                }
        df = pd.DataFrame(data)
        app = trendMinMax(df, isFirstMin, price)
        return app.Run()

    # test data with no close price deviation

    def test_trend7success_01(self):
        reverses, _ = self.dataSetup(
            50, 48, 55, 53, 60, 58, 65, 63, 70, 68, 75, 73, 80, 78, False, 49)
        self.assertEqual(reverses, 6)

    def test_trend7success_02(self):
        reverses, _ = self.dataSetup(
            48, 55, 53, 60, 58, 65, 63, 70, 68, 75, 73, 80, 78, 85, True, 49)
        self.assertEqual(reverses, 6)

    def test_trend7success_04(self):
        reverses, _ = self.dataSetup(
            80, 82, 75, 77, 70, 72, 65, 68, 60, 62, 55, 57, 50, 52, True, 81)
        self.assertEqual(reverses, 6)

    def test_trend7success_05(self):
        reverses, _ = self.dataSetup(
            82, 75, 77, 70, 72, 65, 68, 60, 62, 55, 57, 50, 52, 45, False, 81)
        self.assertEqual(reverses, 6)

    # test data with close price deviation

    def test_trend7success_11(self):
        reverses, trends = self.dataSetup(
            50, 48, 55, 53, 60, 58, 65, 63, 70, 68, 75, 73, 80, 78, False, 47)
        self.assertEqual(reverses, 6)
        self.assertEqual(trends, 0)

    def test_trend7success_12(self):
        reverses, trends = self.dataSetup(
            48, 55, 53, 60, 58, 65, 63, 70, 68, 75, 73, 80, 78, 85, True, 56)
        self.assertEqual(reverses, 0.5)
        self.assertEqual(trends, 6)

    def test_trend7success_14(self):
        reverses, _ = self.dataSetup(
            80, 82, 75, 77, 70, 72, 65, 68, 60, 62, 55, 57, 50, 52, True, 84)
        self.assertEqual(reverses, 6)

    def test_trend7success_15(self):
        reverses, trends = self.dataSetup(
            82, 75, 77, 70, 72, 65, 68, 60, 62, 55, 57, 50, 52, 45, False, 74)
        self.assertEqual(reverses, 0.5)
        self.assertEqual(trends, 6)

    # test data with no close price deviation, mid direction change

    def test_trend7success_21(self):
        reverses, trends = self.dataSetup(
            80, 73, 75, 68, 70, 63, 65, 63, 70, 68, 75, 73, 80, 78, False, 79)
        self.assertEqual(reverses, 3)
        self.assertEqual(trends, 3)

    def test_trend7success_22(self):
        reverses, trends = self.dataSetup(
            73, 75, 68, 70, 63, 65, 63, 70, 68, 75, 73, 80, 78, 85, True, 77)
        self.assertEqual(reverses, 2.5)
        self.assertEqual(trends, 3.5)

    def test_trend7success_24(self):
        reverses, trends = self.dataSetup(
            50, 57, 55, 62, 60, 69, 65, 68, 60, 62, 55, 57, 50, 52, True, 51)
        self.assertEqual(reverses, 2.5)
        self.assertEqual(trends, 3.5)

    def test_trend7success_25(self):
        reverses, trends = self.dataSetup(
            47, 45, 52, 50, 57, 55, 63, 60, 62, 55, 57, 50, 52, 45, False, 46)
        self.assertEqual(reverses, 3.0)
        self.assertEqual(trends, 3.0)

    # test data with close price deviation, mid direction change

    def test_trend7success_31(self):
        reverses, trends = self.dataSetup(
            80, 73, 75, 68, 70, 63, 65, 63, 70, 68, 75, 73, 80, 78, False, 70)
        self.assertEqual(reverses, 0.5)
        self.assertEqual(trends, 3)

    def test_trend7success_32(self):
        reverses, trends = self.dataSetup(
            73, 75, 68, 70, 63, 65, 63, 70, 68, 75, 73, 80, 78, 85, True, 80)
        self.assertEqual(reverses, 2.5)
        self.assertEqual(trends, 3.5)

    def test_trend7success_34(self):
        reverses, trends = self.dataSetup(
            50, 57, 55, 62, 60, 69, 65, 68, 60, 62, 55, 57, 50, 52, True, 60)
        self.assertEqual(reverses, 0.5)
        self.assertEqual(trends, 2.5)

    def test_trend7success_35(self):
        reverses, trends = self.dataSetup(
            47, 45, 52, 50, 57, 55, 63, 60, 62, 55, 57, 50, 52, 45, False, 40)
        self.assertEqual(reverses, 3.0)
        self.assertEqual(trends, 3.0)
