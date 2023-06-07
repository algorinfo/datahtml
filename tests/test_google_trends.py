from datahtml.google_trends import parse_entries, GoogleTrend
from datahtml.parsers import text2soup


def test_google_trends_parse():
    with open("tests/google_trends_rss.xml", "r") as f:
        data = f.read()

    soup = text2soup(data)
    trends = parse_entries(soup)
    assert isinstance(trends[0], GoogleTrend)
