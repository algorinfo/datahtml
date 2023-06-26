import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

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
