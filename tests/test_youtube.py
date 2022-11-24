from datahtml import youtube


def test_transform():
    with open("tests/test.html", "r") as f:
        data = f.read()
    parsed = youtube.transform_channel(data)
    assert isinstance(parsed, youtube.ChannelMeta)
