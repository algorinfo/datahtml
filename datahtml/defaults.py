import re
AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"
EXTENSIONS_REGEX = r"(\.jpg|\.ico|\.js|\.css|\.png|\.woff2|\.svg)+"
# https://coddingbuddy.com/article/10777844/find-url-with-regex-on-text
URL_REGEX = r"(http|ftp|https):\/\/([\w\-_]+(?:(?:\.[\w\-_]+)+))([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?"
SOCIALS_COM = [
    "facebook.com",
    "instagram.com",
    "t.me",
    "facebook.com",
    "twitter.com",
    "tiktok.com",
    "youtube.com",
    "spotify.com",
    "wikipedia.org",
    "meetup.com",
    "linkedin.com",
    "books.google.com",
    "bit.ly",
    "apps.apple.com",
    "play.google.com",
]

WORDS_REGEX = re.compile(r'\b[A-Za-z]+\b')
OG_KEYS = ["og:url", "og:image", "og:description", "og:type", "og:locale", "og:title"]

