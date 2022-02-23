import requests
from .favorites import JsonFavorite
import os
from .environ import EnvFile

def PushToServer(content=None, dest = None):
    print('start push.')
    url = EnvFile.Get(
        'PUSH_URL', 'https://simp-admin.herokuapp.com/api/symbols/1') if dest is None else dest
    if content is None:
        content = JsonFavorite(filename='symbols.json')
        data = content.GetJson
    else:
        data = content
    r = requests.put(url, json=data)

    # print(f"Status Code: {r.status_code}, Response: {r.json()}")
    print(f"Status Code: {r.status_code}")
    print('complete.  exiting.')
