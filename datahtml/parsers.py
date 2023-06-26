import json
import re
from typing import Any, Dict, List
from urllib.parse import urlparse

from bs4 import BeautifulSoup as BS

from datahtml import errors, types
from datahtml.defaults import EXTENSIONS_REGEX, SOCIALS_COM, URL_REGEX, WORDS_REGEX


def _proc_soup_link(s_link, url: types.URL) -> types.Link:
    text = s_link.text
    href = s_link["href"]
    internal = False

    a_file = re.findall(EXTENSIONS_REGEX, href)
    is_a_file = bool(a_file)

    parsed = urlparse(href)
    if not parsed.netloc:
        protocol = "http"
        if url.secure:
            protocol = "https"
        href = f"{protocol}://{url.netloc}{parsed.path}"
    if url.domain_base in href:
        internal = True

    return types.Link(
        title=text.strip(), href=href.strip(), internal=internal, is_file=is_a_file
    )


def is_social(base_url, socials):
    # print(_u)
    for s in socials:
        if s in base_url:
            return True
    return False


def text_from_link(link: str) -> str:
    """Gets a link a return a string from the path.
    It try to keep the last part of the url and give away any extension:
    >> text_from_link("https://www.pe.com/morales-y-bullrich-reeditaron-los-reproches-y-profundizaron-las-diferencias-sobre-el-rumbo-de-jxc.phtml")
    >> 'morales y bullrich reeditaron los reproches y profundizaron las diferencias sobre el rumbo de jxc'
    """
    u = urlparse(link)
    _path = u.path.split(".")[0]
    between_path = _path.split("/")
    last_path = between_path[-1]
    # last_path = last_path.split(".html")[0]
    words = re.findall(WORDS_REGEX, last_path)
    return " ".join(words)


def text2soup(txt: str, parser="lxml") -> BS:
    soup = BS(txt, parser)
    return soup


def extract_metadata(soup: BS) -> List[Dict[str, Any]]:
    """
    Get meta tags from the head part of the html document
    """
    metas = soup.findAll("meta")
    attrs = [m.attrs for m in metas]
    return attrs


def extract_meta_og(
    soup: BS, meta=["og:url", "og:image", "og:description", "og:type"]
) -> Dict[str, str]:
    tags = {}
    for x in meta:
        tag = soup.find("meta", property=x)
        if tag:
            key = x.split(":")[1]
            tags[key] = tag["content"]
            # tags.append({x.split(":")[1]: tag["content"]})

    return tags


def extract_json(soup: BS) -> List[Dict[str, Any]]:
    """Parse js script tags and try to get javascript objects
    a.k.a json"""
    data = []
    for ix, s in enumerate(soup.find_all("script")):
        # print(s.string)
        # print(type(str(s.string)))
        parsed = re.findall(r"{.+[:,].+}|\[.+[,:].+\]", str(s.string))
        try:
            if parsed:
                _d = json.loads(parsed[0])
                # print(ix, json.loads(parsed[0]))
                data.append(_d)
        except json.JSONDecodeError:
            pass
    return data


def url_norm(url, trailing=True):
    """
    Strip slashes.
    """
    _u = urlparse(url)
    # netloc = _u.netloc.strip("/")
    _path = _u.path.strip("/")
    fullurl = f"{_u.scheme}://{_u.netloc}/{_path}"
    url_short = f"{_u.netloc}/{_path}"
    if trailing:
        fullurl = fullurl.strip("/")
        url_short = url_short.strip("/")
    return fullurl, url_short

def get_domain_base(url: str) -> str:
    url_regex = re.findall(URL_REGEX, url)
    if not url_regex:
        raise errors.URLParsingError(url)
    domain = url_regex[0][1]
    return str(domain)

def parse_url(url: str, socials_url=SOCIALS_COM) -> types.URL:
    """Parse a url string to URL.
    URL_REGEX return a tuple with 3 values:
    (protocol, netloc, path)
    """
    url_regex = re.findall(URL_REGEX, url)

    if not url_regex:
        raise errors.URLParsingError(url)

    _u = urlparse(url)
    protocol = url_regex[0][0]
    path = url_regex[0][2]
    domain = url_regex[0][1]
    domain_base = domain
    fullurl, url_short = url_norm(url)

    netloc = _u.netloc
    www = False
    _www = domain.split("www.")
    if len(_www) > 1:
        www = True
        domain_base = _www[1]
        netloc = netloc.split("www.")[1]

    _is_social = is_social(domain_base, socials_url)
    is_secure = protocol == "https"
    tld = domain.split(".")[-1]

    return types.URL(
        fullurl=fullurl,
        url_short=url_short,
        domain_base=domain_base,
        netloc=_u.netloc,
        path=path,
        is_social=_is_social,
        secure=is_secure,
        www=www,
        tld=tld,
    )


def extract_links(soup: BS, fullurl: str) -> List[types.Link]:
    """
    Extract links from a html site
    """
    links = set()
    url = parse_url(fullurl)
    for x in soup.findAll("a"):
        try:
            link = _proc_soup_link(x, url)
            if link:
                links.add(link)
        except KeyError:
            pass
    for x in soup.findAll(href=True):
        try:
            link = _proc_soup_link(x, url)
            if link:
                links.add(link)
        except KeyError:
            pass
    return list(links)


def extract_images(soup: BS) -> List[types.Image]:
    images = [
        types.Image(alt=x.get("alt", ""), src=x.get("src", ""))
        for x in soup.findAll("img")
    ]
    return images


def extract_ld_json(soup: BS) -> Dict[str, Any]:
    j = soup.find("script", type="application/ld+json")
    if not j:
        raise errors.LDJSONNotFound()
    text = j.string
    jdata = json.loads(text)
    return jdata


def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x

def meta_keywords(soup: BS) -> str:
    data = extract_metadata(soup)
    keywords = ""
    for d in data:
        if d.get("property"):
            if d["property"] == "keywords":
                keywords = d["content"]
                break
    return keywords

def proxyconf2url(p: types.ProxyConf) -> str:
    url = p.server
    if p.username:
        parsed = urlparse(p.server)
        url = f"{parsed.scheme}://{p.username}:{p.password}@{parsed.netloc}"
    return url
    
