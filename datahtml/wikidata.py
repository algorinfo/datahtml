from typing import List, Union, Any, Dict
from urllib.parse import urlencode

from datahtml import types
from datahtml.base import CrawlerSpec
from datahtml.defaults import WIKI_API

# based on
# https://www.jcchouinard.com/wikidata-api-python/
# wiki pages
# https://www.wikidata.org/wiki/Q9684

ENTS = {
    "Q5": "Person",
    "Q4830453": "Bussiness",
    "Q18388277": "Technology Company",
    "Q891723": "Public Company",
    "Q30748112": "Big Tech (web)",
    "Q1110794": "Daily newspaper",
    "Q1153191": "Online newspaper",
    "Q1331793": "Media company",
    "Q19967801": "Online service",
    "Q1197685": "Public Holyday",
    "Q7278": "Political Party",
    "Q6138528": "Political Coalition",
    "Q3624078": "Sovereign state",
    "Q6256": "Country",
    "Q6266": "Nation",
}

GENDERS = {
    "Q6581097": "male",
    "Q6581072": "female",
    "Q1097630": "intersexual",
    "Q1052281": "transgender female",
    "Q2449503": "transgender male",
    "Q48270": "non-binary",
}

PROPS = {
    "instance_of": "P31",
    "image": "P18",
    "logo": "P154",
    "gender": "P21",
    "country_cityzen": "P27",  # for persons
    "country": "P17",  # for orgs
    "twitter": "P2002",
    "facebook": "P2013",
    "linkedin": "P4264",
    "youtube": "P2397",
    "ig": "P2003",
    "reddit": "P3984",
    "spotify": "P11625",
    "github": "P2037",
    "rss": "P1019",
    "websites": "P856",
    "native_lang": "P103",
    "birth": "P569",
    "ideology": "P1142",
    "political_party": "P102",
    "subclass": "P279",
    "industry": "P452",
}


def search_entities(
        search_query, *, crawler: CrawlerSpec, lang="en"
) -> List[types.WKEntitySearch]:
    params = urlencode(
        {
            "action": "wbsearchentities",
            "format": "json",
            "search": search_query,
            "language": lang,
        }
    )
    rsp = crawler.get(f"{WIKI_API}?{params}")
    data = rsp.json()
    results = []
    for d in data["search"]:
        e = types.WKEntitySearch(
            id=d["id"],
            pageid=d["pageid"],
            uri=d["concepturi"],
            label=d["label"],
            description=d["description"],
        )
        results.append(e)
    return results


def _get_claim_data(e, prop):
    values = []
    try:
        for val in e["claims"][prop]:
            _data = val["mainsnak"].get("datavalue")
            if _data:
                values.append(_data["value"])
    except KeyError:
        pass
    return values


def _get_gender(e) -> Union[str, None]:
    values = _get_claim_data(e, "P21")
    g = None
    if values:
        g = GENDERS.get(values[0]["id"])
    return g


def _get_country(e) -> Union[str, None]:
    cid = None
    values = _get_claim_data(e, PROPS["country_cityzen"])
    if values:
        cid = values[0]["id"]
    else:
        tmp = _get_claim_data(e, PROPS["country"])
        if tmp:
            cid = tmp[0]["id"]

    return cid


def get_entity(entityid, *, crawler: CrawlerSpec, lang="en") -> types.WKEntityV1:
    params = urlencode(
        {
            "action": "wbgetentities",
            "format": "json",
            "ids": entityid,
            "language": lang,
        }
    )
    rsp = crawler.get(f"{WIKI_API}?{params}")
    data = rsp.json()
    e = data["entities"][entityid]

    label = e["labels"]["en"]["value"]
    desc = e["descriptions"]["en"]["value"]
    pid = e["pageid"]
    aliases = [al.get("value") for al in e["aliases"]["en"]]

    instances_of = _get_claim_data(e, PROPS["instance_of"])
    types_id = [v.get("id") for v in instances_of]

    try:
        image = _get_claim_data(e, PROPS["image"])[0]
    except AttributeError:
        image = None
    return types.WKEntityV1(
        id=entityid,
        pageid=pid,
        instance_of=types_id,
        label=label,
        description=desc,
        modified=e["modified"],
        aliases=aliases,
        image=image,
        raw=e,

    )


def extract_extra(e: Dict[str, Any]) -> types.WKEntityExtra:
    id_ = e["id"]
    label = e["labels"]["en"]["value"]
    sites = _get_claim_data(e, PROPS["websites"])
    gender = _get_gender(e)
    country = _get_country(e)
    ig = _get_claim_data(e, PROPS["ig"])
    twitter = _get_claim_data(e, PROPS["twitter"])
    lk = _get_claim_data(e, PROPS["linkedin"])
    fb = _get_claim_data(e, PROPS["facebook"])

    return types.WKEntityExtra(
        id=id_,
        label=label,
        sites=sites,
        gender=gender,
        country=country,
        ig=ig,
        fb=fb,
        linkedin=lk,
        twitter=twitter,
    )


# def _get_claims(e: Dict[str, Any], prop: str):
#     for values in e["claims"][prop]:
