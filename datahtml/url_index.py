from collections.abc import Callable
from unidecode import unidecode
import re
import sqlite3
from typing import List, Callable
from attr import define
from datahtml.types import URL
from datahtml.parsers import parse_url

_exp = r'[^a-zA-z]'

def norm_words(words):
    new_ = unidecode(words) 
    rsp = re.sub(_exp, ' ', new_)
    final = " ".join(rsp.split())
    return final

@define
class SearchLink:
    text: str
    url: URL

    @classmethod
    def parse(cls, url: str, text: str) -> "SearchLink":
        u = parse_url(url)
        obj = cls(text=text, url=u)
        return obj


class URLIndex:

    def __init__(self, uri=":memory:", norm_func: Callable=norm_words):
        self.conn = sqlite3.connect(uri)
        self.norm: Callable = norm_func

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS content
        (id INTEGER PRIMARY KEY,url TEXT NOT NULL UNIQUE, text TEXT, domain TEXT);
        """
        )
        cur.execute(
            'CREATE VIRTUAL TABLE IF NOT EXISTS search_ix using fts5(id UNINDEXED, url UNINDEXED, text, domain, tokenize="ascii", content=content, content_rowid=id);'
        )

        cur.execute(
            """CREATE INDEX content_domain_idx ON content(domain);"""

        )
        cur.execute(
            """
        -- Triggers to keep the FTS index up to date.
        CREATE TRIGGER content_ai AFTER INSERT ON content BEGIN
          INSERT INTO search_ix(rowid, url, text, domain) VALUES (new.id, new.url, new.text, new.domain);
        END;
        """
        )
        cur.execute("""
        CREATE TRIGGER content_ad AFTER DELETE ON content BEGIN
          INSERT INTO search_ix(search_ix, rowid, url, text, domain) VALUES('delete', old.id, old.url, old.text, old.domain);
        END;
        """)
        cur.execute("""
        CREATE TRIGGER content_au AFTER UPDATE ON content BEGIN
          INSERT INTO search_ix(search_ix, rowid, url, text, domain) VALUES('delete', old.id, old.url, old.text, old.domain);
          INSERT INTO saerch_ix(rowid, url, text, domain) VALUES (new.id, new.url, new.text, new.domain);
        END;
        """
        )
        cur.close()
    def build(self, links: List[SearchLink]):
        self._create_tables()
        cur = self.conn.cursor()
        for link in links:
            text = self.norm(link.text)
            cur.execute(
            "insert into content (url, text, domain) values (?, ?, ?);",
            (
                link.url.fullurl,
                text,
                link.url.domain_base
            ),
        )
        cur.close()
    def add(self, link: SearchLink):

        text = self.norm(link.text)
        cur = self.conn.cursor()
        cur.execute(
            "insert into content (url, text, domain) values (?, ?, ?);",
            (
                link.url.fullurl,
                text,
                link.url.domain_base
            ),
        )
        cur.close()

    def search(self, text, domain=None, top_n=5):
        search = self.norm(text)
        cur = self.conn.cursor()
        if domain:
            rows = cur.execute(
                f"""select * from search_ix where text MATCH '{search}' and domain='{domain}'
                                    order by rank limit {top_n}"""
            ).fetchall()

        else:
            rows = cur.execute(
                f"""select * from search_ix where text MATCH '{search}'
                                    order by rank limit {top_n}"""
            ).fetchall()
        cur.close()
        urls = []
        for r in rows:
            # print(r[1])
            _u = parse_url(r[1])
            link = SearchLink(text=r[2], url=_u)
            urls.append(link)

        return urls
