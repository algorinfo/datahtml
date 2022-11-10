import json
import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup as BS


def extract_metadata(soup: BS) -> List[Dict[str, Any]]:
    """
    Get meta tags from the head part of the html document
    """
    metas = soup.findAll("meta")
    attrs = [ m.attrs for m in metas]
    return attrs


def extract_json(soup: BS) -> List[Dict[str, Any]]:
    """ Parse js script tags and try to get javascript objects 
    a.k.a json """
    data = []
    for ix, s in enumerate(soup.find_all('script')):
        # print(s.string)
        # print(type(str(s.string)))
        parsed = re.findall(r"{.+[:,].+}|\[.+[,:].+\]", str(s.string))
        try:
            if parsed:
                _d = json.loads(parsed[0])
                # print(ix, json.loads(parsed[0]))
                data.append(_d)
        except json.JSONDecodeError:
            pass
    return data
