from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from newspaper import Article

from datahtml.base import CrawlerSpec


@dataclass
class ArticleData:
    url: str
    text: str
    html: str
    img: Optional[str] = None
    publish_date: Optional[datetime] = None

    @classmethod
    def from_html(cls, url: str, html: str) -> "ArticleData":
        a = Article(url=url)
        a.download(input_html=html)
        a.parse()
        return cls(url=url, text=a.text, publish_date=a.publish_date,
                   html=html,
                   img=a.top_image)

    @classmethod
    def from_url(cls, url: str, *, crawler: CrawlerSpec) -> "ArticleData":
        rsp = crawler.get(url)
        return cls.from_html(url=url, html=rsp.text)
