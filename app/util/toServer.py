import requests
import logging
from .favorites import JsonFavorite
import os
from .environ import EnvFile

def PushToServer(content=None, dest = None):
    print('start push.')
    try:
        url = EnvFile.Get(
            'PUSH_URL', 'https://simp-admin.herokuapp.com/api/symbols/1') if dest is None else dest
        if content is None:
            content = JsonFavorite(filename='symbols.json')
            data = content.GetJson
        else:
            data = content
        r = requests.put(url, json=data)

        # print(f"Status Code: {r.status_code}, Response: {r.json()}")
        logging.info(f"PushToServer. Status Code: {r.status_code}")
        print(f"Status Code: {r.status_code}")
        print('complete.  exiting.')
    except Exception as e:
        logging.error(f"PushToServer. Exception: {e}")
        print(f"PushToServer. Exception: {e}")
        print('error.  exiting.')
