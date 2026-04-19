"""HTML page fetcher. Normalizes page content for day-over-day diffing."""
from __future__ import annotations

import httpx
from bs4 import BeautifulSoup
from readability import Document

from pipeline.fetchers.base import FetchResult, ResultMode
from pipeline.sources import Source

# Browser-like UA — many vendor doc sites 403 anything else. We're a read-only
# daily archive tracker; this is a monitoring pattern, not impersonation.
_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
_HEADERS = {
    "User-Agent": _UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
_TIMEOUT = httpx.Timeout(30.0)


async def fetch_html_page(source: Source) -> FetchResult:
    async with httpx.AsyncClient(
        headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True
    ) as client:
        resp = await client.get(source.url)
        resp.raise_for_status()

    html = resp.text
    if source.content_selector:
        soup = BeautifulSoup(html, "lxml")
        node = soup.select_one(source.content_selector)
        if node is None:
            raise ValueError(f"selector {source.content_selector!r} matched nothing")
        text = _clean_text(node)
    else:
        doc = Document(html)
        article_html = doc.summary(html_partial=True)
        text = _clean_text(BeautifulSoup(article_html, "lxml"))

    return FetchResult(mode=ResultMode.DIFFABLE, normalized_content=text, raw_ext="html")


def _clean_text(node) -> str:
    """Strip scripts/styles and collapse whitespace to stable normalized text."""
    for tag in node.find_all(["script", "style", "noscript"]):
        tag.decompose()
    text = node.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
