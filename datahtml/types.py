import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from attr import asdict, define


@dataclass
class Link:
    #: text extract from the link
    title: str
    #: the real link
    href: str
    #: if is internal to site or external (another domain)
    internal: bool
    #: if is't a file
    is_file: bool

    def __hash__(self):
        return hash(self.href)


@dataclass
class URL:
    """
    Represents a url. Usually parsed using :func:`datahtml.parsers.parse_url`
    
    :param fullurl: the origina given url
    :param url_short: a normalized url. It's mantained only for compatibility.
       It will be deprecated because also keeps `www.` attribute.
    :param norm: a real normalize url, with slashes at the end,
       nor queryparams nor www, nor protocol, only domain and path.
    :param www: a boolean value indicating if the original url has www
    :param secure: If the protocol is http or https
    :param domain_base: represents the domain, nor paths nor protocol
    :param netloc: netloc value as provided by urllib's parse function.
       The difference with the norm attribute is that netloc could include port
       and www.
    :param path: path of the url, it keeps queryparams.
    :param tld: tld part of the domain. It could be deprecated
       in a future release
    :param is_social: check if the url belongs to know social network.
       It could be deprecated in future releases.


    .. code-block:: python

        url = parse_url("https://www.algorinfo.com/testing?query=params")
        print(url.norm)
        algorinfo.com/testing
    


    .. versionadded:: 0.4.0rc14
        norm attribute 
    """
    fullurl: str
    url_short: str # Mantained only for compatibility but it will be deprecated
    norm: str # Mantained only for compatibility but it will be deprecated
    www: bool
    secure: bool
    domain_base: str  # withouth www
    netloc: str  # parsed with urlparsed from python
    path: str
    tld: str
    is_social: bool = False

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
