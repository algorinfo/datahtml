from dataclasses import dataclass, field
from datetime import datetime
from datahtml.parsers import extract_json,extract_metadata, findkeys
from typing import List, Optional, Union
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup as BS

@dataclass
class ChannelVideo:
    id: str
    thumbnail_url: str
    title: str
    published_text: str
    viewcount_text: str
    crawled_at: datetime

@dataclass
class ChannelPlaylist:
    title: str
    url: str
    videos: List[ChannelVideo]
    crawled_at: datetime
    
@dataclass
class ChannelMeta:
    id: str
    name: str
    description: str
    thumbnail_url: str 
    tags: List[str] 
    subscribers: str
    family_safe: bool
    crawled_at: datetime
    available_countries: List[str] = field(default_factory=list)
    # playlists: Optional[List[ChannelPlaylist]] = None
    # main_video: Optional[str] = None
    view_count: Optional[str] = None
    joined: Optional[str] = None
    location: Optional[str] = None
    social_links: List[str] = []

    
def _get_location(data) -> Union[str, None]:
    keys = list(findkeys(data, "country"))
    if keys:
        return keys[0].get("simpleText")
    return None

def _get_view_counts(data):
    keys = list(findkeys(data, "viewCountText"))
    if keys:
        return keys[0].get("simpleText")
    return None


def _parse_social_link(link):
    url = link["navigationEndpoint"]["urlEndpoint"]["url"]
    parsed = urlparse(url)
    q = parse_qs(parsed.query)
    social = q.get("q")[0]
    return social

def _get_primary_links(data):
    keys = list(findkeys(data, "primaryLinks"))
    final = []
    if keys:
        links = keys[0]
        for link in links:
                try:
                    l = _parse_social_link(link)
                    final.append(l)
                except (KeyError, IndexError):
                    pass
    return final 
     

def _get_date_creation(data):
    keys = list(findkeys(data, "joinedDateText"))
    if keys:
        try:
            return keys[0].get("runs")[1]["text"]
        except (KeyError, IndexError):
            pass
    return None
    

def _get_tags(data):
    return data[1]["microformat"]['microformatDataRenderer']["tags"]

def _countries(data):
    return  data[1]["microformat"]['microformatDataRenderer']["availableCountries"]

def _is_family_safe(data):
    return data[1]["microformat"]['microformatDataRenderer']["familySafe"]

def _get_subscribers(data):
    s = data[1]["header"]['c4TabbedHeaderRenderer']["subscriberCountText"]["simpleText"]
    return s.replace("\xa0", " ")

def _get_channel_video(vid):
    v = ChannelVideo(
        id=vid["videoId"],
        title=vid["title"]["simpleText"],
        thumbnail_url=vid["thumbnail"]["thumbnails"][0]["url"],
        published_text=vid["publishedTimeText"]["simpleText"],
        viewcount_text=vid["viewCountText"]["simpleText"] ,
        crawled_at=datetime.utcnow()
    )
    return v

    

def _get_playlists(data):
    page = data[1]["contents"]["twoColumnBrowseResultsRenderer"]['tabs'][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
    playlists_obj = []
    for pg in page:
        playlist = pg["itemSectionRenderer"]["contents"][0].get("shelfRenderer")
        if playlist:
            videos = playlist["content"]["horizontalListRenderer"]["items"]
            videos_obj = []
            for vid in videos:
                if vid.get("gridVideoRenderer"):
                    _vid = _get_channel_video(vid.get("gridVideoRenderer"))
                    videos_obj.append(_vid)
            playlist_obj = ChannelPlaylist(
                title=playlist["title"]["runs"][0]["text"],
                url=playlist["title"]["runs"][0]["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"],
                videos=videos_obj,
                crawled_at=datetime.utcnow()

            )
            playlists_obj.append(playlist_obj)
    return playlists_obj

def _get_main_video(data):
    page = data[1]["contents"]["twoColumnBrowseResultsRenderer"]['tabs'][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
    renderer = page[0]['itemSectionRenderer']["contents"][0]['channelVideoPlayerRenderer']
    return renderer["videoId"]
            
def _get_attr(attrs, key):
    for attr in attrs:
        if attr.get("itemprop"):
            if attr["itemprop"] == key:
                return attr["content"]
        elif attr.get("name"):
            if attr["name"] == key:
                return attr["content"]
        elif attr.get("property"):
            if attr["property"] == key:
                return attr["content"]
        

def transform_channel(html):
    soup = BS(html)
    attrs = extract_metadata(soup)
    jdata = extract_json(soup)

    country = _get_location(jdata)
    view_count = _get_view_counts(jdata)
    joined = _get_date_creation(jdata)

    tags = _get_tags(jdata)
    try:
        countries = _countries(jdata)
    except KeyError:
        countries = []

    family = _is_family_safe(jdata)
    sus = _get_subscribers(jdata)
    socials = _get_primary_links(jdata)
    # try:
    #     playlists = _get_playlists(jdata)
    # except KeyError:
    #     playlists = None
    # try:
    #     main_video = _get_main_video(jdata)
    # except KeyError:
    #     main_video = None
    return ChannelMeta(
        id=_get_attr(attrs, "channelId"),
        name=_get_attr(attrs, "name"),
        description=_get_attr(attrs, "og:description"),
        thumbnail_url=_get_attr(attrs, "og:image"),
        available_countries=countries,
        tags=tags,
        subscribers=sus,
        family_safe=family,
        crawled_at=datetime.utcnow(),
        # playlists=playlists,
        # main_video=main_video,
        location=country,
        joined=joined,
        view_count=view_count,
        social_links=socials
        
    )

def from_id2url(id_) -> str:
    return f"https://www.youtube.com/channel/{id_}"
