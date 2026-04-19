"""RSS feed fetcher. Returns items newer than `since` and not in `seen_guids`."""
from __future__ import annotations

from datetime import datetime, timezone
from time import mktime

import feedparser
import httpx

from pipeline.fetchers.base import CandidateItem, FetchResult, ResultMode
from pipeline.sources import Source

_UA = "ai-ecosystem-tracker/0.1"
_TIMEOUT = httpx.Timeout(30.0)


async def fetch_rss_feed(
    source: Source,
    since: datetime | None,
    seen_guids: list[str],
) -> FetchResult:
    async with httpx.AsyncClient(
        headers={"User-Agent": _UA}, timeout=_TIMEOUT, follow_redirects=True
    ) as client:
        resp = await client.get(source.url)
        resp.raise_for_status()
    parsed = feedparser.parse(resp.text)

    seen = set(seen_guids)
    items: list[CandidateItem] = []
    for entry in parsed.entries:
        guid = getattr(entry, "id", None) or getattr(entry, "link", None)
        if not guid or guid in seen:
            continue
        published = _parse_date(entry)
        if since and published and published < since:
            continue
        summary = getattr(entry, "summary", "") or ""
        body = _extract_body(entry)
        items.append(
            CandidateItem(
                guid=guid,
                title=entry.title,
                published_at=published,
                url=getattr(entry, "link", None),
                summary=summary,
                body=body,
            )
        )
    return FetchResult(mode=ResultMode.PER_ITEM, items=items)


def _parse_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        v = getattr(entry, attr, None)
        if v:
            return datetime.fromtimestamp(mktime(v), tz=timezone.utc)
    return None


def _extract_body(entry) -> str:
    content = getattr(entry, "content", None)
    if content:
        return "\n\n".join(c.value for c in content)
    return getattr(entry, "summary", "") or ""
