import os
from typing import Any, Dict, Optional

import httpx

from datahtml import errors, types, defaults
from datahtml.base import CrawlerSpec, CrawlResponse
from datahtml.parsers import proxyconf2url

# import traceback


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
            headers={"User-Agent": defaults.AGENT}

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
            headers={"User-Agent": defaults.AGENT}
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
