import os
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field


class Topics(Enum):
    music = "/m/04rlf"
    christian_music = "/m/02mscn"
    classhical_music = "/m/0ggq0m"
    country = "/m/01lyv"
    electronic_music = "/m/02lkt"
    hip_hop_music = "/m/0glt670"
    independent_music = "/m/05rwpb"
    jazz = "/m/03_d0"
    music_asia = "/m/028sqc"
    music_latin = "/m/0g293"
    pop_music = "/m/064t9"
    reggae = "/m/06cqb"
    rhythm_blues = "/m/06j6l"
    rock_music = "/m/06by7"
    sould_music = "/m/0gywn"
    ## gaming_topics
    gaming = "/m/0bzvm2"  # Gaming (parent topic)
    action_game = "/m/025zzc"
    adventure = "/m/02ntfj"
    casual_game = "/m/0b1vjn"
    music_game = "/m/02hygl"
    puzzle_game = "/m/04q1x3q"
    racing_game = "/m/01sjng"
    role_playing = "/m/0403l3g"
    simulation = "/m/021bp2"
    sports_game = "/m/022dc6"
    strategy_game = "/m/03hf_rm"
    ## Sports topics
    sports = "/m/06ntj"  # Sports (parent topic)
    american_football = "/m/0jm_"
    baseball = "/m/018jz"
    basketball = "/m/018w8"
    boxing = "/m/01cg"
    cricket = "/m/09xp_"
    football = "/m/02vx4"
    golf = "/m/037hz"
    ice_hocket = "/m/03tmr"
    martial_arts = "/m/01h7lh"
    motorsport = "/m/0410tth"
    tennis = "/m/07bs0"
    volleyball = "/m/07_53"
    ## Entertainment topics
    entertainment = "/m/02jjt"
    humor = "/m/09kqc"
    movies = "/m/02vxn"
    performing_artes = "/m/05qjc"
    wrestling = "/m/066wd"
    tv_shows = "/m/0f2f9"
    # Lifestyle topics
    lifestyle = "/m/019_rr"
    fashion = "/m/032tl"
    fitness = "/m/027x7n"
    food = "/m/02wbm"
    hobby = "/m/03glg"
    pets = "/m/068hy"
    beauty = "/m/041xxh"  # Physical attractiveness [Beauty]
    technology = "/m/07c1v"
    tourism = "/m/07bxq"
    vehicles = "/m/07yv9"
    # Society topics
    society = "/m/098wr"
    business = "/m/09s1f"
    health = "/m/0kt51"
    military = "/m/01h6rj"
    politics = "/m/05qt0"
    religion = "/m/06bvp"
    # Other topics
    knowledge = "/m/01k8wb"


class SearchQuery(BaseModel):
    """
    https://developers.google.com/youtube/v3/docs/search/list
    """

    q: str
    part: str = "snippet"
    next_token: Optional[str] = Field(alias="nextToken", default=None)
    event_type: Optional[str] = Field(alias="eventType", default=None)
    max_results: int = Field(alias="maxResults", default=50)
    order: str = "relevance"
    type_: Optional[str] = Field(alias="type", default=None)
    page_token: Optional[str] = Field(alias="pageToken", default=None)
    topic: Optional[Topics] = Field(alias="topicId", default=None)
    related_to_video_id: Optional[str] = Field(alias="relatedToVideoId", default=None)
    region_code: Optional[str] = Field(alias="regionCode", default=None)
    lang: Optional[str] = Field(alias="relevanceLanguage", default=None)

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True


class SearchItem(BaseModel):
    id: str
    kind: str
    published_at: str = Field(alias="publishedAt")
    publish_time: str = Field(alias="publishTime")
    title: str
    description: str
    thumbnail: str
    channel_id: str = Field(alias="channelId")
    channel_title: str = Field(alias="channelTitle")

    class Config:
        allow_population_by_field_name = True


class SearchResponse(BaseModel):
    items: List[SearchItem]
    next_page: Optional[str] = Field(alias="nextPageToken", default=None)
    total_results: Optional[str] = Field(alias="totalResults", default=None)

    class Config:
        allow_population_by_field_name = True


class VideoQuery(BaseModel):
    part: str = "snippet,contentDetails,statistics"
    id: Optional[str] = None
    max_results: int = Field(alias="maxResults", default=50)
    page_token: Optional[str] = Field(alias="pageToken", default=None)
    region_code: Optional[str] = Field(alias="regionCode", default=None)
    video_category: Optional[str] = Field(alias="videoCategoryId", default=None)
    chart: Optional[str] = None

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True


class VideoItem(BaseModel):
    id: str
    kind: str
    tags: List[str]
    published_at: str = Field(alias="publishedAt")
    default_audio_lang: Optional[str] = Field(
        alias="defaultAudioLanguage", default=None
    )
    default_lang: Optional[str] = Field(alias="defaultLanguage", default=None)
    title: str
    thumbnail: str
    channel_id: str = Field(alias="channelId")
    channel_title: str = Field(alias="channelTitle")
    view_count: str = Field(alias="viewCount")
    like_count: str = Field(alias="likeCount")
    comment_count: str = Field(alias="commentCount")

    class Config:
        allow_population_by_field_name = True


class VideoResponse(BaseModel):
    items: List[VideoItem]


class Client:
    URL = "https://youtube.googleapis.com/youtube/v3"

    def __init__(self, api_key=os.getenv("YOUTUBE_KEY"), debug=False):
        self._api_key = api_key
        self._h = {
            # "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        self._debug = debug
        self._raw_rsp = None

    def _store_rsp(self, rsp: httpx.Response):
        if self._debug:
            self._raw_rsp = rsp

    @property
    def _response(self) -> httpx.Response:
        return self._raw_rsp

    @staticmethod
    def create_search(q: str) -> SearchQuery:
        return SearchQuery(q=q)

    @staticmethod
    def create_video_popular(region="AR", video_category=None) -> VideoQuery:
        return VideoQuery(
            region_code=region, video_category=video_category, chart="mostPopular"
        )

    @staticmethod
    def create_video(id_) -> VideoQuery:
        return VideoQuery(id=id_)

    def _dict2searchitem(self, item: Dict[str, Any]) -> SearchItem:
        id_ = item["id"].get("videoId")
        if not id_:
            id_ = item["id"].get("channelId")

        s = item["snippet"]
        pat = s["publishedAt"]
        pat2 = s["publishTime"]
        return SearchItem(
            id=id_,
            kind=item["kind"],
            published_at=pat,
            publish_time=pat2,
            title=s["title"],
            description=s["description"],
            thumbnail=s["thumbnails"]["default"]["url"],
            channel_id=s["channelId"],
            channel_title=s["channelTitle"],
        )

    def _dict2searchresponse(self, rsp: Dict[str, Any]) -> SearchResponse:
        items = [self._dict2searchitem(i) for i in rsp["items"]]
        return SearchResponse(
            items=items,
            next_page=rsp["nextPageToken"],
            total_results=rsp["pageInfo"]["totalResults"],
        )

    def search(self, q: SearchQuery) -> SearchResponse:
        data = q.dict(by_alias=True, exclude_none=True)
        data.update({"key": self._api_key})
        uri = urlencode(data)
        rsp = httpx.get(f"{self.URL}/search?{uri}", headers=self._h)
        self._store_rsp(rsp)

        return self._dict2searchresponse(rsp.json())

    def video(self, v: VideoQuery) -> VideoResponse:
        data = v.dict(by_alias=True, exclude_none=True)
        data.update({"key": self._api_key})
        uri = urlencode(data)
        rsp = httpx.get(f"{self.URL}/videos?{uri}", headers=self._h)
        self._store_rsp(rsp)

        return self._dict2videoresponse(rsp.json())

    def _dict2videoitem(self, item: Dict[str, Any]) -> VideoItem:
        s = item["snippet"]
        st = item["statistics"]

        return VideoItem(
            id=item["id"],
            kind=item["kind"],
            tags=s["tags"],
            published_at=s["publishedAt"],
            title=s["title"],
            thumbnail=s["thumbnails"]["default"]["url"],
            default_audio_lang=s.get("defaultAudioLanguage"),
            default_lang=s.get("defaultLanguage"),
            channel_id=s["channelId"],
            channel_title=s["channelTitle"],
            view_count=st["viewCount"],
            like_count=st["likeCount"],
            comment_count=st["commentCount"],
        )

    def _dict2videoresponse(self, rsp: Dict[str, Any]) -> VideoResponse:
        items = [self._dict2videoitem(i) for i in rsp["items"]]
        return VideoResponse(
            items=items,
            next_page=rsp.get("nextPageToken"),
            total_results=rsp["pageInfo"]["totalResults"],
        )
