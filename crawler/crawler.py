from tqdm import tqdm
from crawler.helper import get_content_type, ensure_get_response, call
from crawler.crawl_methods import get_hrefs_html, get_hrefs_js, get_hrefs_js_boosted


class Crawler:
    def __init__(self, downloader, get_handlers=None, head_handlers=None, follow_foreign_hosts = False):

        # Crawler internals
        self.downloader = downloader
        self.get_handlers = get_handlers or {}
        self.head_handlers = head_handlers or {}
        self.session = self.downloader.session()

        # Crawler information
        self.get_handled = set()
        self.head_handled = set()
        self.follow_foreign = follow_foreign_hosts

    def crawl(self, url, depth, previous_url=None, follow=True):
        response = call(self.session.head, url) or call(self.session.get, url)
        if not response:
            return

        # Type of content on page at url
        content_type = get_content_type(response)

        # Name of pdf
        local_name = None

        get_handler = self.get_handlers.get(content_type)
        if get_handler and url not in self.get_handled:
            response = ensure_get_response(response, self.session)
            if response:
                local_name = get_handler.handle(response)
                self.get_handled.add(url)

        head_handler = self.head_handlers.get(content_type)
        if head_handler and url not in self.head_handled:
            head_handler.handle(response, depth, previous_url, local_name)
            self.head_handled.add(url)

        if content_type == "text/html" and depth and follow:
            response = ensure_get_response(response, self.session)
            if not response:
                return
            depth -= 1
            urls = self.get_urls(response, method="html")
            for next_url in tqdm(urls):
                self.crawl(next_url['url'], depth, previous_url=url, follow=next_url['follow'])

    def get_urls(self, response, method="html"):
        if method == "html":
            urls = get_hrefs_html(response,self.follow_foreign)
        elif method == "javascript":
            urls = get_hrefs_js(response,self.follow_foreign)
        elif method == "javascript_boosted":
            urls = get_hrefs_js_boosted(response,self.follow_foreign)
        else:
            print("No valid scrape method.")
            return

        return urls
