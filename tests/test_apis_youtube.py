import json

from datahtml.apis import youtube


def test_apis_youtube_search():
    c = youtube.Client()
    with open("tests/youtube_search_response.json", "r") as f:
        data = json.loads(f.read())
    y = c._dict2searchresponse(data)
    assert isinstance(y, youtube.SearchResponse)


def test_apis_youtube_video():
    c = youtube.Client()
    with open("tests/youtube_video_response.json", "r") as f:
        data = json.loads(f.read())

    with open("tests/youtube_video_multiple_ids.json", "r") as f:
        data2 = json.loads(f.read())

    y = c._dict2videoresponse(data)
    y2 = c._dict2videoresponse(data2)
    assert isinstance(y, youtube.VideoResponse)
    assert isinstance(y2, youtube.VideoResponse)
