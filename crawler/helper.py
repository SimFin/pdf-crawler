import logging
from functools import lru_cache


log = logging.getLogger(__name__)

def get_content_type(response):
	content_type = response.headers.get("content-type")
	if content_type:
		return content_type.split(';')[0]

@lru_cache(maxsize=8192)
def call(func, url):
	try:
		response = func(url,timeout=5)
		response.raise_for_status()
	except Exception:
		return None
	else:
		return response
