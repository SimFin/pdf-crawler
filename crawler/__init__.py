import logging
import sys
from urllib.parse import urlparse

from crawler.crawler import Crawler
from crawler.downloaders import RequestsDownloader
from crawler.handlers import (
    LocalStoragePDFHandler,
    CSVStatsPDFHandler,
    ProcessHandler,
    get_filename
)

logging.basicConfig(
    format='[%(asctime)s] %(message)s',
    level=logging.INFO,
    stream=sys.stdout,
)

requests_downloader = RequestsDownloader()


def crawl(url, output_dir, depth=2, method="normal", gecko_path="geckodriver", page_name=None, custom_stats_handler=None, custom_process_handler=None):
    head_handlers = {}
    get_handlers = {}

    # get name of page for sub-directories etc. if not custom name given
    if page_name is None:
        page_name = urlparse(url).netloc

    get_handlers['application/pdf'] = LocalStoragePDFHandler(
        directory=output_dir, subdirectory=page_name)

    if custom_stats_handler is None:
        head_handlers['application/pdf'] = CSVStatsPDFHandler(directory=output_dir, name=page_name)
    else:
        for content_type, Handler in custom_stats_handler.items():
            head_handlers[content_type] = Handler

    if custom_process_handler is None:
        process_handler = ProcessHandler()
    else:
        process_handler = custom_process_handler

    if not get_handlers and not head_handlers:
        raise ValueError('You did not specify any output')

    crawler = Crawler(
        downloader=requests_downloader,
        head_handlers=head_handlers,
        get_handlers=get_handlers,
        follow_foreign_hosts=False,
        crawl_method=method,
        gecko_path=gecko_path,
        process_handler=process_handler
    )
    crawler.crawl(url, depth)
