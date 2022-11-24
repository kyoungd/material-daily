import yfinance as yf

def GetHisotricalCommodities(symbol):
    stock = yf.Ticker(symbol)

    hist = stock.history(period="1y")
    # show actions (dividends, splits)
    stock.actions

    print(stock.info['sector'])
    print(stock.info['industry'])
    print(stock.info['close'])
    result = []
    result.add({
        'symbol': stock.info['symbol'], 
        'sector': stock.info['sector'], 
        'industry': stock.info['industry'], 
        'close': stock.info['close'],
        'volume': stock.info['volume'],
        })
    
    for _, row in hist.iterrows():
        print(str(row.name))
        result.append({'t': str(row.name), 'o': row.Open, 'h': row.High, 'l': row.Low, 'c': row.Close, 'v': row.Volume})
    print(result[::-1])
    return result[::-1]

def GetSnapshotCommodities(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1day")
    for _, row in hist.iterrows():
        return {'t': str(row.name), 'o': row.Open, 'h': row.High, 'l': row.Low, 'c': row.Close, 'v': row.Volume}


historicals = GetHisotricalCommodities('MSFT')
print(historicals)
print('-----------------------------------------------------')
snapshot = GetSnapshotCommodities('MSFT')
print(snapshot)
print('done')

# # show dividends
# stock.dividends

# # show splits
# stock.splits

# # show financials
# stock.financials
# stock.quarterly_financials

# # show major holders
# stock.major_holders

# # show institutional holders
# stock.institutional_holders

# # show balance sheet
# stock.balance_sheet
# stock.quarterly_balance_sheet

# # show cashflow
# stock.cashflow
# stock.quarterly_cashflow

# # show earnings
# stock.earnings
# stock.quarterly_earnings

# # show sustainability
# stock.sustainability

# # show analysts recommendations
# stock.recommendations

# # show next event (earnings, etc)
# stock.calendar

# # show ISIN code - *experimental*
# # ISIN = International Securities Identification Number
# stock.isin

# # show options expirations
# stock.options

# # show news
# stock.news

# # get option chain for specific expiration
# opt = stock.option_chain('YYYY-MM-DD')
# # data available via: opt.calls, opt.puts
