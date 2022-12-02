from typing import Any, Dict, List, Optional

from datahtml import errors, parsers, types
from datahtml.base import CrawlerSpec


class Web:
    def __init__(self, url, *, html_txt, is_root=False):
        self.url: types.URL = parsers.parse_url(url)
        self._html = html_txt
        self.soup = parsers.text2soup(html_txt)
        self.is_root = is_root

    @classmethod
    def parse(
        cls,
        url: str,
        *,
        crawler: CrawlerSpec,
        is_root=False,
    ) -> "Web":
        rsp = crawler.get(url)
        obj = cls(url=url, html_txt=rsp.text, is_root=is_root)
        return obj

    def links(self) -> List[types.Link]:
        links = parsers.extract_links(self.soup, fullurl=self.url.fullurl)
        return links

    def images(self) -> List[types.Image]:
        return parsers.extract_images(self.soup)

    def ld_json(self) -> Dict[str, Any]:
        return parsers.extract_ld_json(self.soup)

    def meta_og(
        self, keys=["og:url", "og:image", "og:description", "og:type"]
    ) -> Dict[str, str]:
        return parsers.extract_meta_og(self.soup, meta=keys)


