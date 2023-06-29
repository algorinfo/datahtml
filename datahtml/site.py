from typing import Dict, List, Optional, Any

from datahtml import rss, web
from datahtml.base import CrawlerSpec
from datahtml.errors import URLParsingError, XMLContentNotFound
from datahtml.parsers import parse_url, text_from_link
from datahtml.sitemap import SitemapLink
from datahtml.types import Link
from datahtml.web import WebDocument

from datahtml.types import LinkMerged


def _map_rss_links(links: Dict[str, LinkMerged], rss_links: List[rss.Entry]):
    for l in rss_links:
        try:
            u = parse_url(l.href)
        except URLParsingError:
            break
        _link2crawl = links.get(u.url_short)
        if not _link2crawl:
            text = text_from_link(u.fullurl)
            title = l.title if l.title else None
            text2use = title if title else text
            links[u.url_short] = LinkMerged(
                fullurl=u.fullurl,
                urlnorm=u.url_short,
                source="rss",
                title=title,
                text=text2use,
                text_path=text,
                lastmod=l.published,
            )


def _map_html_links(links: Dict[str, LinkMerged], html_links: List[Link]):
    for l in html_links:
        if l.internal and not l.is_file:
            try:
                u = parse_url(l.href)
            except URLParsingError:
                u = None
            if u and (u.path != "/" or not u.path):
                _link2crawl = links.get(u.url_short)
                if not _link2crawl:
                    text = text_from_link(u.fullurl)
                    title = l.title if l.title else None
                    text2use = title if title else text

                    links[u.url_short] = LinkMerged(
                        fullurl=u.fullurl,
                        urlnorm=u.url_short,
                        source="html",
                        title=title,
                        text=text2use,
                        text_path=text,
                    )


def _map_sitemap_links(links: Dict[str, LinkMerged], map_links: List[SitemapLink]):
    for l in map_links:
        u = parse_url(l.fullurl)
        _link2crawl = links.get(u.url_short)
        if not _link2crawl:
            text = text_from_link(u.fullurl)
            title = None
            links[u.url_short] = LinkMerged(
                fullurl=u.fullurl,
                urlnorm=u.url_short,
                source="sitemap",
                title=title,
                text=text,
                text_path=text,
                lastmod=l.lastmod,
            )
        else:
            links[u.url_short].lastmod = l.lastmod


def links_mapping(
    sitemap: List[SitemapLink],
    w: Optional[WebDocument] = None,
    rss_data: Optional[List[rss.Entry]] = None,
) -> List[LinkMerged]:
    links: Dict[str, LinkMerged] = {}
    if w:
        _map_html_links(links, w.links())
    if sitemap:
        _map_sitemap_links(links, sitemap)
    if rss_data:
        _map_rss_links(links, rss_data)
    return list(links.values())


def extract_links(
    fullurl: str,
    crawler: CrawlerSpec,
    from_html=True,
    from_rss=None,
    from_sitemap=False,
) -> List[LinkMerged]:
    """
    Extract links from different sources.

    :param fullurl: usually the root url where we want to get links
    :param crawler: instance of CrawlerSpec
    :param from_html: True if you want to include links from the html source
    :param from_rss: The url of a feed rss to download
    :param from_sitemap: True if you want also get links from the sitemap
    """
    w = None
    if from_html:
        w = web.download(fullurl, crawler=crawler)

    smap = []
    if from_sitemap:
        smap = web.build_sitemap(fullurl, crawler=crawler)
    rss_data = None
    if from_rss:
        try:
            rss_data = rss.download(from_rss, crawler=crawler)
        except XMLContentNotFound:
            pass
    links = links_mapping(smap, w, rss_data)
    return links
