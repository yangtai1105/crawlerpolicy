"""Fetcher contracts. Each fetcher implementation returns a FetchResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ResultMode(str, Enum):
    # html_page / ietf_draft: full content diffed against previous snapshot
    DIFFABLE = "diffable"
    # rss_feed / github_repo: list of candidate items, each potentially a separate event
    PER_ITEM = "per_item"


@dataclass
class CandidateItem:
    """One item from a per-item source (RSS post, GitHub release, etc.)."""
    guid: str
    title: str
    published_at: datetime | None
    url: str | None
    summary: str
    body: str


@dataclass
class FetchResult:
    mode: ResultMode
    normalized_content: str | None = None
    raw_ext: str = "html"
    items: list[CandidateItem] = field(default_factory=list)
