"""Discover new articles on a site that blocks crawlers and has no usable feed.

humansecurity.com (and GlobeNewswire, where HUMAN distributes releases)
answer declared crawlers with a captcha page. A grounded listing query finds
recent posts through Google's index; each cited article is then read the
same way to confirm it exists and learn its real title and date.

Only grounding citations become candidates: the URLs in Gemini's answer text
are often invented. An article that cannot be read yet is left out without
being marked seen, so the next run tries it again.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from pipeline import grounded_reader
from pipeline.fetchers.base import CandidateItem, FetchResult, ResultMode
from pipeline.sources import Source

log = logging.getLogger("gemini_listing")


def article_guid(url: str) -> str:
    """One GUID per article however the index spells its path."""
    return f"{grounded_reader.host(url)}/{grounded_reader._slug(url)}"


async def fetch_gemini_listing(
    source: Source,
    *,
    seen_guids: list[str],
    now: datetime,
    model: str | None = None,
) -> FetchResult:
    lookback_days = source.lookback_days or 14
    urls = await grounded_reader.discover_articles(
        source.listing_domain or "",
        source.query or "",
        lookback_days=lookback_days,
        model=model,
    )
    seen = set(seen_guids)
    earliest = now - timedelta(days=lookback_days)
    items: list[CandidateItem] = []
    # Read and rejected: recorded as seen so they are not read again each run.
    settled: list[str] = []
    for url in urls:
        guid = article_guid(url)
        if guid in seen:
            continue
        try:
            read = await grounded_reader.read_article(url, model=model)
        except grounded_reader.NotIndexed as error:
            log.info("gemini_listing %s: skipping %s (%s)", source.slug, url, error)
            continue
        # An undated or old page is an archive hit, not a new development.
        if read.published_on is None or read.published_on < earliest:
            settled.append(guid)
            continue
        items.append(
            CandidateItem(
                guid=guid,
                title=read.title,
                published_at=read.published_on,
                url=read.url,
                summary="",
                body="",
            )
        )
    log.info("gemini_listing %s: %d cited articles, %d new", source.slug, len(urls), len(items))
    return FetchResult(
        mode=ResultMode.PER_ITEM,
        items=items,
        metadata={"settled_guids": settled},
    )
