import random

import requests
from fake_useragent import UserAgent


class RequestsDownloader:

    def session(self):
        session = requests.Session()
        session.headers = self._get_fake_headers()
        return session

    def _get_fake_headers(self):
        return {
            'User-Agent': self._get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache',
        }

    def _get_user_agent(self):
        try:
            ua_file = open('.user_agents', 'r')
            user_agents = ua_file.read().splitlines()
        except FileNotFoundError:
            ua_file = open('.user_agents', 'w')
            ua = UserAgent()
            user_agents = ua.data_browsers['chrome']
            for user_agent in user_agents:
                ua_file.write(f'{user_agent}\n')
        finally:
            ua_file.close()
            return random.choice(user_agents)
