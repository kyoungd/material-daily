from unittest import mock, TestCase, main
from study import trendMinMax
import pandas as pd


class TestFilterTrend(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def dataSetup(self, p0, p1, p2, p3, p4, p5, p6):
        data = {'Date':
                ['2021-12-31T00:00:00.000000000', '2021-12-30T00:00:00.000000000',
                 '2021-12-29T00:00:00.000000000', '2021-12-28:00:00.000000000',
                 '2021-12-27T00:00:00.000000000', '2021-12-26T00:00:00.000000000'
                 ],
                'Close':
                    [p0, p1, p2, p3, p4, p5]
                }
        df = pd.DataFrame(data)
        return df

    def test_trend7success1(self):
        trends, _ = self.dataSetup(50, 55, 60, 65, 70, 75, 80)
        self.assertEqual(trends, 7)

    def test_trend7success2(self):
        trends, _ = self.dataSetup(80, 75, 70, 65, 60, 55, 50)
        self.assertEqual(trends, 7)

    def test_trend7fail1(self):
        trends, reveres = self.dataSetup(50, 55, 45, 65, 40, 75, 60)
        self.assertEqual(trends, 1)
        self.assertEqual(reveres, 1)

    def test_reverse3success(self):
        trends, reveres = self.dataSetup(50, 55, 45, 40, 35, 50, 60)
        self.assertEqual(trends, 1)
        self.assertEqual(reveres, 3)
