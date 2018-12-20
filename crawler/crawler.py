from crawler.helper import get_content_type, call, clean_url
from crawler.crawl_methods import get_hrefs_html, get_hrefs_js_simple, ClickCrawler


class Crawler:
    def __init__(self, downloader, get_handlers=None, head_handlers=None, follow_foreign_hosts=False, crawl_method="normal", gecko_path="geckodriver", process_handler=None):

        # Crawler internals
        self.downloader = downloader
        self.get_handlers = get_handlers or {}
        self.head_handlers = head_handlers or {}
        self.session = self.downloader.session()
        self.process_handler = process_handler

        # Crawler information
        self.handled = set()
        self.follow_foreign = follow_foreign_hosts
        self.executable_path_gecko = gecko_path
        # these file endings are excluded to speed up the crawling (assumed that urls ending with these strings are actual files)
        self.file_endings_exclude = [".mp3", ".wav", ".mkv", ".flv", ".vob", ".ogv", ".ogg", ".gif", ".avi", ".mov", ".wmv", ".mp4", ".mp3", ".mpg"]

        # 3 possible values:
        # "normal" (default) => simple html crawling (no js),
        # "rendered" => renders page,
        # "rendered-all" => renders page and clicks all buttons/other elements to collect all links that only appear when something is clicked (javascript pagination etc.)
        self.crawl_method = crawl_method

        # load already handled files from folder if available
        for k, Handler in self.head_handlers.items():
            handled_list = Handler.get_handled_list()
            for handled_entry in handled_list:
                self.handled.add(clean_url(handled_entry))

    def crawl(self, url, depth, previous_url=None, follow=True):

        url = clean_url(url)

        if url in self.handled or url[-4:] in self.file_endings_exclude:
            return

        response = call(self.session, url)
        if not response:
            return

        final_url = clean_url(response.url)

        if final_url in self.handled or final_url[-4:] in self.file_endings_exclude:
            return

        print(final_url)

        # Type of content on page at url
        content_type = get_content_type(response)

        # Name of pdf
        local_name = None

        get_handler = self.get_handlers.get(content_type)
        if get_handler:
            local_name = get_handler.handle(response)

        head_handler = self.head_handlers.get(content_type)
        if head_handler:
            head_handler.handle(response, depth, previous_url, local_name)

        if content_type == "text/html":
            if depth and follow:
                depth -= 1
                urls = self.get_urls(response)
                self.handled.add(final_url)
                for next_url in urls:
                    self.crawl(next_url['url'], depth, previous_url=url, follow=next_url['follow'])
        else:
            self.handled.add(final_url)

    def get_urls(self, response):

        if self.crawl_method == "rendered":
            urls = get_hrefs_js_simple(response, self.follow_foreign)
        elif self.crawl_method == "rendered-all":
            click_crawler = ClickCrawler(self.process_handler, self.executable_path_gecko, response, self.follow_foreign)
            urls = click_crawler.get_hrefs_js_complex()
        else:
            # plain html
            if self.crawl_method is not None and self.crawl_method != "normal":
                print("Invalid crawl method specified, default used (normal)")
            urls = get_hrefs_html(response, self.follow_foreign)

        return urls
