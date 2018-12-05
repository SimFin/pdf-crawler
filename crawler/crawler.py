import os
import csv
import re

from crawler.helper import get_content_type, ensure_get_response, call
from crawler.crawl_methods import get_hrefs_html, get_hrefs_js_simple, get_hrefs_js_complex


class Crawler:
    def __init__(self, downloader, get_handlers=None, head_handlers=None, follow_foreign_hosts=False, crawl_method="normal", gecko_path="geckodriver"):

        # Crawler internals
        self.downloader = downloader
        self.get_handlers = get_handlers or {}
        self.head_handlers = head_handlers or {}
        self.session = self.downloader.session()

        # Crawler information
        self.handled = set()
        self.follow_foreign = follow_foreign_hosts
        self.executable_path_gecko = gecko_path
        # these file endings are excluded to speed up the crawling (assumed that urls ending with these strings are actual files)
        self.file_endings_exclude = [".mp3",".wav",".mkv",".flv",".vob",".ogv",".ogg",".gif",".avi",".mov",".wmv",".mp4",".mp3",".mpg"]

        # 3 possible values:
        # "normal" (default) => simple html crawling (no js),
        # "rendered" => renders page,
        # "rendered-all" => renders page and clicks all buttons/other elements to collect all links that only appear when something is clicked (javascript pagination etc.)
        self.crawl_method = crawl_method

        # load already handled files from folder if available
        for k, Handler in self.head_handlers.items():
            handled_list = Handler.get_handled_list()
            for handled_entry in handled_list:
                self.handled.add(handled_entry)

    def crawl(self, url, depth, previous_url=None, follow=True):

        url = clean_url(url)

        if url in self.handled or url[-4:] in self.file_endings_exclude:
            return

        response = call(self.session.head, url) or call(self.session.get, url)
        if not response:
            return

        # Type of content on page at url
        content_type = get_content_type(response)

        # Name of pdf
        local_name = None

        get_handler = self.get_handlers.get(content_type)
        if get_handler:
            response = ensure_get_response(response, self.session)
            if response:
                local_name = get_handler.handle(response)

        head_handler = self.head_handlers.get(content_type)
        if head_handler:
            head_handler.handle(response, depth, previous_url, local_name)

        if content_type == "text/html":
            if depth and follow:
                response = ensure_get_response(response, self.session)
                if not response:
                    return
                depth -= 1
                urls = self.get_urls(response)
                self.handled.add(response.url)
                for next_url in urls:
                    self.crawl(next_url['url'], depth, previous_url=url, follow=next_url['follow'])
        else:
            self.handled.add(response.url)

    def get_urls(self, response):

        if self.crawl_method == "rendered":
            urls = get_hrefs_js_simple(response, self.follow_foreign)
        elif self.crawl_method == "rendered-all":
            urls = get_hrefs_js_complex(response, self.follow_foreign, self.executable_path_gecko)
        else:
            # plain html
            if self.crawl_method is not None and self.crawl_method != "normal":
                print("Invalid crawl method specified, default used (normal)")
            urls = get_hrefs_html(response, self.follow_foreign)

        return urls


def clean_url(url):

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
