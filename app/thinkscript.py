from datetime import datetime
from dateutil.parser import parse

script_drawline = """
    script DrawLine {
        input startDate = 20210420;
        input onePrice = 50;
        def hh = if GetYYYYMMDD() >= startDate then onePrice else Double.NaN;
        plot oneLine = hh;
    }
"""

sr_line = """
    plot supportLine_{0} = DrawLine({1}, {2});
    supportLine_{0}.SetPaintingStrategy(PaintingStrategy.LINE);
    supportLine_{0}.SetLineWeight(1);
    supportLine_{0}.SetDefaultColor(Color.LIGHT_RED);
    supportLine_{0}.SetStyle(Curve.SHORT_DASH);
"""


cloud_line = """
    def startDate = {0}
    def OpenPrice = if GetYYYYMMDD() >= startDate then {1} else Double.NaN
    def ClosePrice = if GetYYYYMMDD() >= startDate then {2} else Double.NaN
    AddCloud(OpenPrice, ClosePrice, color.RED, color.GREEN, yes)
"""


def support_resistance_script(sr_lines):
    tscript = script_drawline
    for item in sr_lines:
        index = item[0]
        onedate = parse(item[1])
        price = item[2]
        tscript += " \n " + \
            sr_line.format(index, "{:%Y%m%d}".format(onedate), price)
    return tscript


def overnight_gapper_script(gappers):
    tscript = ""
    for ix in range(0, len(gappers) - 1, 2):
        date1 = parse(gappers[ix][2])
        price1 = gappers[ix][1]
        price2 = gappers[ix+1][1]
        tscript += " \n " + \
            cloud_line.format("{:%Y%m%d}".format(date1), price1, price2)
    return tscript


if __name__ == '__main__':
    sr_lines = {
        "result": [
            [
                29,
                "Wed, 10 Jun 2020 00:00:00 GMT",
                0.89
            ],
            [
                56,
                "Mon, 20 Jul 2020 00:00:00 GMT",
                0.68
            ],
            [
                62,
                "Tue, 28 Jul 2020 00:00:00 GMT",
                2.15
            ],
            [
                83,
                "Wed, 26 Aug 2020 00:00:00 GMT",
                1.28
            ],
            [
                138,
                "Thu, 12 Nov 2020 00:00:00 GMT",
                1.75
            ],
            [
                188,
                "Wed, 27 Jan 2021 00:00:00 GMT",
                2.79
            ],
            [
                221,
                "Tue, 16 Mar 2021 00:00:00 GMT",
                5.04
            ],
            [
                223,
                "Thu, 18 Mar 2021 00:00:00 GMT",
                3.83
            ],
            [
                233,
                "Thu, 01 Apr 2021 00:00:00 GMT",
                3.59
            ],
            [
                246,
                "Wed, 21 Apr 2021 00:00:00 GMT",
                2.54
            ],
            [
                248,
                "Fri, 23 Apr 2021 00:00:00 GMT",
                5.82
            ]
        ]
    }
    result = support_resistance_script(sr_lines['result'])
    print(result)
