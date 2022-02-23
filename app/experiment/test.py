import pandas as pd
import requests
from _pickle import dump
import re

DEFAULT_TICKERS = ['goog', 'aapl']
URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
CIK_RE = re.compile(r'.CIK=(\d{10}).')

cik_dict = {}
for ticker in DEFAULT_TICKERS:
    f = requests.get(URL.format(ticker), stream=True)
    results = CIK_RE.findall(f.text)
    print (results)
