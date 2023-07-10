import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx

from datahtml import defaults, errors, types
from datahtml.base import CrawlerSpec, CrawlResponse

# import traceback


def proxyconf2url(p: types.ProxyConf) -> str:
    url = p.server
    if p.username:
        parsed = urlparse(p.server)
        url = f"{parsed.scheme}://{p.username}:{p.password}@{parsed.netloc}"
    return url


def proxyconf_from_env() -> types.ProxyConf:
    _user = os.getenv("PROXY_USER") or os.getenv("PROXY_USERNAME")
    _pass = os.getenv("PROXY_PASS") or os.getenv("PROXY_PASSWORD")
    return types.ProxyConf(
        server=os.environ["PROXY_SERVER"], username=_user, password=_pass
    )


@dataclass
class Proxy:
    server: str
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class ViewPort:
    width: int = 1280
    height: int = 720


@dataclass
class GeoLocation:
    # longitude: float=-34.6156548
    # latitude: float = -58.5156983
    longitude: float = 40.697631
    latitude: float = -74.144485


@dataclass
class Emulation:
    # locale: str = "es-AR"
    # timezoneId: str = "America/Argentina/Buenos_Aires"
    locale: str = "en-US"
    timezoneId: str = "America/New_York"
    isMobile: bool = False
    viewport: ViewPort = field(default_factory=ViewPort)
    geoEnabled: bool = False
    geolocation: GeoLocation = GeoLocation()


@dataclass
class ChromeConfig:
    ts: int = 120
    waitElement: Optional[str] = None
    screenshot: bool = False
    headers: Dict[str, Any] = field(default_factory=dict)
    emulation: Optional[Emulation] = field(default_factory=Emulation)


class LocalCrawler(CrawlerSpec):
    def __init__(self, proxy: Optional[types.ProxyConf] = None):
        self.proxy = proxy

    def get(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:
        if not headers:
            headers = {"User-Agent": defaults.AGENT}

        client = httpx.Client(
            headers=headers, timeout=timeout_secs, follow_redirects=True
        )
        if self.proxy:
            proxy_url = proxyconf2url(self.proxy)
            client = httpx.Client(
                headers=headers,
                timeout=timeout_secs,
                follow_redirects=True,
                proxies={"all://": proxy_url},
            )

        try:
            r = client.get(
                url, headers=headers, timeout=timeout_secs, follow_redirects=True
            )
            rsp = CrawlResponse(
                url=url,
                headers=dict(r.headers),
                status_code=r.status_code,
                content=r.content,
            )
            return rsp
        except httpx.HTTPError as e:
            # err = traceback.format_exc()
            raise errors.CrawlHTTPError(str(e))
        finally:
            client.close()

    async def aget(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:

        client = httpx.AsyncClient(
            headers=headers, timeout=timeout_secs, follow_redirects=True
        )
        if not headers:
            headers = {"User-Agent": defaults.AGENT}
        if self.proxy:
            proxy_url = proxyconf2url(self.proxy)
            client = httpx.AsyncClient(
                headers=headers,
                timeout=timeout_secs,
                follow_redirects=True,
                proxies={"all://": proxy_url},
            )

        try:
            r = await client.get(
                url, headers=headers, timeout=timeout_secs, follow_redirects=True
            )
            rsp = CrawlResponse(
                url=url,
                headers=dict(r.headers),
                status_code=r.status_code,
                content=r.content,
            )
            return rsp
        except httpx.HTTPError as e:
            # err = traceback.format_exc()
            raise errors.CrawlHTTPError(str(e))
        finally:
            await client.aclose()


class AxiosCrawler(CrawlerSpec):
    def __init__(self, url=None, token=None, proxy: Optional[types.ProxyConf] = None):
        """
        Axios Crawler is a wrapper around chrome_crawler project

        :param url: fullurl of the crawler i.e:
        https://chrome.algorinfo.com/v4/axios
        :param token: token to be used for the crawler
        """
        self._url = url or os.getenv("AXIOS_URL")
        self._token = token or os.getenv("AXIOS_TOKEN")
        self._headers = {"Authorization": f"Bearer {self._token}"}

        self.proxy = proxy

    def get(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:
        # TODO: fix if something fail on the crawler service

        try:
            r = httpx.post(
                self._url,
                data={"url": url, "headers": headers},
                headers=self._headers,
                timeout=timeout_secs,
            )
            data = r.json()
            rsp = CrawlResponse(
                url=url,
                headers=data.get("headers", {}),
                status_code=data["status"],
                content=data["content"],
            )
            return rsp
        except httpx.HTTPError as e:
            # err = traceback.format_exc()
            raise errors.CrawlHTTPError(str(e))

    async def aget(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:
        raise NotImplementedError()


class ChromeV4(CrawlerSpec):
    def __init__(
        self,
        config: ChromeConfig,
        url=None,
        token=None,
        proxy: Optional[types.ProxyConf] = None,
    ):
        """
        Axios Crawler is a wrapper around chrome_crawler project

        :param url: fullurl of the crawler i.e:
        https://chrome.algorinfo.com/v4/chrome
        :param token: token to be used for the crawler
        """
        self._url = url or os.getenv("CHROME_URL")
        self._token = token or os.getenv("CHROME_TOKEN")
        self._headers = {"Authorization": f"Bearer {self._token}"}
        self._conf = config

        self.proxy = proxy
    def __str__(self) -> str:
        return f"<ChromeV4 {self._url}>"

    def get(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:

        client = httpx.Client(headers=self._headers, timeout=timeout_secs + 10)
        payload = asdict(self._conf)
        payload["url"] = url
        if self.proxy:
            payload["proxy"] = self.proxy.dict()
        r = client.post(f"{self._url}/v4/chrome", json=payload)
        rsp = CrawlResponse(
                url=url,
                headers=dict(r.headers),
                status_code=r.status_code,
                content=r.content,
        )
        return rsp

    async def aget(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:
        raise NotImplementedError()

    def google_search(
        self, text, next_page=None, google_url="https://www.google.com", timeout_secs=60
    ) -> CrawlResponse:
        client = httpx.Client(headers=self._headers, timeout=timeout_secs + 10)

        payload = asdict(self._conf)
        payload["url"] = google_url
        if self.proxy:
            payload["proxy"] = self.proxy.dict()
        payload["text"] = text
        del(payload["waitElement"])
        if next_page:
            payload["nextPage"] = next_page
        r = client.post(f"{self._url}/v4/google-search", json=payload)
        rsp = CrawlResponse(
                url=google_url,
                headers=dict(r.headers),
                status_code=r.status_code,
                content=r.content,
            )
        return rsp


def default_chrome(*, service, token) -> ChromeV4:
    cf = ChromeConfig()
    c = ChromeV4(config=cf, url=service, token=token)
    return c
