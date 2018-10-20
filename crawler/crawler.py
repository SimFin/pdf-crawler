from tqdm import tqdm
from crawler.helper import get_content_type, ensure_get_response, call
from crawler.crawl_methods import get_hrefs_html, get_hrefs_js_simple, get_hrefs_js_complex


class Crawler:
    def __init__(self, downloader, get_handlers=None, head_handlers=None, follow_foreign_hosts=False, crawl_method="normal"):

        # Crawler internals
        self.downloader = downloader
        self.get_handlers = get_handlers or {}
        self.head_handlers = head_handlers or {}
        self.session = self.downloader.session()

        # Crawler information
        self.get_handled = set()
        self.head_handled = set()
        self.follow_foreign = follow_foreign_hosts

        # 3 possible values:
        # "normal" (default) => simple html crawling (no js),
        # "rendered" => renders page,
        # "rendered-all" => renders page and clicks all buttons/other elements to collect all links that only appear when something is clicked (javascript pagination etc.)
        self.crawl_method = crawl_method

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
            urls = self.get_urls(response)
            for next_url in tqdm(urls):
                self.crawl(next_url['url'], depth, previous_url=url, follow=next_url['follow'])

    def get_urls(self, response):

        if self.crawl_method == "rendered":
            urls = get_hrefs_js_simple(response, self.follow_foreign)
        elif self.crawl_method == "rendered-all":
            urls = get_hrefs_js_complex(response, self.follow_foreign)
        else:
            # plain html
            if self.crawl_method is not None and self.crawl_method != "normal":
                print("Invalid crawl method specified, default used (normal)")
            urls = get_hrefs_html(response, self.follow_foreign)

        return urls
