from datahtml import parsers


def test_parsers_parse_url():
    u1 = "https://www.google.com/"
    u2 = "https://www.google.com/test?query=testq"
    u3 = "http://google.com"
    u4 = "https://google.com.ar"

    r1 = parsers.parse_url(u1)
    r2 = parsers.parse_url(u2)
    r3 = parsers.parse_url(u3)
    r4 = parsers.parse_url(u4)

    assert r1.url_short == "www.google.com" 
    assert r2.url_short == "www.google.com/test"
    assert r1.secure
    assert r3.secure is False
    assert r2.www
    assert r3.www is False
    assert r1.domain_base == "google.com"
    assert r1.tld == "com"
    assert r4.tld == "ar"
    
