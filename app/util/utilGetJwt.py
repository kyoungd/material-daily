import logging
import requests
from environ import EnvFile
from datetime import datetime
import os

class GetJwtFromSite:
    jwt = None
    jwtFrom = None

    def __init__(self):
        self.url = os.environ.get('URL_JWT_AUTH', 'http://localhost:1337/api/auth/local')
        self.username = os.environ.get('URL_JWT_USERNAME', 'courage')
        self.password = os.environ.get('URL_JWT_PASSWORD', 'password')

    def start(self):
        try:
            data = {
                    'identifier': self.username,
                    'password': self.password
            }
            r = requests.post(self.url, json=data)
            result = r.json()
            return result['jwt']
        except Exception as e:
            print(e)
            logging.error(e)
            return None

    @staticmethod
    def run() -> str:
        if GetJwtFromSite.jwt is None:
            logging.info("GetJwtFromSite.run")
            candidate = GetJwtFromSite()
            GetJwtFromSite.jwtFrom = datetime.now()
            GetJwtFromSite.jwt = candidate.start()
        return GetJwtFromSite.jwt


if __name__ == '__main__':
    print("utilGetJwt.py")
