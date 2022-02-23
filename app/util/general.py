from datetime import datetime

class UtilGeneral:

    @staticmethod
    def days_between(d1, d2):
        d1 = datetime.strptime(d1.iloc[0].split('T')[0], "%Y-%m-%d")
        d2 = datetime.strptime(d2.iloc[0].split('T')[0], "%Y-%m-%d")
        return abs((d2 - d1).days)
