import logging
from functools import lru_cache
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

log = logging.getLogger(__name__)


class Crawler:

    def __init__(self, downloader, get_handlers=None, head_handlers=None):
        self.downloader = downloader
        self.get_handlers = get_handlers or {}
        self.head_handlers = head_handlers or {}

    def crawl(self, url, depth):
        session = self.downloader.session()
        get_handled = set()
        head_handled = set()
        self._crawl(url, get_handled, head_handled, session, depth)

    def _crawl(self, url, get_handled, head_handled, session, depth,
               previous_url=None, follow=True):
        response = _call(session.head, url) or _call(session.get, url)
        if not response:
            return

        content_type = _get_content_type(response)

        local_name = None
        get_handler = self.get_handlers.get(content_type)
        if get_handler and url not in get_handled:
            response = _ensure_get_response(response, session)
            if response:
                local_name = get_handler.handle(response)
                get_handled.add(url)

        head_handler = self.head_handlers.get(content_type)
        if head_handler and url not in head_handled:
            head_handler.handle(response, depth, previous_url, local_name)
            head_handled.add(url)

        if content_type == 'text/html' and depth and follow:
            response = _ensure_get_response(response, session)
            if not response:
                return
            depth -= 1
            urls = _find_urls(response)
            for next_url in tqdm(urls):
                self._crawl(next_url['url'], get_handled, head_handled, session,
                            depth, previous_url=url,follow=next_url['follow'])


def _get_content_type(response):
    content_type = response.headers.get('Content-Type')
    if content_type:
        return content_type.split(';')[0]


def _ensure_get_response(response, session):
    request = response.request
    if request.method == 'GET':
        return response

    response = _call(session.get, request.url)
    if not response:
        log.debug('TODO: No GET response after HEAD. This request should '
                  f'normally be retried or otherwise handled: {request.url}')

    return response


@lru_cache(maxsize=8192)
def _call(func, url):
    try:
        response = func(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    else:
        return response


def _find_urls(response, deep_search=False):
    parsed_response_url = urlparse(response.url)
    soup = BeautifulSoup(response.text, 'lxml')
    hrefs = {a.attrs.get('href') for a in soup.find_all('a')}
    urls = []
    for href in hrefs:

        follow = True

        # parse url
        parsed = urlparse(href)

        # if no relative directory/path, skip that link
        if not parsed.path:
            continue

        # if no base directory/path, add the response basepath and reparse the url
        if not parsed.netloc:
            href = urljoin(response.url, parsed.path)
            parsed = urlparse(href)

        if parsed_response_url.netloc != parsed.netloc and not deep_search:
            follow = False

        urls.append({"url":parsed.geturl(),"follow":follow})

    return urls
