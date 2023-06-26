from typing import Any, Dict, List, Union

from datahtml import defaults, errors, news, parsers, rss, sitemap, types
from datahtml._utils import difference_from_now
from datahtml.base import CrawlerSpec


class WebDocument:
    """
    It's the main object for the library. It represents a HTML Document.
    This page could be a root link or a subpage.
    """

    def __init__(self, url: str, *, html_txt: str, is_root=False):
        """
        :param url: url where the document belongs.
        :type url: str
        :param html_txt: html text of the document.
        :type html_txt: str
        :param is_root: if is the root site or a subpage.
        :type is_root: bool
        """
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
    ) -> "WebDocument":
        """
        It crawl and parse a url passed.

        .. deprecated:: 0.3.0
           Use :func:`datahtml.web.download`

        """
        rsp = crawler.get(url)
        obj = cls(url=url, html_txt=rsp.text, is_root=is_root)
        return obj

    def social_urls(self) -> List[types.URL]:
        _socials = []
        for l in self.links():
            if not l.internal:
                try:
                    _url = parsers.parse_url(l.href)
                    if _url.is_social:
                        _socials.append(_url)
                except errors.URLParsingError:
                    pass

        return _socials

    def links(self) -> List[types.Link]:
        links = parsers.extract_links(self.soup, fullurl=self.url.fullurl.strip("/"))
        return links

    def images(self) -> List[types.Image]:
        return parsers.extract_images(self.soup)

    def ld_json(self) -> Dict[str, Any]:
        return parsers.extract_ld_json(self.soup)

    def meta_og(self, keys=defaults.OG_KEYS) -> Dict[str, str]:
        return parsers.extract_meta_og(self.soup, meta=keys)

    def article(self) -> news.ArticleData:
        ad = news.ArticleData.from_html(url=self.url.fullurl, html=self._html)
        return ad

    def keywords(self) -> Union[str, None]:
        k = None
        for m in self.soup.find_all("meta"):
            p = m.get("property")
            if p and p == "keywords":
                k = m.get("content")
        return k

    def metas(self) -> List[types.MetaTag]:
        metas = []
        for m in self.soup.find_all("meta"):
            if m.get("content") and m.get("property"):
                _mt = types.MetaTag(key=m.get("property"), value=m.get("content"))
                metas.append(_mt)
            elif m.get("content") and m.get("name"):
                _mt = types.MetaTag(key=m.get("name"), value=m.get("content"))
                metas.append(_mt)
        return metas

    def get_locale(self) -> Union[str, None]:
        locale = None
        l = self.soup.html.get("lang")
        og_l = self.meta_og(keys=["og:locale"])
        if og_l:
            locale = og_l["locale"]
        elif l:
            locale = l
        return locale

    def __repr__(self):
        return f"<WebDocument '{self.url.fullurl}'>"

    def __str__(self):
        return f"<WebDocument '{self.url.fullurl}'>"


def download(
    url: str,
    *,
    crawler: CrawlerSpec,
    is_root=True,
    raise_when_not_200=True,
) -> WebDocument:
    """
    It crawls the url passed.

    :param url: url to crawl
    :type url: str
    :param crawler: A class:`CrawlerSpec` implementation.
    :type crawler: CrawlerSpec
    :param is_root: if it's a root site or not.
    :type is_root: bool
    :return: A web object.
    :rtype: WebDocument
    """
    rsp = crawler.get(url)
    if raise_when_not_200 and rsp.status_code != 200:
        raise errors.CrawlingError(url=url, status=rsp.status_code)

    w = WebDocument(url=url, html_txt=rsp.text, is_root=is_root)
    return w


def build_sitemap(
    url: str, *, crawler: CrawlerSpec, filter_dt: int = 1
) -> List[sitemap.SitemapLink]:
    """
    It try to get the sitemap of the site based on the robots.txt protocol.
    After finding sitemaps links, it starts crawling each link.

    :param url: Base url of the site
    :type url: str
    :param crawler: A crawler based on the :class:`CrawlerSpec`
    :type crawler: CrawlerSpec
    :param filter_dt: some sites could have a lot of sitemaps and links,
        like media site, `filter_dt` helps to filter old content.

    :return: A list of links extracted from the sitemaps.
    :rtype: List[sitemap.SitemapLink]
    """
    rsp_txt = crawler.get(f"{url.strip('/')}/robots.txt")
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
                        if _w.soup:
                            _urls = _w.soup.findAll("url")
                            sites = sitemap.parse_sitemap_links(_urls)
                            total_sites.extend(sites)
                except AttributeError:
                    pass
    return total_sites


def find_rss_links(
    url: str, *, crawler: CrawlerSpec, web: WebDocument = None
) -> List[rss.RSSLink]:
    """
    It will scrap the url, looking for links related to rss feeds.
    If it found rss links, then it will try to get the feed from those urls.

    :param url: base url to crawl, it should be the root url.
    :type url: str
    :param crawler: class:`CrawlerSpec` implementation to be used
    :type crawler: CrawlerSpec
    :param web: Optional, if a class:`WebDocument`  object is passed, then it wouldn't
        crawl the site.
    :return: A list of RSS link already parsed.
    :rtype: List[rss.RSSLink]
    """
    _rss: List[rss.RSSLink] = []
    _urls = set()
    _parsed = set()

    w = web or download(url=url, crawler=crawler)

    rss_links = rss.find_rss_realated_links(w.links())
    for x in rss_links:
        if x not in _parsed:
            try:
                possible = crawler.get(x)
                _parsed.add(x)

                if possible.is_xml:
                    if x not in _urls:
                        _urls.add(x)
                        _rss.append(rss.RSSLink(url=x, xmlcontent=possible.text))
                else:
                    w2 = WebDocument(x, html_txt=possible.text)
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
