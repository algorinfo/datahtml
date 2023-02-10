import re
from dataclasses import dataclass
from typing import List
from urllib.parse import parse_qs, quote, urlparse

from bs4 import BeautifulSoup as BS

from datahtml.base import CrawlerSpec

_G = "https://www.google.com/search?q="
_BLACKLIST = [
    "gstatic",
    "w3.org",
    "google.com",
    "googleapis.com",
    "googleadservices.com",
    "ytimg.com",
    "googleusercontent.com",
    "schema.org",
]
_REGEX = "(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+"


LANGS = dict(es="tbs=lr:lang_1es&lr=lang_es", pt="tbs=lr:lang_1pt&lr=lang_pt")


@dataclass
class GLink:
    url: str
    text: str


@dataclass
class SearchResult:
    links: List[GLink]
    related: List[str]


def _valid_url(url) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "" and parsed.netloc != "":
        invalid = False
        for u in _BLACKLIST:
            if u in parsed.netloc:
                invalid = True
                break
        if invalid:
            return False
        return True


def _get_possible_url(text):
    u = urlparse(text)
    possible_url = parse_qs(u.query).get("q")
    if possible_url:
        return possible_url[0]
    return None


def _get_possible_related(text):
    if text.startswith("/search"):
        u = urlparse(text)
        related = parse_qs(u.query).get("q")
        if related:
            return related[0]
    return None


def words2url(words: str, lang=None):
    _quoted = quote(words)

    fullurl = f"{_G}{_quoted}"
    if lang:
        extra_param = LANGS[lang.lower()]
        fullurl = f"{fullurl}&{extra_param}"

    return fullurl


def transform_result_simple(html) -> List[str]:
    urls = re.findall(_REGEX, html)
    final = set()
    for u in urls:
        url = _valid_url(u)
        if url:
            final.add(u)
    return list(final)


def transform_result(html) -> SearchResult:
    soup = BS(html, "lxml")
    links = soup.find_all(href=True)
    v2 = []
    for x in links:
        u = _get_possible_url(x["href"])
        if u and _valid_url(u):
            v2.append(GLink(url=u, text=x.text))

    related = set()
    for x in links:
        r = _get_possible_related(x["href"])
        if r:
            related.add(r)
    return SearchResult(links=v2, related=list(related))


def search(words: str, *, crawler: CrawlerSpec, lang=None) -> SearchResult:
    u = words2url(words, lang=lang)
    r = crawler.get(u)
    gr = transform_result(r.text)
    return gr
