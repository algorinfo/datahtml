from typing import Any, Dict, List, Optional

from datahtml import errors, news, parsers, rss, sitemap, types
from datahtml._utils import difference_from_now
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

    def article(self) -> news.ArticleData:
        ad = news.ArticleData.from_html(url=self.url, html=self._html)
        return ad


def download(
    url: str,
    *,
    crawler: CrawlerSpec,
    is_root=True,
) -> Web:
    rsp = crawler.get(url)
    w = Web(url=url, html_txt=rsp.text, is_root=is_root)
    return w


def build_sitemap(
    url, *, crawler: CrawlerSpec, filter_dt=1
) -> List[sitemap.SitemapLink]:
    rsp_txt = crawler.get(f"{url.strip()}/robots.txt")
    sitesmaps = sitemap.get_sitemaps_from_robots(rsp_txt.text)

    total_sites = []
    for site in sitesmaps:
        w = download(site, crawler=crawler)
        urls = w.soup.findAll("url")
        if urls:
            sites = sitemap.parse_sitemap_links(urls)
            total_sites.extend(sites)
        else:
            # breakpoint()
            # locs = s.findAll("loc")
            # for l in locs:
            xmlsites = w.soup.findAll("sitemap")
            for site2 in xmlsites:
                try:
                    diff = difference_from_now(site2.lastmod.text)
                    if diff.days <= filter_dt:
                        _w = download(site2.loc.text, crawler=crawler)
                        # _w = Web.parse(site2.loc.text, crawler=crawler)
                        if _w.soup:
                            _urls = _w.soup.findAll("url")
                            sites = sitemap.parse_sitemap_links(_urls)
                            total_sites.extend(sites)
                except AttributeError:
                    pass
    return total_sites


def find_rss_links(url, *, crawler: CrawlerSpec, web: Web = None) -> List[rss.RSSLink]:
    """Main method, it will scrap from the url provided looking for links related
    to rss feed. If it found rss links then, it will try to get the feed.
    """
    _rss: List[rss.RSSLink] = []
    _urls = set()
    _parsed = set()
    # breakpoint()
    # print(url)
    # w = Web.parse(url=url, crawler=crawler)
    w = web or download(url=url, crawler=crawler)

    rss_links = rss.find_rss_realated_links(w.links())
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
                        _rss.append(rss.RSSLink(url=x, xmlcontent=possible.text))
                else:
                    w2 = Web(x, html_txt=possible.text)
                    rss_links2 = rss.find_rss_realated_links(w2.links())
                    for y in rss_links2:
                        if y not in _parsed:
                            # print(y)
                            possible2 = crawler.get(y)
                            _parsed.add(y)
                            try:
                                if possible2.is_xml:
                                    if y not in _urls:
                                        _urls.add(y)
                                        _rss.append(
                                            rss.RSSLink(
                                                url=y, xmlcontent=possible2.text
                                            )
                                        )
                            except KeyError:
                                pass
            except errors.CrawlHTTPError as e:
                print(e)
    return _rss
