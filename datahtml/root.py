from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup as BS
from dateutil.parser import parse as dtparser

from datahtml import errors
from datahtml.base import CrawlerSpec
from datahtml.web import Web


@dataclass
class SitemapLink:
    fullurl: str
    lastmod: str


def _difference_from_now(dt: str):
    now = datetime.utcnow()
    _dt = dtparser(dt, ignoretz=True)
    diff = now - _dt
    return diff


def _parse_xml(urls) -> List[SitemapLink]:
    final = []
    for u in urls:
        lastmod = u.find("lastmod")
        lastmod_txt = ""
        if lastmod:
            lastmod_txt = lastmod.text

        data = SitemapLink(fullurl=u.find("loc").text, lastmod=lastmod_txt)
        final.append(data)

    return final


def sitemap_urls(soup: BS) -> List[SitemapLink]:
    """get urls from a sitemap parsed object"""
    urls = soup.findAll("url")
    if not urls:
        # raise errors.SitemapEmptyLinks()
        return []
    sites = _parse_xml(urls)
    return sites


def sitemap_sitemaps(soup: BS, filter_dt=1):
    """
    get links to other sitemaps from the main sitemap
    :param filter_dt: filter sitemaps below 1 day
    """
    xmlsites = soup.findAll("sitemap")
    sites = []
    for s in xmlsites:
        if filter_dt:
            try:
                diff = _difference_from_now(s.lastmod.text)
                if diff.days <= filter_dt:
                    sites.append(s.loc.text)
            except AttributeError:
                pass
        else:
            sites.append(s.loc.text)
    return sites


def get_sitemaps_from_robots(robots_txt: str) -> List[str]:
    sitemaps = []
    for line in robots_txt.splitlines():
        if "Sitemap:" in line:
            sitemaps.append(line.split()[1])
    return sitemaps


def build_sitemap(url, *, crawler: CrawlerSpec, filter_dt=1) -> List[SitemapLink]:
    rsp_txt = crawler.get(f"{url.strip()}/robots.txt")
    sitesmaps = get_sitemaps_from_robots(rsp_txt.text)

    total_sites = []
    for site in sitesmaps:
        w = Web.parse(site, crawler=crawler)
        urls = w.soup.findAll("url")
        if urls:
            sites = _parse_xml(urls)
            total_sites.extend(sites)
        else:
            # breakpoint()
            # locs = s.findAll("loc")
            # for l in locs:
            xmlsites = w.soup.findAll("sitemap")
            for site2 in xmlsites:
                try:
                    diff = _difference_from_now(site2.lastmod.text)
                    if diff.days <= filter_dt:
                        _w = Web.parse(site2.loc.text, crawler=crawler)
                        if _w.soup:
                            _urls = _w.soup.findAll("url")
                            sites = _parse_xml(_urls)
                            total_sites.extend(sites)
                except AttributeError:
                    pass
    return total_sites
