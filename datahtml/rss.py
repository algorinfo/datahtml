import logging
from dataclasses import dataclass
from typing import List, Optional

import feedparser
from dateutil.parser import parse as dtparser

from datahtml import errors, types
from datahtml.base import CrawlerSpec
from datahtml.web import Web


@dataclass
class Entry:
    link: str
    title: Optional[str] = None
    published: Optional[str] = None
    author: Optional[str] = None

    def __hash__(self):
        return hash(self.link)


@dataclass
class RSSLink:
    """URL of the feed and the xml content of it"""

    url: str
    xmlcontent: str

    def parse(self) -> List[Entry]:
        entries = parse(self.xmlcontent)
        return entries


def parse(xmlcontent: str) -> List[Entry]:
    feed = feedparser.parse(xmlcontent)
    entries = []
    for e in feed["entries"]:
        # print(e.keys())
        title = e.get("title")
        published = e.get("published")
        dt = None
        try:
            _dt = dtparser(published)
            dt = _dt.isoformat()
        except ValueError:
            pass
        except TypeError:
            pass
        try:
            _link = e["link"]
            author = e.get("author")
            _entry = Entry(link=_link, title=title, author=author, published=dt)
            entries.append(_entry)
        except KeyError:
            pass

    return entries


def _find_rss_realated_links(links: List[types.Link]):
    rss_links = set()
    for link in links:
        if link.internal and "rss" in link.href or "feed" in link.href:
            rss_links.add(link.href)
    return rss_links


def find_rss_links(url, *, crawler: CrawlerSpec) -> List[RSSLink]:
    """Main method, it will scrap from the url provided looking for links related
    to rss feed. If it found rss links then, it will try to get the feed.
    """
    rss: List[RSSLink] = []
    _urls = set()
    _parsed = set()
    # breakpoint()
    # print(url)
    w = Web.parse(url=url, crawler=crawler)

    rss_links = _find_rss_realated_links(w.links())
    for x in rss_links:
        if x not in _parsed:
            # print(x)
            # req = fetch.from_url(x)
            try:
                possible = crawler.get(x)
                _parsed.add(x)

                if possible.is_xml:
                    if x not in _urls:
                        _urls.add(x)
                        rss.append(RSSLink(url=x, xmlcontent=possible.text))
                else:
                    w2 = Web(x, html_txt=possible.text)
                    rss_links2 = _find_rss_realated_links(w2.links())
                    for y in rss_links2:
                        if y not in _parsed:
                            # print(y)
                            possible2 = crawler.get(y)
                            _parsed.add(y)
                            try:
                                if possible2.is_xml:
                                    if y not in _urls:
                                        _urls.add(y)
                                        rss.append(
                                            RSSLink(url=y, xmlcontent=possible2.text)
                                        )
                            except KeyError:
                                pass
            except errors.CrawlHTTPError as e:
                print(e)
    return rss
