import requests
from alpaca import JsonFavorite
import os
import logging
from .environ import EnvFile

def PushToServer(dest = None):
    logging.info('start push.')
    url = EnvFile.Get(
        'PUSH_URL', 'https://simp-admin.herokuapp.com/api/symbols/1')
    content = JsonFavorite(filename='symbols.json')
    data = content.GetJson
    r = requests.put(url, json=data)

    # print(f"Status Code: {r.status_code}, Response: {r.json()}")
    logging.info(f"Status Code: {r.status_code}")
    logging.info('complete.  exiting.')
