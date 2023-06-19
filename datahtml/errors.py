class URLParsingError(Exception):
    def __init__(self, url):
        msg = f"Error parsing url {url}"
        super().__init__(msg)


class LDJSONNotFound(Exception):
    def __init__(self, msg="ld+json tag not found"):
        super().__init__(msg)


class CrawlHTTPError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class SitemapEmptyLinks(Exception):
    def __init__(self):
        msg = "Any link found"
        super().__init__(msg)


class RobotsTxtNotFound(Exception):
    def __init__(self, url):
        msg = f"robots.txt file not found for {url}"
        super().__init__(msg)


class CrawlingError(Exception):
    def __init__(self, url, status):
        msg = f"Error crawling url {url} with status {status}"
        super().__init__(msg)


