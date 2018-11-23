import logging
from functools import lru_cache


log = logging.getLogger(__name__)

def get_content_type(response):
	content_type = response.headers.get("Content-Type")
	if content_type:
		return content_type.split(';')[0]

def ensure_get_response(response, session):
	request = response.request
	if request.method == "GET":
		return response

	response = call(session.get, request.url)
	if not response:
		log.debug("TODO: No GET response after HEAD. This request should"
				  f"normally be retried or otherwise handled: {request.url}")

	return response

@lru_cache(maxsize=8192)
def call(func, url):
	try:
		response = func(url,timeout=5)
		response.raise_for_status()
	except Exception:
		return None
	else:
		return response
