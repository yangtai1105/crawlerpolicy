"""Raw item log: every candidate RSS/GitHub item that passes keyword_filter
gets appended here, regardless of whether it becomes a material event.

Purpose: long-term trend analysis. The curated `content/events/` feed only
contains items the analyzer deemed `material`. The raw log captures the full
corpus the pipeline saw, so future analysis ("how often did source X mention
Y in 2026?") doesn't need re-scraping.

Format: JSONL, one item per line, partitioned by month per source:
  content/raw/{slug}/{YYYY-MM}.jsonl
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def append(
    raw_root: Path,
    slug: str,
    *,
    guid: str,
    title: str,
    summary: str,
    url: str | None,
    published_at: datetime | None,
    keyword_pass: bool,
    relevance_pass: bool | None,
    change_kind: str | None,
    importance: float | None,
    recorded_at: datetime,
) -> None:
    """Append one item record. Idempotent if called with the same guid twice
    (but we don't enforce — guids are already deduplicated by state.last_seen_guids)."""
    month = (published_at or recorded_at).strftime("%Y-%m")
    folder = raw_root / slug
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / f"{month}.jsonl"
    record = {
        "guid": guid,
        "title": title,
        "summary": summary[:2000],
        "url": url,
        "published_at": published_at.isoformat() if published_at else None,
        "recorded_at": recorded_at.isoformat(),
        "keyword_pass": keyword_pass,
        "relevance_pass": relevance_pass,
        "change_kind": change_kind,
        "importance": importance,
    }
    with p.open("a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
