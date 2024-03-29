import os
import urllib.parse
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from datahtml import errors, types
from datahtml.base import CrawlerSpec, CrawlResponse

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
_DEFAULT_URL = "http://localhost:3000"

from datahtml.errors import URLParsingError
from datahtml.parsers import parse_url, text2soup
from datahtml.types import URL


@dataclass
class DuckLink:
    link: URL
    text: str
    from_search: str


def process_duckduck(content, from_search) -> List[DuckLink]:
    """
    from the response of duckduck, it needs the raw response from the :class:`CrawlResponse` object.
    This is as a workaround because chrome_crawler is not working well.
    """

    soup = text2soup(content)
    autos = []
    for art in soup.find_all("article"):
        links = art.find_all(href=True)
        for l in links:
            _url = l["href"]
            try:
                parsed = parse_url(_url)
                if parsed.netloc and parsed.netloc != "duckduckgo.com":
                    _auto = DuckLink(
                        link=parsed, text=art.text, from_search=from_search
                    )
                    autos.append(_auto)
                    break
            except URLParsingError:
                pass

    return autos


@dataclass
class Proxy:
    server: str
    username: Optional[str] = None
    password: Optional[str] = None
    # protocol: Optional[str] = None


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
class Browser:
    emulation: Optional[Emulation] = field(default_factory=Emulation)
    proxy: Optional[Proxy] = None


@dataclass
class ChromeConfig:
    """
    Chromiun general runtime configuration.
    In this case to respect :class:`datahtml.CrawlerSpec`,
    the configuration which is sent to the endpoints is generalizated here.

    :param ts: timeout in seconds between
    the Chrome Service and the url to crawl
    :param waitElement: Wait for a specific element in the rendered DOM.
    :param screenshot: If it would take a screenshot of the crawled page.
    :param useCookies: It will store and load cookies in every request.
    :param cookieId: cookie id used.
    :param headers: Not used
    :param browser: Runtime configuration as :class:`datahtml.contrib.chrome.BrowserConf`
    """

    ts: int = 120
    waitElement: Optional[str] = None
    screenshot: bool = False
    useCookies: bool = False
    cleanCookies: bool = False
    cookieId: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    browser: Optional[Browser] = field(default_factory=Browser)


@dataclass
class SearchGoogle:
    text: str
    ts: int = 120
    region: str = "Argentina"
    moreResults = 1
    timeFilter: Optional[str] = None
    screenshot: bool = False
    useCookies: bool = True
    cookieId: Optional[str] = "default"
    browser: Optional[Browser] = None


@dataclass
class SearchDuck:
    text: str
    ts: int = 120
    region: str = "ar-es"
    moreResults = 1
    timeFilter: Optional[str] = None
    screenshot: bool = False
    useCookies: bool = True
    cookieId: Optional[str] = "default"
    browser: Optional[Browser] = None


@dataclass
class ImageResponse:
    fullurl: str
    headers: Dict[str, Any]
    status: int
    image: Optional[str] = None
    error: Optional[str] = None


def default_headers() -> Dict[str, Any]:
    return {"User-Agent": UA}


@dataclass
class _AxiosRequest:
    url: str
    ts: int = 60
    headers: Dict[str, Any] = field(default_factory=default_headers)
    # proxy: Optional[Proxy] = None


def prepare_google_req(text: str) -> SearchGoogle:
    return SearchGoogle(text=text)


def prepare_duck_req(text: str) -> SearchDuck:
    return SearchDuck(text=text)


@dataclass
class ChromeResponse:
    fullurl: str
    content: str
    headers: Dict[str, Any]
    status: int
    fullLoaded: bool
    screenshot: Optional[str] = None
    error: Optional[str] = None
    cookieId: Optional[str] = None


class SearchLink:
    href: str
    text: Optional[str] = None


@dataclass
class SearchResponse:
    query: str
    fullurl: str
    content: str
    links: List[SearchLink]
    headers: Dict[str, Any]
    status: int
    fullLoaded: bool
    screenshot: Optional[str] = None
    error: Optional[str] = None
    cookieId: Optional[str] = None


class ChromeV6(CrawlerSpec):
    version = "v6"

    def __init__(
        self,
        token,
        url=_DEFAULT_URL,
        config: Optional[ChromeConfig] = None,
        service_ts_secs=60,
        proxy: Optional[types.ProxyConf] = None,
    ):
        """
        Chrome Crawler is a wrapper around chrome_crawler project
        https://github.com/algorinfo/chrome_crawler

        :param config: Chrome configuration
        :param url: base url of the service. Ex:
            https://chrome.algorinfo.com
        :param token: token to be used for the crawler
        :param service_ts_secs: timeout for httpx doing requests
            to the Chrome Service
        :param proxy: Proxy to be used.
        """
        self._url = url
        self._token = token
        self._headers = {"Authorization": f"Bearer {self._token}"}
        self._conf = config or ChromeConfig()
        self._service_ts = service_ts_secs

        self.proxy = proxy

    @classmethod
    def from_env(cls) -> "ChromeV6":
        tkn = os.getenv("CHROME_TOKEN")
        srv = os.getenv("CHROME_SERVICE")
        cf = ChromeConfig()
        c = cls(config=cf, url=srv, token=tkn)
        return c

    def __str__(self) -> str:
        return f"<Chrome {self.version}: {self._url}>"

    def get_raw(
        self, url, headers: Optional[Dict[str, Any]] = None, timeout_secs: int = 60
    ) -> CrawlResponse:
        """
        Get a raw response, it parse as if the response from the service.
        It will be a json.
        """
        client = httpx.Client(headers=self._headers, timeout=timeout_secs + 10)
        payload = asdict(self._conf)
        payload["url"] = url
        if self.proxy:
            payload["proxy"] = self.proxy.dict()
        try:
            r = client.post(f"{self._url}/{self.version}/chrome", json=payload)
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

    def get_chrome(
        self, url, headers: Optional[Dict[str, Any]] = None, timeout_secs: int = 60
    ) -> ChromeResponse:
        """Get a Chrome formatted response"""
        rsp = self.get_raw(url, headers, timeout_secs)
        chrome = self.as_chrome(rsp)
        return chrome

    def get(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:
        """Get complies with :class:`CrawlerSpec`, as content it returns
        the html content of the Chrome service, but some information is
        loss like if the content was fullLoaded, or if a screenshot was taken.

        To get the full response from Chrome use :method:`ChromeV6.get_chrome`
        """
        rsp = self.get_raw(url, headers, timeout_secs)
        jdata = rsp.json()
        return CrawlResponse(
            url=rsp.url,
            headers=rsp.headers,
            status_code=rsp.status_code,
            content=jdata["content"],
        )

    @staticmethod
    def as_chrome(rsp: CrawlResponse) -> ChromeResponse:
        if rsp.status_code == 200:
            data = rsp.json()
            _rsp = ChromeResponse(**data)
        else:
            data = rsp.json()
            _rsp = ChromeResponse(
                fullurl=rsp.url,
                content=rsp.content.decode("utf-8"),
                headers=rsp.headers,
                status=rsp.status_code,
                fullLoaded=False,
                error=data.get("error", "error"),
            )
        return _rsp

    async def aget(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:
        client = httpx.AsyncClient(
            headers=self._headers, timeout=self._service_ts, follow_redirects=True
        )
        payload = asdict(self._conf)
        payload["url"] = url
        if self.proxy:
            payload["proxy"] = self.proxy.dict()
        try:
            r = await client.post(f"{self._url}/{self.version}/chrome", json=payload)
            jdata = r.json()
            rsp = CrawlResponse(
                url=url,
                headers=dict(r.headers),
                status_code=r.status_code,
                content=jdata["content"],
            )

            return rsp
        except httpx.HTTPError as e:
            # err = traceback.format_exc()
            raise errors.CrawlHTTPError(str(e))
        finally:
            await client.aclose()

    def google_search(self, req: SearchGoogle) -> CrawlResponse:
        client = httpx.Client(headers=self._headers, timeout=self._service_ts)
        payload = asdict(req)
        try:
            r = client.post(f"{self._url}/{self.version}/google", json=payload)
            rsp = CrawlResponse(
                url=f"{self._url}/{self.version}/google",
                headers=dict(r.headers),
                status_code=r.status_code,
                content=r.content,
            )
            return rsp
        except httpx.HTTPError as e:
            # err = traceback.format_exc()
            raise errors.CrawlHTTPError(str(e))

    def duckduckgo_search(self, req: SearchDuck) -> CrawlResponse:
        client = httpx.Client(headers=self._headers, timeout=self._service_ts)

        payload = asdict(req)
        try:
            r = client.post(f"{self._url}/{self.version}/duckduckgo", json=payload)
            rsp = CrawlResponse(
                url=f"{self._url}/{self.version}/duckduckgo",
                headers=dict(r.headers),
                status_code=r.status_code,
                content=r.content,
            )
            return rsp
        except httpx.HTTPError as e:
            # err = traceback.format_exc()
            raise errors.CrawlHTTPError(str(e))

    def probe(self) -> bool:
        rsp = httpx.get(self._url, timeout=self._service_ts)
        if rsp.status_code == 200:
            return True
        return False

    async def aprobe(self) -> bool:

        async with httpx.AsyncClient(timeout=self._service_ts) as client:
            rsp = await client.get(self._url)

        if rsp.status_code == 200:
            return True
        return False


class AxiosV6(CrawlerSpec):
    version = "v6"

    def __init__(
        self,
        token,
        url=_DEFAULT_URL,
        service_ts_secs=60,
        proxy: Optional[types.ProxyConf] = None,
    ):
        """
        Axios Crawler is a wrapper around chrome_crawler project

        :param url: fullurl of the crawler i.e:
        https://chrome.algorinfo.com/v4/axios
        :param token: token to be used for the crawler
        """
        self._url = url
        self._token = token
        self._headers = {"Authorization": f"Bearer {self._token}"}
        self._service_ts = service_ts_secs

        self.proxy = proxy

    @classmethod
    def from_env(cls) -> "AxiosV6":
        tkn = os.getenv("CHROME_TOKEN")
        srv = os.getenv("CHROME_SERVICE")
        c = cls(token=tkn, url=srv)
        return c

    def __str__(self) -> str:
        return f"<Axios {self.version} {self._url}>"

    def __repr__(self) -> str:
        return f"<Axios {self.version} {self._url}>"

    def get(
        self,
        url,
        headers: Optional[Dict[str, Any]] = None,
        timeout_secs: int = 60,
    ) -> CrawlResponse:
        req = _AxiosRequest(url=url, ts=timeout_secs)
        if headers:
            req.headers = headers
        req.ts = timeout_secs

        try:
            r = httpx.post(
                f"{self._url}/{self.version}/axios",
                json=asdict(req),
                headers=self._headers,
                timeout=self._service_ts,
            )
            data = r.json()
            rsp = CrawlResponse(
                url=url,
                headers=data.get("headers", {}),
                status_code=r.status_code,
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
        client = httpx.AsyncClient(
            headers=self._headers, timeout=self._service_ts, follow_redirects=True
        )

        req = _AxiosRequest(url=url, ts=timeout_secs)
        if headers:
            req.headers = headers
        req.ts = timeout_secs

        try:
            r = await client.post(
                f"{self._url}/{self.version}/axios",
                json=asdict(req),
                headers=self._headers,
                timeout=self._service_ts,
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

    def image(self, url: str) -> ImageResponse:
        params = urllib.parse.urlencode({"url": url})

        try:
            r = httpx.get(
                f"{self._url}/{self.version}/image?{params}",
                headers=self._headers,
                timeout=self._service_ts,
            )
            data = r.json()
            rsp = ImageResponse(
                fullurl=url,
                headers=data.get("headers", {}),
                status=data.get("status"),
                image=data.get("image"),
                error=data.get("error"),
            )
            return rsp
        except httpx.HTTPError as e:
            # err = traceback.format_exc()
            raise errors.CrawlHTTPError(str(e))

    def probe(self) -> bool:
        rsp = httpx.get(self._url, timeout=self._service_ts)
        if rsp.status_code == 200:
            return True
        return False

    async def aprobe(self) -> bool:

        async with httpx.AsyncClient(timeout=self._service_ts) as client:
            rsp = await client.get(self._url)

        if rsp.status_code == 200:
            return True
        return False


def default_chrome_v6(*, token, service) -> ChromeV6:
    cf = ChromeConfig()
    c = ChromeV6(config=cf, url=service, token=token)
    return c


def default_axios_v6(*, token, service) -> AxiosV6:
    ac = AxiosV6(token, url=service)
    return ac
