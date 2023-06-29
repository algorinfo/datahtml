import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from attr import asdict, define


@dataclass
class Link:
    title: str
    href: str
    internal: bool
    is_file: bool

    def __hash__(self):
        return hash(self.href)


@dataclass
class URL:
    fullurl: str
    url_short: str
    www: bool
    secure: bool
    domain_base: str  # withouth www
    netloc: str  # parsed with urlparsed from python
    path: str
    is_social: bool
    tld: str

    # def text(self):
    #    return text_from_link(self.fullurl)

    def __hash__(self):
        return hash(self.fullurl)


@dataclass
class Image:
    alt: str
    src: str


@dataclass
class MetaTag:
    key: str
    value: str


@define
class ProxyConf:
    server: str
    username: Optional[str] = None
    password: Optional[str] = None

    def dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_env(cls) -> "ProxyConf":
        return cls(
            server=os.environ["PROXY_SERVER"],
            username=os.getenv("PROXY_USER", None),
            password=os.getenv("PROXY_PASS"),
        )


@define
class WKEntitySearch:
    id: str
    pageid: int
    uri: str
    label: str
    description: str

    def __str__(self):
        return f"<EntitySearch {self.id} | {self.label}>"

    def __repr__(self):
        return f"<EntitySearch {self.id} | {self.label}>"

    def dict(self) -> Dict[str, Any]:
        return asdict(self)


@define
class WKEntityV1:
    id: str
    pageid: int
    instance_of: List[str]
    label: str
    description: str
    modified: str
    raw: Dict[str, Any]
    aliases: List[str]
    image: Optional[str] = None

    def __str__(self):
        return f"<WKEntity {self.id} | {self.label}>"

    def __repr__(self):
        return f"<WKEntity {self.id} | {self.label}>"

    def dict(self) -> Dict[str, Any]:
        return asdict(self)


@define
class WKEntityExtra:
    id: str
    label: str
    sites: List[str]
    gender: Optional[str] = None
    country: Optional[str] = None
    ig: Optional[List[str]] = None
    fb: Optional[List[str]] = None
    linkedin: Optional[List[str]] = None
    twitter: Optional[List[str]] = None

    def __str__(self):
        return f"<WKEntityExtra {self.id} | {self.label}>"

    def __repr__(self):
        return f"<WKEntityExtra {self.id} | {self.label}>"

    def dict(self) -> Dict[str, Any]:
        return asdict(self)

@define
class LinkMerged:
    fullurl: str
    urlnorm: str
    source: str
    text: str
    text_path: str
    title: Optional[str] = None
    lastmod: Optional[str] = None
