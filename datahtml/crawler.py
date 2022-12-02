from typing import Any, Dict, Optional

import httpx

from datahtml.base import CrawlerSpec, CrawlResponse
from datahtml import errors
# import traceback


class LocalCrawler(CrawlerSpec):
    def get(
        self, url, headers: Optional[Dict[str, Any]] = {}, timeout_secs: int = 60
    ) -> CrawlResponse:

        try:
            r = httpx.get(url, headers=headers, timeout=timeout_secs,
                          follow_redirects=True)
            rsp = CrawlResponse(url=url, headers=r.headers,
                                status_code=r.status_code, content=r.content)
            return rsp
        except httpx.HTTPError as e:
            #err = traceback.format_exc()
            raise errors.CrawlHTTPError(str(e))


