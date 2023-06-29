from datahtml import parsers

u1 = "https://www.google.com/"
u2 = "https://www.google.com/test?query=testq"
u3 = "http://google.com"
u4 = "https://google.com.ar"

u5 = "https://www.infobae.com/politica/2023/06/29/crece-la-tension-diplomatica-valdes-afirmo-que-paraguay-hostiga-a-pescadores-argentinos-y-pidio-la-intervencion-de-cancilleria/"
u6 = "https://www.pe.com/morales-y-bullrich-reeditaron-los-reproches-y-profundizaron-las-diferencias-sobre-el-rumbo-de-jxc.phtml"
u7 = "https://www.infobae.com/leamos/2023/06/29/los-dias-que-victoria-ocampo-estuvo-presa-por-antiperonista-usted-no-tiene-derecho-a-nada/"

def test_parsers_parse_url():
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

def test_parsers_url_norm():
    _, r1 = parsers.url_norm(u1)
    _, r2 = parsers.url_norm(u2)

    assert r1 == "www.google.com"
    assert r2 == "www.google.com/test"

def test_parsers_text_from_link():
    t1 = parsers.text_from_link(u5)
    t2 = parsers.text_from_link(u6)
    t3 = parsers.text_from_link(u7)

    assert "argentinos" in u5
    assert "reproches" in u6
    assert "derecho" in u7
