from unittest import mock, TestCase, main
from study import WyckoffAccumlationDistribution
import pandas as pd


class TestFilterAccDis(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def setupDf(self, 
                c31, c30, c29, c28,
                c27, c26, c25, c24,
                c23, c22, c21, c20,
                c19, c18, c17, c16,
                c15, c14, c13, c12,
                c11, c10, c09, c08,
                c07, c06, c05, c04,
                c03, c02, c01, n30,
                n29, n28, n27, n26,
                n25, n24, n23, n22,
                n21, n20, n19, n18):
        data = {'Date':
                ['2021-12-31', '2021-12-30', '2021-12-29', '2021-12-28',
                 '2021-12-27', '2021-12-26', '2021-12-25', '2021-12-24',
                 '2021-12-23', '2021-12-22', '2021-12-21', '2021-12-20',
                 '2021-12-19', '2021-12-18', '2021-12-17', '2021-12-16',
                 '2021-12-15', '2021-12-14', '2021-12-13', '2021-12-12',
                 '2021-12-11', '2021-12-10', '2021-12-09', '2021-12-08',
                 '2021-12-07', '2021-12-06', '2021-12-05', '2021-12-04',
                 '2021-12-03', '2021-12-02', '2021-12-01', '2021-11-30',
                 '2021-11-29', '2021-11-28', '2021-11-27', '2021-11-26',
                 '2021-11-25', '2021-11-24', '2021-11-23', '2021-11-22',
                 '2021-11-21', '2021-11-20', '2021-11-19', '2021-11-18'],
                'Close': [c31, c30, c29, c28, 
                        c27, c26, c25, c24,
                        c23, c22, c21, c20,
                        c19, c18, c17, c16,
                        c15, c14, c13, c12,
                        c11, c10, c09, c08,
                        c07, c06, c05, c04,
                          c03, c02, c01, n30,
                          n29, n28, n27, n26,
                          n25, n24, n23, n22,
                          n21, n20, n19, n18],
                'Open': [c31, c30, c29, c28, 
                        c27, c26, c25, c24,
                        c23, c22, c21, c20,
                        c19, c18, c17, c16,
                        c15, c14, c13, c12,
                        c11, c10, c09, c08,
                        c07, c06, c05, c04,
                        c03, c02, c01, n30,
                n29, n28, n27, n26,
                n25, n24, n23, n22,
                n21, n20, n19, n18],
                'High': [c31+1, c30+1, c29+1, c28+1, 
                        c27+1, c26+1, c25+1, c24+1,
                        c23+1, c22+1, c21+1, c20+1,
                        c19+1, c18+1, c17+1, c16+1,
                        c15+1, c14+1, c13+1, c12+1,
                        c11+1, c10+1, c09+1, c08+1,
                        c07+1, c06+1, c05+1, c04+1,
                         c03+1, c02+1, c01+1, n30+1,
                         n29+1, n28+1, n27+1, n26+1,
                         n25+1, n24+1, n23+1, n22+1,
                         n21+1, n20+1, n19+1, n18],
                'Low': [c31-1, c30-1, c29-1, c28-1, 
                        c27-1, c26-1, c25-1, c24-1,
                        c23-1, c22-1, c21-1, c20-1,
                        c19-1, c18-1, c17-1, c16-1,
                        c15-1, c14-1, c13-1, c12-1,
                        c11-1, c10-1, c09-1, c08-1,
                        c07-1, c06-1, c05-1, c04-1,
                        c03-1, c02-1, c01-1, n30-1,
                        n29-1, n28-1, n27-1, n26-1,
                        n25-1, n24-1, n23-1, n22-1,
                        n21-1, n20-1, n19-1, n18-1],
                'Volume': [100, 100, 100, 100,
                            100, 100, 100, 100,
                            100, 100, 100, 100,
                            100, 100, 100, 100,
                            100, 100, 100, 100,
                            100, 100, 100, 100,
                            100, 100, 100, 100,
                            100, 100, 100, 100,
                            100, 100, 100, 100,
                            100, 100, 100, 100,
                            100, 100, 100, 100]
                }
        df = pd.DataFrame(data)
        return df

    # test data wi
    def test_AccumulationDetection01(self):
        df = self.setupDf(99, 101, 99, 101,
                        99, 101, 99, 101,
                        99, 101, 99, 101,
                        99, 101, 99, 101,
                        99, 101, 99, 101,
                        99, 101, 102, 104,
                        92, 104, 108, 112,
                        116, 120, 121, 120,
                        121, 120, 121, 120,
                        121, 120, 121, 120,
                        121, 120, 121, 120)
        app = WyckoffAccumlationDistribution()
        result = app.Run(symbol='AAPL', df=df[::-1].reset_index(), volClimax=1200, volClimaxIndex=24)
        self.assertEqual(result, True)