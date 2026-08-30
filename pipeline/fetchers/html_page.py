"""HTML page fetcher. Normalizes page content for day-over-day diffing."""
from __future__ import annotations

from urllib.parse import urljoin, urlparse

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
        seen_urls = {str(resp.url)}
        for _ in range(3):
            redirect_url = _document_redirect_target(resp.text, str(resp.url))
            if not redirect_url or redirect_url in seen_urls:
                break
            seen_urls.add(redirect_url)
            resp = await client.get(redirect_url)
            resp.raise_for_status()

    html = resp.text
    if source.content_selector:
        soup = BeautifulSoup(html, "lxml")
        node = soup.select_one(source.content_selector)
        if node is None:
            raise ValueError(f"selector {source.content_selector!r} matched nothing")
        text = _clean_text(node)
    else:
        text = _extract_main_text(html)

    return FetchResult(mode=ResultMode.DIFFABLE, normalized_content=text, raw_ext="html")


def _document_redirect_target(html: str, base_url: str) -> str | None:
    """Resolve an explicit HTML-level relocation without crawling arbitrary links."""
    soup = BeautifulSoup(html, "lxml")
    meta = soup.find(
        "meta",
        attrs={"http-equiv": lambda value: value and value.lower() == "refresh"},
    )
    target: str | None = None
    if meta:
        content = str(meta.get("content", ""))
        for part in content.split(";")[1:]:
            key, separator, value = part.partition("=")
            if separator and key.strip().lower() == "url":
                target = value.strip().strip("'\"")
                break

    visible = _clean_text(soup)
    links = soup.select("a[href]")
    explicit_move = visible.lower().startswith("moved to") and len(links) == 1
    if target is None and len(visible) < 500 and explicit_move:
        target = str(links[0].get("href", "")).strip()

    if not target:
        return None
    resolved = urljoin(base_url, target)
    parsed = urlparse(resolved)
    return resolved if parsed.scheme in {"http", "https"} and parsed.netloc else None


# Below this threshold, readability-lxml probably picked the wrong element —
# common on Intercom help pages, AWS developer docs, and similar — and we lose
# the real article body. Fall back to full-page body text in that case.
_MIN_READABLE_CHARS = 1500


def _extract_main_text(html: str) -> str:
    """Primary: readability.Document.summary. Fallback: full body text minus
    scripts/styles/nav, which is noisier but doesn't lose the UA list."""
    readability_text = ""
    try:
        article_html = Document(html).summary(html_partial=True)
        readability_text = _clean_text(BeautifulSoup(article_html, "lxml"))
    except Exception:
        readability_text = ""

    if len(readability_text) >= _MIN_READABLE_CHARS:
        return readability_text

    # Fallback — strip obvious boilerplate and take the body text.
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(["script", "style", "noscript", "nav", "header", "footer", "aside"]):
        tag.decompose()
    body = soup.body or soup
    full_text = _clean_text(body)
    # If fallback is also tiny, whatever readability gave is still the best we have.
    return full_text if len(full_text) > len(readability_text) else readability_text


def _clean_text(node) -> str:
    """Strip scripts/styles and collapse whitespace to stable normalized text."""
    for tag in node.find_all(["script", "style", "noscript"]):
        tag.decompose()
    text = node.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
