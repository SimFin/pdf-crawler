import logging
import sys

import click

from crawler.crawler import Crawler
from crawler.downloaders import RequestsDownloader
from crawler.handlers import (
    LocalStoragePDFHandler,
    CSVStatsPDFHandler,
)

logging.basicConfig(
    format='[%(asctime)s] %(message)s',
    level=logging.INFO,
    stream=sys.stdout,
)

requests_downloader = RequestsDownloader()


@click.command()
@click.argument('url')
@click.option('--depth', '-d', type=int)
@click.option('--pdfs-dir')
@click.option('--pdfs-subdir')
@click.option('--stats-dir')
@click.option('--stats-name')
@click.option('--method')
def crawl(url, depth,
          pdfs_dir=None, pdfs_subdir=None,
          stats_dir=None, stats_name=None, method="normal"):
    head_handlers = {}
    get_handlers = {}

    if pdfs_dir:
        get_handlers['application/pdf'] = LocalStoragePDFHandler(
            directory=pdfs_dir, subdirectory=pdfs_subdir)

    if stats_dir:
        head_handlers['application/pdf'] = CSVStatsPDFHandler(
            directory=stats_dir, name=stats_name)

    if not get_handlers and not head_handlers:
        raise ValueError('You did not specify any output')

    crawler = Crawler(
        downloader=requests_downloader,
        head_handlers=head_handlers,
        get_handlers=get_handlers,
        follow_foreign_hosts=False,
        crawl_method=method
    )
    crawler.crawl(url, depth)
