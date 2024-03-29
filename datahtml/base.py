import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from datahtml.types import ProxyConf


class CrawlResponse:
    def __init__(
        self, content: bytes, url: str, headers: Dict[str, str], status_code: int
    ):
        self.url = url
        self.content = content
        self.headers = headers
        self.status_code = status_code

    @property
    def text(self):
        try:
            return self.content.decode("utf-8")
        except UnicodeDecodeError:
            return self.content.decode("latin-1")
        except AttributeError:
            return self.content

    def json(self):
        return json.loads(self.text)

    @property
    def is_json(self):
        if "application/json" in self.headers["content-type"]:
            return True
        return False

    @property
    def is_xml(self):
        if "xml" in self.headers["content-type"]:
            return True
        return False

    @property
    def is_txt(self):
        if "text/plain" in self.headers["content-type"]:
            return True
        return False

    def __str__(self):
        return f"<CrawlResponse {self.url} {self.status_code}>"

    def __repr__(self):
        return f"<CrawlResponse {self.url} {self.status_code}>"


class CrawlerSpec(ABC):
    proxy: Optional[ProxyConf]

    @abstractmethod
    def get(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:
        pass

    @abstractmethod
    async def aget(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:
        pass
