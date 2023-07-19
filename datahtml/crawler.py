import os
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


