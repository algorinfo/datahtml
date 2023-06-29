import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import feedparser
from dateutil.parser import parse as dtparser

from datahtml import errors, types
from datahtml.base import CrawlerSpec

# from datahtml.web import Web


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


def parse_as_dict(xmlcontent: str) -> List[Dict[str, Any]]:
    feed = feedparser.parse(xmlcontent)
    return feed["entries"]


def find_rss_realated_links(links: List[types.Link]):
    rss_links = set()
    for link in links:
        if link.internal and "rss" in link.href or "feed" in link.href:
            rss_links.add(link.href)
    return rss_links


def download_as_dict(url, *, crawler: CrawlerSpec) -> List[Dict[str, Any]]:
    """
    Get and parse the rss feed from a URL.

    IT returns a dict which is very close to the original parsed feed using
    the feedparser library.
    """
    rsp = crawler.get(url)
    if not rsp.is_xml:
        raise errors.XMLContentNotFound(url)

    data = parse_as_dict(rsp.text)
    return data


def download(url, *, crawler: CrawlerSpec) -> List[Entry]:
    """
    Get and parse the rss feed from a URL.

    It returns a list of Entry
    """
    rsp = crawler.get(url)
    if not rsp.is_xml:
        raise errors.XMLContentNotFound(url)

    data = parse(rsp.text)
    return data
