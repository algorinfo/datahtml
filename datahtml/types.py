from dataclasses import dataclass


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
    
