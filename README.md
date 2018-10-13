# PDF Crawler
This is SimFin's open source PDF crawler. Can be used to crawl all PDFs from a website.

You specify a starting page and all pages that link from that page are crawled (ignoring links that lead to other pages, while still fetching PDFs that are linked on the original page but hosted on a different domain).

Can crawl files "hidden" with javascript too (the crawler can render the page).

We use this crawler to gather PDFs from company websites to find financial reports that are then uploaded to SimFin, but can be used for other documents too.

# Development

How to install pdf-extractor for development.

```bash
$ git clone git@github.com:SimFin/pdf-crawler.git
$ cd pdf-crawler

# Make virtualenv with the tool of your choice. Please use Python version 3.6+
# Here example based on pyenv:
$ pyenv virtualenv 3.6.6 pdf-crawler
$ echo 'pdf-crawler' > .python-version

$ pip install -e .[tests]

# Run tests
$ py.test --pep8 --flakes --cov pdf_crawler
```

# Usage

For now follow the "Development" guide and run `pdf-extractor-crawl` command like this:

```bash
$ pdf-crawler {url to crawl} --depth {crawling depth} --pdfs-dir {directory for PDFs} --stats-dir {directory for CSVs with stats}

# eg.
$ pdf-crawler https://www.daimler.com/investors/ --depth 2 --pdfs-dir pdfs --stats-dir stats
```

# License
Available under MIT license

# Credits
Main author: @gwaramadze, contributors: @q7v6rhgfzc8tnj3d, @thf24