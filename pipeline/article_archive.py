"""Keep the articles behind published X signals reachable after the fact.

Two copies, for two audiences:

- a private full-text copy in a separate private GitHub repository, so the
  owner can always reread what the analysis was based on. This repository is
  public, so the text never lands here; the daily workflow checks the private
  repository out at PRIVATE_ARCHIVE_DIR and pushes it after the run.
- a public Wayback Machine snapshot (Save Page Now) for every reader, so a
  link that rots or changes still resolves to the version we read.

Both are opt-in by environment so tests and local runs touch neither.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path

import httpx

from pipeline.article_reader import Article
from pipeline.evidence import EvidenceRecord

_SNAPSHOT = re.compile(r"^https://web\.archive\.org/web/\d{14}/")
_WAYBACK_TIMEOUT = httpx.Timeout(120.0, connect=15.0)
_WAYBACK_UA = "CrawlerPolicy/1.0 (+https://crawlerpolicy.com/about)"


def _private_target() -> tuple[Path, str] | None:
    directory = os.environ.get("PRIVATE_ARCHIVE_DIR", "").strip()
    repo = os.environ.get("PRIVATE_ARCHIVE_REPO", "").strip()
    if not directory or not repo:
        return None
    return Path(directory), repo


def save_private_copies(
    articles: list[Article],
    *,
    record: EvidenceRecord,
    read_at: datetime,
) -> dict[str, str]:
    """Write each article to the private archive; return url -> GitHub link."""
    target = _private_target()
    if target is None:
        return {}
    root, repo = target
    day = (record.published_at or record.detected_at).date().isoformat()
    links: dict[str, str] = {}
    for index, article in enumerate(articles, start=1):
        relative = Path("articles") / day / f"{record.evidence_id}-{index}.md"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {
            "title": article.title,
            "url": article.url,
            "final_url": article.final_url,
            "method": article.method,
            "read_at": read_at.isoformat(),
            "evidence_id": record.evidence_id,
            "x_post": record.source_url,
        }
        frontmatter = "\n".join(f"{key}: {json.dumps(value)}" for key, value in header.items())
        path.write_text(f"---\n{frontmatter}\n---\n\n# {article.title}\n\n{article.text}\n")
        links[article.url] = f"https://github.com/{repo}/blob/main/{relative.as_posix()}"
    return links


def wayback_enabled() -> bool:
    return os.environ.get("WAYBACK_SAVE", "").strip() == "1"


async def _save_one(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        response = await client.get(f"https://web.archive.org/save/{url}")
    except httpx.HTTPError:
        return None
    for header in ("location", "content-location"):
        value = response.headers.get(header, "")
        if value.startswith("/web/"):
            value = f"https://web.archive.org{value}"
        if _SNAPSHOT.match(value):
            return value
    return None


async def save_wayback_snapshots(
    urls: list[str],
    *,
    client: httpx.AsyncClient | None = None,
) -> dict[str, str]:
    """Ask Save Page Now for each URL concurrently; return url -> snapshot."""
    if not urls or (client is None and not wayback_enabled()):
        return {}
    owns_client = client is None
    active = client or httpx.AsyncClient(
        headers={"User-Agent": _WAYBACK_UA},
        timeout=_WAYBACK_TIMEOUT,
        follow_redirects=False,
    )
    try:
        snapshots = await asyncio.gather(*(_save_one(active, url) for url in urls))
    finally:
        if owns_client:
            await active.aclose()
    return {url: snapshot for url, snapshot in zip(urls, snapshots, strict=True) if snapshot}


async def preserve(
    articles: list[Article],
    *,
    record: EvidenceRecord,
    read_at: datetime,
) -> None:
    """Save private and public copies and note them on the evidence's read log."""
    private = save_private_copies(articles, record=record, read_at=read_at)
    public = await save_wayback_snapshots([article.url for article in articles])
    for entry in record.discovery_metadata.get("linked_articles", []):
        url = entry.get("url")
        if url in private:
            entry["saved_copy"] = private[url]
        if url in public:
            entry["archived_copy"] = public[url]
