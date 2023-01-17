from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Union
from urllib.parse import parse_qs, urlparse, quote

import feedparser
import httpx
from bs4 import BeautifulSoup as BS

from datahtml.parsers import extract_json, extract_metadata, findkeys


@dataclass
class ChannelVideo:
    id: str
    thumbnail_url: str
    title: str
    published_text: str
    viewcount_text: str
    crawled_at: datetime


@dataclass
class RelatedVideo:
    id: str
    title: str
    channel_id: str
    view_count: str


@dataclass
class Video:
    id: str
    channel_id: str
    author: str
    thumbnail_url: str
    title: str
    description: str
    category: str
    keywords: List[str]
    view_count: str
    length_secs: str
    # family_safe: bool
    related: List[RelatedVideo]
    crawled_at: datetime


@dataclass
class RSSVideo:
    id: str
    title: str
    description: str
    published: str
    thumbnail: str
    views: str


@dataclass
class SearchVideo:
    id: str
    title: str
    channel_id: str
    views_count: str


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
    family_safe: bool
    crawled_at: datetime
    tags: list = field(default_factory=list)
    available_countries: List[str] = field(default_factory=list)
    # playlists: Optional[List[ChannelPlaylist]] = None
    # main_video: Optional[str] = None
    subscribers: Optional[str] = None
    view_count: Optional[str] = None
    joined: Optional[str] = None
    location: Optional[str] = None
    social_links: list = field(default_factory=list)


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
    try:
        url = link["navigationEndpoint"]["urlEndpoint"]["url"]
        parsed = urlparse(url)
        q = parse_qs(parsed.query)
        social = q.get("q")[0]
    except TypeError:
        social = None
    return social


def _get_primary_links(data):
    keys = list(findkeys(data, "primaryLinks"))
    final = []
    if keys:
        links = keys[0]
        for link in links:
            try:
                sl = _parse_social_link(link)
                final.append(sl)
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
    try:
        tags = data[1]["microformat"]["microformatDataRenderer"]["tags"]
    except KeyError:
        tags = None
    return tags


def _countries(data):
    return data[1]["microformat"]["microformatDataRenderer"]["availableCountries"]


def _is_family_safe(data):
    return data[1]["microformat"]["microformatDataRenderer"]["familySafe"]


def _get_subscribers(data):
    try:
        s = data[1]["header"]["c4TabbedHeaderRenderer"]["subscriberCountText"][
            "simpleText"
        ]
        s = s.replace("\xa0", " ")
    except KeyError:
        s = None

    return s


def _get_channel_video(vid):
    v = ChannelVideo(
        id=vid["videoId"],
        title=vid["title"]["simpleText"],
        thumbnail_url=vid["thumbnail"]["thumbnails"][0]["url"],
        published_text=vid["publishedTimeText"]["simpleText"],
        viewcount_text=vid["viewCountText"]["simpleText"],
        crawled_at=datetime.utcnow(),
    )
    return v


def _get_playlists(data):
    page = data[1]["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0][
        "tabRenderer"
    ]["content"]["sectionListRenderer"]["contents"]
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
                url=playlist["title"]["runs"][0]["navigationEndpoint"][
                    "commandMetadata"
                ]["webCommandMetadata"]["url"],
                videos=videos_obj,
                crawled_at=datetime.utcnow(),
            )
            playlists_obj.append(playlist_obj)
    return playlists_obj


def _get_main_video(data):
    page = data[1]["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0][
        "tabRenderer"
    ]["content"]["sectionListRenderer"]["contents"]
    renderer = page[0]["itemSectionRenderer"]["contents"][0][
        "channelVideoPlayerRenderer"
    ]
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


def _get_related_vids(data):
    """get related videos in a youtube video"""
    results = findkeys(data, "secondaryResults")
    related = []
    for level in results:
        if level.get("secondaryResults"):
            for _v in findkeys(
                level["secondaryResults"]["results"], "compactVideoRenderer"
            ):
                try:
                    t = _v["longBylineText"]
                    channel_id = t["runs"][0]["navigationEndpoint"]["browseEndpoint"][
                        "browseId"
                    ]
                    vid = RelatedVideo(
                        id=_v["videoId"],
                        title=_v["title"]["simpleText"],
                        view_count=_v["viewCountText"]["simpleText"],
                        channel_id=channel_id,
                    )
                    related.append(vid)
                except KeyError:
                    pass
    return related


def _get_vid_id(data):
    data[0]
    results = list(findkeys(data[0], "videoId"))
    return results[0]


def _get_vid_channel_id(data):
    results = list(findkeys(data[0], "channelId"))
    return results[0]


def _get_vid_category(data):
    results = list(findkeys(data, "category"))
    return results[0]


def transform_search(html):
    soup = BS(html, "lxml")
    jdata = extract_json(soup)
    results = jdata[1]["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
        "sectionListRenderer"
    ]["contents"][0]["itemSectionRenderer"]["contents"]
    search = []
    for r in results:
        if r.get("videoRenderer"):
            channel_id = r["videoRenderer"]["longBylineText"]["runs"][0][
                "navigationEndpoint"
            ]["browseEndpoint"]["browseId"]
            title = r["videoRenderer"]["title"]["runs"][0]["text"]
            videoid = r["videoRenderer"]["videoId"]
            views = r["videoRenderer"]["viewCountText"]["simpleText"]
            sv = SearchVideo(
                id=videoid,
                title=title,
                channel_id=channel_id,
                views_count=views,
            )
            search.append(sv)
    return search


def transform_video(html) -> Video:
    soup = BS(html, "lxml")
    # attrs = extract_metadata(soup)
    jdata = extract_json(soup)
    vd = list(findkeys(jdata, "videoDetails"))[0]

    id_ = vd["videoId"]
    channel = vd["channelId"]
    author = vd["author"]
    views = vd["viewCount"]
    image = vd["thumbnail"]["thumbnails"][0]["url"]
    keywords = vd.get("keywords", [])
    description = vd["shortDescription"]
    title = vd["title"]
    length = vd["lengthSeconds"]
    category = _get_vid_category(jdata)
    related = _get_related_vids(jdata)

    return Video(
        id=id_,
        channel_id=channel,
        author=author,
        thumbnail_url=image,
        title=title,
        description=description,
        category=category,
        keywords=keywords,
        view_count=views,
        length_secs=length,
        related=related,
        crawled_at=datetime.utcnow(),
    )


def transform_channel(html) -> ChannelMeta:
    soup = BS(html, "lxml")
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
        social_links=socials,
    )


def transform_rss(xml: str) -> List[RSSVideo]:
    d = feedparser.parse(xml)
    videos = [
        RSSVideo(
            id=x.yt_videoid,
            title=x.title,
            description=x.summary,
            published=x.published,
            thumbnail=x.media_thumbnail[0]["url"],
            views=x.media_statistics["views"],
        )
        for x in d.entries
    ]
    return videos


def channel_rss_from_id(id_: str):
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={id_}"


def channel_url_from_id(id_: str) -> str:
    return f"https://www.youtube.com/channel/{id_}"


def video_url_from_id(id_: str) -> str:
    return f"https://www.youtube.com/watch?v={id_}"


def text2search_url(txt: str) -> str:
    words = txt.replace(" ", "+")
    return f"https://www.youtube.com/results?search_query={words}"
