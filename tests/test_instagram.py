from datahtml.instagram import Instagram
from datahtml.web import WebDocument

def test_instagram_from_webdoc():

    with open("tests/instagram_profile.html", "r") as f:
        data = f.read()
    w = WebDocument(url="https://instagram.com/p/test", html_txt=data, is_root=False)
    ig = Instagram.from_webdoc(w)

    assert isinstance(ig, Instagram)
    assert ig.title
    assert ig.body
    assert isinstance(ig.web, WebDocument)
        
    
    
