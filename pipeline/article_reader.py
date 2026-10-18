"""Read the articles an X post links to, for analysis depth.

Many news sites (The Verge, Business Insider) hydrate a paywall with
JavaScript but serve the article body in the initial HTML as schema.org
JSON-LD `articleBody`. One plain GET of that HTML, before any script runs,
is enough; nothing here sends cookies, spoofs a crawler, or retries around a
block. robots.txt is honoured.

Article text is used only as model input. It is never persisted: the
repository is public, so evidence keeps only metadata about what was read.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup
from readability import Document

from pipeline.fetchers.html_page import _HEADERS

ROBOTS_AGENT = "CrawlerPolicy"
MAX_ARTICLES = 3
MAX_CHARS = 12_000
_MIN_CHARS = 400
_TIMEOUT = httpx.Timeout(20.0, connect=10.0)
_SKIP_HOSTS = {"x.com", "twitter.com", "t.co"}


@dataclass(frozen=True)
class Article:
    url: str
    final_url: str
    method: str
    title: str
    text: str

    def as_metadata(self) -> dict[str, object]:
        return {
            "url": self.url,
            "final_url": self.final_url,
            "method": self.method,
            "chars": len(self.text),
            "sha256": hashlib.sha256(self.text.encode()).hexdigest(),
        }


def _host(url: str) -> str:
    return urlsplit(url).netloc.lower().removeprefix("www.")


def _json_ld_article(soup: BeautifulSoup) -> tuple[str, str]:
    best_title, best_body = "", ""
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except ValueError:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
                continue
            if not isinstance(node, dict):
                continue
            if isinstance(node.get("@graph"), list):
                stack.extend(node["@graph"])
            body = node.get("articleBody")
            if isinstance(body, str) and len(body) > len(best_body):
                best_body = body
                best_title = str(node.get("headline") or "")
    return best_title, " ".join(best_body.split())


def extract_article(html: str) -> tuple[str, str, str]:
    """Return (method, title, text) for the richest body in static HTML."""
    soup = BeautifulSoup(html, "lxml")
    ld_title, ld_body = _json_ld_article(soup)
    document = Document(html)
    readable = " ".join(
        BeautifulSoup(document.summary(), "lxml").get_text(" ", strip=True).split()
    )
    title = ld_title or document.short_title() or ""
    if len(ld_body) >= len(readable):
        return "json-ld", title, ld_body
    return "readability", title, readable


async def _robots_allows(client: httpx.AsyncClient, url: str) -> bool:
    parts = urlsplit(url)
    try:
        response = await client.get(f"{parts.scheme}://{parts.netloc}/robots.txt")
    except httpx.HTTPError:
        return True
    if response.status_code >= 400:
        return True
    parser = RobotFileParser()
    parser.parse(response.text.splitlines())
    return parser.can_fetch(ROBOTS_AGENT, url)


async def read_article(client: httpx.AsyncClient, url: str) -> Article:
    if not await _robots_allows(client, url):
        raise PermissionError("robots.txt disallows this URL")
    response = await client.get(url)
    response.raise_for_status()
    if "html" not in response.headers.get("content-type", "html"):
        raise ValueError("linked URL is not an HTML page")
    method, title, text = extract_article(response.text)
    if len(text) < _MIN_CHARS:
        raise ValueError(f"no article body in static HTML ({len(text)} chars)")
    return Article(
        url=url,
        final_url=str(response.url),
        method=method,
        title=title,
        text=text[:MAX_CHARS],
    )


async def read_linked_articles(
    urls: list[str],
    *,
    client: httpx.AsyncClient | None = None,
) -> tuple[list[Article], list[dict[str, object]]]:
    """Read up to MAX_ARTICLES linked pages; return articles and per-URL metadata."""
    targets = [
        url
        for url in dict.fromkeys(urls)
        if url.startswith("https://") and _host(url) not in _SKIP_HOSTS
    ][:MAX_ARTICLES]
    articles: list[Article] = []
    log: list[dict[str, object]] = []
    if not targets:
        return articles, log
    owns_client = client is None
    active = client or httpx.AsyncClient(
        headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True
    )
    try:
        for url in targets:
            try:
                article = await read_article(active, url)
            except Exception as error:  # one bad link must not block analysis
                log.append({"url": url, "error": f"{type(error).__name__}: {error}"[:200]})
                continue
            articles.append(article)
            log.append(article.as_metadata())
    finally:
        if owns_client:
            await active.aclose()
    return articles, log


def article_context(articles: list[Article]) -> str:
    return "\n\n".join(
        f"=== LINKED ARTICLE ({_host(article.final_url)}) ===\n"
        f"Title: {article.title}\n{article.text}"
        for article in articles
    )
