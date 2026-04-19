"""Source configuration schema and loader."""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, Field, model_validator


class Pillar(str, Enum):
    CRAWLER = "crawler"
    ECOSYSTEM = "ecosystem"
    AGENT = "agent"


class SourceType(str, Enum):
    HTML_PAGE = "html_page"
    RSS_FEED = "rss_feed"
    GITHUB_REPO = "github_repo"
    IETF_DRAFT = "ietf_draft"


class Source(BaseModel):
    slug: str
    pillar: Pillar
    type: SourceType
    display_name: str

    # html_page + rss_feed
    url: str | None = None
    content_selector: str | None = None

    # rss_feed
    keyword_filter: list[str] | None = None

    # github_repo
    repo: str | None = None
    pr_labels: list[str] = Field(default_factory=list)
    pr_path_globs: list[str] = Field(default_factory=list)

    # ietf_draft
    draft_name: str | None = None

    # Optional Sonnet/Opus override per source
    model: str | None = None

    @model_validator(mode="after")
    def _validate_type_requirements(self) -> Self:
        if self.type in (SourceType.HTML_PAGE, SourceType.RSS_FEED) and not self.url:
            raise ValueError(f"source {self.slug}: {self.type} requires `url`")
        if self.type == SourceType.RSS_FEED and not self.keyword_filter:
            raise ValueError(f"source {self.slug}: rss_feed requires `keyword_filter`")
        if self.type == SourceType.GITHUB_REPO and not self.repo:
            raise ValueError(f"source {self.slug}: github_repo requires `repo`")
        if self.type == SourceType.IETF_DRAFT and not self.draft_name:
            raise ValueError(f"source {self.slug}: ietf_draft requires `draft_name`")
        return self


def load_sources(yaml_path: Path) -> list[Source]:
    raw = yaml.safe_load(yaml_path.read_text())
    if not isinstance(raw, list):
        raise ValueError(f"{yaml_path} must be a YAML list")
    sources = [Source.model_validate(item) for item in raw]
    seen: set[str] = set()
    for s in sources:
        if s.slug in seen:
            raise ValueError(f"duplicate slug: {s.slug}")
        seen.add(s.slug)
    return sources
