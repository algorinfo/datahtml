from datahtml import parsers, root


def test_root_sitemap_sitemaps():
    with open("tests/root_carrefour_sitemap.xml", "r") as f:
        data = f.read()
    soup = parsers.text2soup(data)
    sites = root.sitemap_sitemaps(soup, filter_dt=None)

    assert len(sites) > 0


def test_root_sitemap_from_robots():
    with open("tests/robots.txt", "r") as f:
        data = f.read()

    sites = root.get_sitemaps_from_robots(data)

    assert len(sites) > 0
