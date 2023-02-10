# datahtml

[![PyPI - Version](https://img.shields.io/pypi/v/datahtml.svg)](https://pypi.org/project/datahtml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/datahtml.svg)](https://pypi.org/project/datahtml)
[![readthedocs](https://readthedocs.org/projects/datahtml/badge/?version=latest)](https://datahtml.readthedocs.io/en/latest/)

-------

**datahtml** is a library for crawling and extraction of data from html and xml content. 

Datahtml lets you:

* Extract ld+json data from html
* Extract frequently used meta tags from html (those that are used for SEO and social media, between others)
* Extract Article data from a html, usually from Newspaper sites
* Parse RSS feeds from sites
* Crawl some specific social media sites like google and youtube

Under the hood datahtml uses libraries like BeautifoulSoup, Newspaper2k, feedparser between others, but
datahtml takes an opinionated approach for crawling based on our expriencies doing so. 



## Quickstart

```console
pip install datahtml
```

```python

from datahtml import web, crawler

c = crawler.LocalCrawler()
w = web.download("https://www.infobae.com", crawler=c)
w.links()
```

## License

`datahtml` is distributed under the terms of the [MPL-2.0](https://www.mozilla.org/en-US/MPL/2.0/) license.
