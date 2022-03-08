from unittest import mock, TestCase
from study import fibonachiRetracement
import pandas as pd


class TestFilterFibonachiRetracement(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def dataSetup(self, p0, p1, p2, p3, p4):
        data = {'Date':
                ['2021-01-07T00:00:00.000000000', '2021-02-01T00:00:00.000000000',
                 '2021-03-12T00:00:00.000000000', '2021-04-23T00:00:00.000000000',
                 '2021-05-28T00:00:00.000000000', '2021-09-01T00:00:00.000000000'],
                'Close':
                    [p0, p1, p2,
                     p3, p4, 91.8385245]
                }
        df = pd.DataFrame(data)
        price = 110.01
        isFirstMin = False
        fib = fibonachiRetracement(price, isFirstMin, df)
        result = fib.Run()
        return result

    def test_First2BullSuccess(self):
        result, data = self.dataSetup(120.00, 100.01, 0,
                                0, 0)
        self.assertEqual(result, True)
        self.assertIsNotNone(data)

    def test_First2BearSuccess(self):
        result, data = self.dataSetup(100.01, 120.00, 0,
                                0, 0)
        self.assertEqual(result, True)
        self.assertIsNotNone(data)

    def test_First2BullFail(self):
        result, _ = self.dataSetup(110.00, 100.01, 0,
                                0, 0)
        self.assertEqual(result, False)

    def test_First2BearFail(self):
        result, _ = self.dataSetup(100.01, 110.00, 0,
                                0, 0)
        self.assertEqual(result, False)

    def test_First3BullSuccess(self):
        result, data = self.dataSetup(109.90, 120.00, 100.01,
                                0, 0)
        self.assertEqual(result, True)
        self.assertIsNotNone(data)

    def test_First3BearSuccess(self):
        result, data = self.dataSetup(119.95, 100.01, 120.00,
                                0, 0)
        self.assertEqual(result, True)
        self.assertIsNotNone(data)

    # def test_First4BullSuccess_1(self):
    #     result, data = self.dataSetup(98.95, 99.95,
    #                             100.90, 120.00,
    #                             0)
    #     self.assertEqual(result, True)
    #     self.assertIsNotNone(data)

    # def test_First4BearSuccess_2(self):
    #     result, data = self.dataSetup(120.95, 119.01,
    #                             120.00, 100.63,
    #                             0)
    #     self.assertEqual(result, True)
    #     self.assertIsNotNone(data)

    # def test_First4BullSuccess_3(self):
    #     result, data = self.dataSetup(98.95, 99.95,
    #                             110.90, 120.00,
    #                             0)
    #     self.assertEqual(result, True)
    #     self.assertIsNotNone(data)

    # def test_First4BearSuccess_4(self):
    #     result, data = self.dataSetup(120.95, 109.01,
    #                             100.00, 100.63,
    #                             0)
    #     self.assertEqual(result, True)
    #     self.assertIsNotNone(data)

    # def test_First4BullFail_5(self):
    #     result, _ = self.dataSetup(99.95, 150.95,
    #                             100.90, 120.00,
    #                             93.63782723)
    #     self.assertEqual(result, False)

    # def test_First4BearFail_6(self):
    #     result, _ = self.dataSetup(150.00, 99.01,
    #                             120.00, 100.63,
    #                             101.50373968)
    #     self.assertEqual(result, False)

    # def test_First5BullSuccess_1(self):
    #     result, data = self.dataSetup(110.90, 119.00,
    #                             109.90, 120.00,
    #                             100.00)
    #     self.assertEqual(result, True)
    #     self.assertIsNotNone(data)

    # def test_First5BearSuccess_2(self):
    #     result, data = self.dataSetup(100.95, 89.01,
    #                             105.00, 100.63,
    #                             120.00)
    #     self.assertEqual(result, True)
    #     self.assertIsNotNone(data)

    # def test_First5BullSuccess_3(self):
    #     result, data = self.dataSetup(110.90, 119.00,
    #                             111.90, 112.00,
    #                             100.00)
    #     self.assertEqual(result, True)
    #     self.assertIsNotNone(data)

    # def test_First5BearSuccess_4(self):
    #     result, data = self.dataSetup(98.95, 100.01,
    #                             99.00, 112.63,
    #                             120.00)
    #     self.assertEqual(result, True)
    #     self.assertIsNotNone(data)

    # def test_First5BullFail_5(self):
    #     result, _ = self.dataSetup(10.90, 119.00,
    #                             111.90, 112.00,
    #                             100.00)
    #     self.assertEqual(result, False)

    # def test_First5BearFail_6(self):
    #     result, _ = self.dataSetup(18.95, 100.01,
    #                             99.00, 112.63,
    #                             120.00)
    #     self.assertEqual(result, False)
