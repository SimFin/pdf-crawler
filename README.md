# PDF Crawler
This is SimFin's open source PDF crawler. Can be used to crawl all PDFs from a website.

You specify a starting page and all pages that link from that page are crawled (ignoring links that lead to other pages, while still fetching PDFs that are linked on the original page but hosted on a different domain).

Can crawl files "hidden" with javascript too (the crawler can render the page and click on all elements to make new links appear).

We use this crawler to gather PDFs from company websites to find financial reports that are then uploaded to SimFin, but can be used for other documents too.

# Development

How to install pdf-extractor for development.

```bash
$ git clone https://github.com/SimFin/pdf-crawler.git
$ cd pdf-crawler

# Make a virtual environment with the tool of your choice. Please use Python version 3.6+
# Here an example based on pyenv:
$ pyenv virtualenv 3.6.6 pdf-crawler

$ pip install -e .[tests]

```

# Usage Example

After having installed pdf-crawler as described in the "Development" section, you can import and use the crawler class like so:

```python
import crawler

crawler.crawl(url="https://simfin.com/crawlingtest/",output_dir="crawling_test",method="rendered-all")
```

## Parameters

<ul>
<li><b>url</b> - the url to crawl</li>
<li><b>output_dir</b> - the directory where the files should be saved</li>
<li><b>method</b> - the method to use for the crawling, has 3 possible values: <b>normal</b> (plain HTML crawling), <b>rendered</b> (renders the HTML page, so that frontend SPA frameworks like Angular, Vue etc. get read properly) and <b>rendered-all</b> (renders the HTML page and clicks on all elements that can be clicked on (buttons etc.) to make appear links that are hidden somewhere)</li>
<li><b>depth</b> - the "depth" to crawl, refers to the number of sub-pages the crawler goes to before it stops. Default is 2.</li>
<li><b>gecko_path</b> - if you choose the crawling method "rendered-all", you have to install Firefox's headless browser Gecko. You can specify the location to the executable that you downloaded here.</li>
</ul>

# License
Available under MIT license

# Credits
<a href="https://github.com/gwaramadze">@gwaramadze</a>, <a href="https://github.com/q7v6rhgfzc8tnj3d">@q7v6rhgfzc8tnj3d</a>, <a href="https://github.com/thf24">@thf24</a>