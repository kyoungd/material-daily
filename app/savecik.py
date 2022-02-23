import pandas as pd
from dbase import SecDb

# read text file seperated by tab
db = SecDb()

# cikCode = db.get_cik('aapl')
# print(cikCode)

# print('done')

df = pd.read_csv('./app/dbase/cik-ticker.txt', sep='\t', header=None)
df.columns = ['symbol', 'cik']
for item in df.iterrows():
    try:
        symbol = item[1]['symbol'].upper()
        cik = item[1]['cik']
        print(symbol, cik)
        db.save_cik(symbol, cik)
    except Exception as e:
        print(e)
