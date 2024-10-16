from datetime import datetime
from typing import List, Optional, Union

from dateutil.parser import parse as dtparser
from attrs import define

from datahtml.base import CrawlerSpec
from datahtml.parsers import text2soup

URL = "https://trends.google.com/trending/rss?geo="


def _dt_parser(published) -> Union[datetime, None]:
    dt = None
    try:
        dt = dtparser(published)
    except ValueError:
        pass
    except TypeError:
        pass
    return dt


@define
class NewsItem:
    title: str
    snippet: str
    url: str
    source: str

@define
class GoogleTrend:
    title: str
    aprox_traffic: str
    description: str
    news: List[NewsItem]
    pubdate: Optional[datetime] = None
    picture: Optional[str] = None


@define
class GoogleTrendList:
    geo: str
    trends: List[GoogleTrend]


def parse_news_item(i) -> NewsItem:
    title = i.find("ht:news_item_title").text
    snippet = i.find("ht:news_item_snippet").text
    url = i.find("ht:news_item_url").text
    source = i.find("ht:news_item_source").text
    return NewsItem(title=title, snippet=snippet, url=url, source=source)


def parse_entries(soup) -> List[GoogleTrend]:
    entries = soup.find_all("item")
    trends = []
    for e in entries:
        news_items = e.find_all("ht:news_item")
        news = [parse_news_item(ni) for ni in news_items]
        title = e.title.text
        desc = e.description.text
        pubdate = _dt_parser(e.pubdate.text)
        traffic = e.find("ht:approx_traffic").text
        picture = None
        _p = e.find("ht:picture")
        if _p:
            picture = _p.text
        gt = GoogleTrend(
            title=title,
            description=desc,
            aprox_traffic=traffic,
            pubdate=pubdate,
            picture=picture,
            news=news,
        )
        trends.append(gt)
    return trends


def download(
    geo: str,
    *,
    crawler: CrawlerSpec,
    url: str = URL, 
) -> List[GoogleTrend]:
    rsp = crawler.get(f"{url}{geo.upper()}")
    soup = text2soup(rsp.text)
    trends = parse_entries(soup)
    return trends
