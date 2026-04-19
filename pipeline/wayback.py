"""Wayback Machine baseline fetcher.

Given a URL and a target age window (e.g. "180–365 days ago"), find the
closest archived snapshot via Wayback's CDX API and return its content.
Used for bootstrapping crawler-pillar sources with real history so the
first live pipeline run produces a meaningful "6 months ago vs today" diff.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup
from readability import Document

_UA = "ai-ecosystem-tracker/0.1 (wayback-baseline)"
_TIMEOUT = httpx.Timeout(60.0)


@dataclass
class WaybackSnapshot:
    archived_at: datetime
    content: str
    wayback_url: str


async def fetch_wayback_snapshot(
    source_url: str,
    *,
    target_days_ago: int = 180,
    window_start_days: int = 150,
    window_end_days: int = 400,
    content_selector: str | None = None,
) -> WaybackSnapshot | None:
    """Fetch an archived snapshot of source_url from roughly target_days_ago.

    Uses Wayback's CDX API to find all snapshots within
    [window_start_days, window_end_days] and picks the one closest to
    target_days_ago. Returns None if no snapshot exists in that range.
    """
    now = datetime.now(tz=timezone.utc)
    window_start = now - timedelta(days=window_end_days)
    window_end = now - timedelta(days=window_start_days)
    target = now - timedelta(days=target_days_ago)

    cdx_url = (
        "https://web.archive.org/cdx/search/cdx"
        f"?url={quote(source_url, safe='')}"
        f"&from={window_start.strftime('%Y%m%d')}"
        f"&to={window_end.strftime('%Y%m%d')}"
        "&filter=statuscode:200"
        "&filter=mimetype:text/html"
        "&output=json"
        "&limit=100"
    )

    async with httpx.AsyncClient(
        headers={"User-Agent": _UA}, timeout=_TIMEOUT, follow_redirects=True
    ) as client:
        resp = await client.get(cdx_url)
        resp.raise_for_status()
        rows = resp.json()
        # First row is header: ["urlkey","timestamp","original","mimetype","statuscode","digest","length"]
        if len(rows) <= 1:
            return None

        # Pick snapshot closest to target date.
        best: tuple[timedelta, str, str] | None = None
        for row in rows[1:]:
            ts, original = row[1], row[2]
            try:
                snap_dt = datetime.strptime(ts, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            distance = abs(snap_dt - target)
            if best is None or distance < best[0]:
                best = (distance, ts, original)
        if best is None:
            return None

        _, ts, original = best
        snap_dt = datetime.strptime(ts, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        # `id_` suffix on the timestamp returns the raw archived HTML
        # without Wayback's injected toolbar frame.
        wayback_url = f"https://web.archive.org/web/{ts}id_/{original}"
        page_resp = await client.get(wayback_url)
        page_resp.raise_for_status()
        normalized = _normalize(page_resp.text, content_selector)

    return WaybackSnapshot(archived_at=snap_dt, content=normalized, wayback_url=wayback_url)


_MIN_READABLE_CHARS = 1500


def _normalize(html: str, content_selector: str | None) -> str:
    """Match fetch_html_page normalization: try readability or selector, but
    fall back to full body text when the result is suspiciously short (common
    on archived Intercom-style pages and developer-doc sidebars)."""
    if content_selector:
        soup = BeautifulSoup(html, "lxml")
        node = soup.select_one(content_selector)
        if node is not None:
            text = _strip_and_join(node)
            if text:
                return text

    readability_text = ""
    try:
        article_html = Document(html).summary(html_partial=True)
        readability_text = _strip_and_join(BeautifulSoup(article_html, "lxml"))
    except Exception:
        readability_text = ""

    if len(readability_text) >= _MIN_READABLE_CHARS:
        return readability_text

    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(["script", "style", "noscript", "nav", "header", "footer", "aside"]):
        tag.decompose()
    body = soup.body or soup
    full_text = _strip_and_join(body)
    return full_text if len(full_text) > len(readability_text) else readability_text


def _strip_and_join(node) -> str:
    for tag in node.find_all(["script", "style", "noscript"]):
        tag.decompose()
    text = node.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
