import random
import os
from requests_html import HTMLSession


def get_user_agent():
    dirname = os.path.dirname(__file__)
    file_loc = os.path.join(dirname, '.user_agents')
    ua_file = open(file_loc, 'r')
    user_agents = ua_file.read().splitlines()
    ua_file.close()
    return random.choice(user_agents)


class RequestsDownloader:

    def session(self):
        session = HTMLSession()
        session.headers = self._get_fake_headers()
        return session

    def _get_fake_headers(self):
        return {
            'User-Agent': get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache',
        }
