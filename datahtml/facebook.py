from typing import Optional
from urllib.parse import parse_qs, urlparse

from attrs import define

from datahtml.types import URL
from datahtml.web import WebDocument
from datahtml.base import CrawlerSpec


@define
class FBLink:
    url: str
    is_profile: bool
    is_photo: bool = False
    id: Optional[str] = None
    alias: Optional[str] = None

    @classmethod
    def from_url(cls, url: str) -> "FBLink":
        u_parsed = urlparse(url)
        first = u_parsed.path.split("/")[1]
        path_len = len(u_parsed.path.split("/"))

        is_photo = False
        id = None
        alias = None
        is_profile = False
        if "people" in u_parsed.path:
            alias = u_parsed.path.split("/")[2]
            id = u_parsed.path.split("/")[3]
            is_profile = True
        elif "story.php" in u_parsed.path:
            id = parse_qs(u_parsed.query).get("id")[0]
        elif "photo" in u_parsed.path:
            id = None
            is_photo = True
        elif ("posts" in u_parsed.path) or ("videos" in u_parsed.path):
            id = u_parsed.path.strip("/")[-1]
            alias = first
        elif "profile.php" in u_parsed.path:
            id = parse_qs(u_parsed.query).get("id")[0]
            is_profile = True
        elif path_len == 2:
            alias = first
            is_profile = True
        return cls(url=url, is_profile=is_profile, is_photo=is_photo, id=id, alias=alias)

@define
class Facebook:
    url: str
    title: str
    web: WebDocument
    link: FBLink
    description: Optional[str] = None


def normalize_fb_url(url: URL):
    # if url.domain_base != "facebook.com":
    # _url = deepcopy(url)
    u = f"https://www.facebook.com{url.path}"
    # else:
    #    u = f"https://www.faceboook.com{u.path}"
    return u


def download_fb(url: URL, crawler: CrawlerSpec) -> Facebook:
    norm = normalize_fb_url(url)
    link = FBLink.from_url(norm)
    r = crawler.get(norm)
    w = WebDocument(url=norm, html_txt=r.json()["content"], is_root=False)
    title = w.soup.title.text
    _m = w.meta_og()
    desc = _m.get("description")

    fb = Facebook(url=norm, web=w, title=title, link=link, description=desc)
    return fb
