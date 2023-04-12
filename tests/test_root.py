from datahtml import parsers, sitemap


def test_root_sitemap_sitemaps():
    with open("tests/root_carrefour_sitemap.xml", "r") as f:
        data = f.read()
    soup = parsers.text2soup(data)
    sites = sitemap.sitemap_sitemaps(soup, filter_dt=None)

    assert len(sites) > 0


def test_root_sitemap_from_robots():
    with open("tests/robots.txt", "r") as f:
        data = f.read()

    sites = sitemap.get_sitemaps_from_robots(data)

    assert len(sites) > 0
