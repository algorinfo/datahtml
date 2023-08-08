from typing import Optional

from attrs import define

from datahtml.parsers import extract_json
from datahtml.web import WebDocument


@define
class Instagram:
    url: str
    title: str
    # html: str
    web: WebDocument
    description: Optional[str] = None
    body: Optional[str] = None
    profile_url: Optional[str] = None
    name: Optional[str] = None
    alternate_name: Optional[str] = None

    @classmethod
    def from_webdoc(cls, w: WebDocument) -> "Instagram":
        metas = w.meta_og()
        text = w.soup.title.text
        desc = metas.get("description")

        name = None
        an = None
        body = None
        profile = None
        try:
            jd = extract_json(w.soup)[1][0]
            body = jd.get("articleBody")
            author = jd.get("author")
            if author:
                name = author.get("name")
                an = author.get("alternateName")
                profile = author.get("url")
        except:
            pass

        return cls(
            url=w.url.fullurl,
            title=text,
            web=w,
            description=desc,
            body=body,
            profile_url=profile,
            name=name,
            alternate_name=an,
        )


def download_ig(url, crawler) -> Instagram:
    r = crawler.get(url)
    w = WebDocument(url=url, html_txt=r.json()["content"], is_root=False)
    ig = Instagram.from_webdoc(w)
    return ig
