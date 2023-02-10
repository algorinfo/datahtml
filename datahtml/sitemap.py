from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup as BS

from datahtml._utils import difference_from_now


@dataclass
class SitemapLink:
    fullurl: str
    lastmod: str


def parse_sitemap_links(urls) -> List[SitemapLink]:
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
    sites = parse_sitemap_links(urls)
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
                diff = difference_from_now(s.lastmod.text)
                if diff.days <= filter_dt:
                    sites.append(s.loc.text)
            except AttributeError:
                pass
        else:
            sites.append(s.loc.text)
    return sites


def get_sitemaps_from_robots(robots_txt: str) -> List[str]:
    """ it's parse links to sitemap files from the
    robots.txt protocol file
    """
    sitemaps = []
    for line in robots_txt.splitlines():
        if "Sitemap:" in line:
            sitemaps.append(line.split()[1])
    return sitemaps
