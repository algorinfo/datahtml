from datahtml import youtube


def test_transform_channel():
    with open("tests/youtube_channel.html", "r") as f:
        data = f.read()
    parsed = youtube.transform_channel(data)
    assert isinstance(parsed, youtube.ChannelMeta)


def test_transform_video():
    with open("tests/youtube_video.html", "r") as f:
        data = f.read()
    parsed = youtube.transform_video(data)
    assert isinstance(parsed, youtube.Video)


def test_transform_search():
    with open("tests/youtube_search.html", "r") as f:
        data = f.read()
    parsed = youtube.transform_search(data)
    assert isinstance(parsed[0], youtube.SearchVideo)


def test_transform_rss():
    with open("tests/youtube_channel_rss.xml", "r") as f:
        data = f.read()
    parsed = youtube.transform_rss(data)
    assert isinstance(parsed[0], youtube.RSSVideo)
