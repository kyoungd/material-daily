import json
from dbase import MarketDataDb


app = MarketDataDb()
symbols = app.AllAVailableSymbols(timeframe='1Day')
for item in symbols:
    id, data = item
    value = json.dumps(data[1:])
    app.UpdateData(id, value)
