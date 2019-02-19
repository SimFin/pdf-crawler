import logging
from functools import lru_cache
from crawler.proxy import ProxyManager
import re
from urllib.parse import urlparse,urlunparse

pm = ProxyManager()
log = logging.getLogger(__name__)

def clean_url(url):

    parsed = urlparse(url)

    # add scheme if not available
    if not parsed.scheme:
        parsed = parsed._replace(scheme="http")

        url = urlunparse(parsed)

    # clean text anchor from urls if available
    pattern = r'(.+)(\/#[a-zA-Z0-9]+)$'
    m = re.match(pattern, url)

    if m:
        return m.group(1)
    else:
        # clean trailing slash if available
        pattern = r'(.+)(\/)$'
        m = re.match(pattern, url)

        if m:
            return m.group(1)

    return url


def get_content_type(response):
    content_type = response.headers.get("content-type")
    if content_type:
        return content_type.split(';')[0]


@lru_cache(maxsize=8192)
def call(session, url, use_proxy=False, retries=0):
    if use_proxy:
        proxy = pm.get_proxy()
        if proxy[0]:
            try:
                response = session.get(url, timeout=5, proxies=proxy[0], verify=False)
                response.raise_for_status()
            except Exception as e:
                if retries <= 3:
                    pm.change_proxy(proxy[1])
                    return call(session, url, True, retries + 1)
                else:
                    return None
            else:
                return response
        else:
            return None
    else:
        try:
            response = session.get(url, timeout=5, verify=False)
            response.raise_for_status()
        except Exception as e:
            # try with proxy
            return call(session,url,use_proxy=True)
        else:
            return response
