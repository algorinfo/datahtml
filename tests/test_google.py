from datahtml import google


def test_transform_search():
    with open("tests/google_search.html", "r") as f:
        data = f.read()
    parsed = google.transform_result(data)
    assert isinstance(parsed, google.SearchResult)
