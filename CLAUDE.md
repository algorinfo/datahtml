# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**datahtml** is a Python library for crawling and extracting data from HTML, XML, RSS, sitemaps, and social media content. It provides pluggable HTTP crawlers, rich URL parsing, and specialized extractors for platforms like YouTube, Google, Facebook, and Instagram.

## Build System

Uses **uv** for dependency management and **hatchling** as build backend. Version is in `datahtml/__about__.py`.

## Common Commands

```bash
# Install dependencies
uv sync

# Run tests with coverage
uv run pytest --cov-report=term-missing --cov-config=pyproject.toml --cov=datahtml --cov=tests
# or: make cov

# Run tests
uv run pytest
# or: make test

# Run a single test
uv run pytest tests/test_foo.py::test_name

# Type checking
uv run mypy datahtml/

# Code formatting
uv run black datahtml/ tests/
uv run isort datahtml/ tests/

# Linting
uv run pylint datahtml/

# Build docs
uv run --group docs sphinx-autobuild docs docs/_build/html --port 9292 --watch ./
# or: make docs-serve

# Build package
uv build
```

## Architecture

### Core Abstractions (`base.py`)

- **`CrawlerSpec`** — Abstract base class for HTTP crawlers. Defines sync `get()` and async `aget()` methods. All crawler implementations follow this interface.
- **`CrawlResponse`** — Wraps HTTP responses with content-type detection (`is_json`, `is_xml`, `is_txt`).

### Main Entry Points

- **`web.WebDocument`** — Primary HTML parsing interface. Wraps BeautifulSoup and provides extraction methods: `links()`, `images()`, `meta_og()`, `ld_json()`, `article()`, `metas()`.
- **`web.download(url, crawler)`** — Fetch and parse a URL into a WebDocument.
- **`crawler.LocalCrawler`** — Default httpx-based crawler with proxy support.

### Data Models (`types.py`)

- **`URL`** — Rich URL representation with multiple normalizations (`fullurl`, `url_short`, `norm`, `domain_base`), protocol/www detection, and social network identification.
- **`Link`**, **`ProxyConf`** — Supporting data structures.
- Uses a mix of `dataclasses`, `attrs`, and `pydantic>=2` models.

### Specialized Domain Modules

Each module follows a consistent pattern: dataclasses for data, parsing functions, crawler integration.

| Module | Purpose |
|---|---|
| `rss.py` | RSS/Atom feed parsing via feedparser |
| `sitemap.py` | XML sitemap parsing |
| `news.py` | Article extraction (newspaper3k, optional `news` extra) |
| `google.py` | Google search results parsing |
| `google_trends.py` | Google Trends RSS parsing |
| `youtube.py` | YouTube data structures & page parsing |
| `apis/youtube.py` | YouTube Data API v3 client |
| `wikidata.py` | Wikidata API integration |
| `instagram.py` | Instagram profile parsing |
| `facebook.py` | Facebook page/profile parsing |
| `site.py` | Merges links from HTML, RSS, and sitemaps into deduplicated `LinkMerged` objects |
| `url_index.py` | SQLite FTS5-based full-text search for crawled URLs |

### Contrib Modules (`contrib/`)

- **`contrib/chrome/`** — Chrome DevTools Protocol crawler implementations (v5, v6) as alternative `CrawlerSpec` implementations.

### Key Design Patterns

- **Crawler abstraction**: Pluggable crawlers (LocalCrawler, Chrome variants) via `CrawlerSpec` ABC with sync/async support.
- **Composition**: `WebDocument` composes BeautifulSoup + URL parser + CrawlResponse rather than inheriting.
- **URL normalization**: Multiple representations for different use cases (deduplication via `norm`, display via `url_short`).
- **Optional dependencies**: `newspaper3k` is behind the `news` extra; Chrome crawlers are in `contrib/`.
