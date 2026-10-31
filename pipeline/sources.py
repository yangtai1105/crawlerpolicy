"""Source configuration schema and loader."""
from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal, Self

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from pipeline.taxonomy import (
    Front,
    SourceRole,
    SourceTier,
    Subject,
    Track,
    resolve_track_list,
)


class SourceType(StrEnum):
    HTML_PAGE = "html_page"
    RSS_FEED = "rss_feed"
    GITHUB_REPO = "github_repo"
    IETF_DRAFT = "ietf_draft"
    GEMINI_SEARCH = "gemini_search"
    GEMINI_LISTING = "gemini_listing"
    XAI_SEARCH = "xai_search"
    CF_BROWSER_RUN = "cf_browser_run"


class Source(BaseModel):
    slug: str
    type: SourceType
    display_name: str
    default_tracks: list[Track]
    default_subject: Subject = Subject.UNKNOWN
    tier: SourceTier
    role: SourceRole
    enabled: bool = True
    required_for_coverage: bool = False

    # html_page + rss_feed
    url: str | None = None
    content_selector: str | None = None

    # Optional: when the tracked URL changed recently (vendor rebrand / URL
    # restructure), this URL is used by bootstrap_baseline for Wayback lookup
    # so we still get a ~6-month historical baseline to diff against.
    baseline_url: str | None = None

    # rss_feed
    keyword_filter: list[str] | None = None
    # Security-vendor blogs mention "AI" and "bot" in nearly every body, so a
    # broad feed can match on the title alone and leave the rest to the
    # model relevance check.
    keyword_filter_scope: Literal["content", "title"] = "content"

    # rss_feed + gemini_listing: read each item through Google Search grounding
    # before analysis, for sites that block crawlers but let search engines
    # index them. gemini_listing sources always read this way.
    enrich_via: Literal["gemini_grounded"] | None = None
    # Ask the Wayback Machine to snapshot each material item's article URL.
    archive_primary: bool = False

    # github_repo
    repo: str | None = None
    pr_labels: list[str] = Field(default_factory=list)
    pr_path_globs: list[str] = Field(default_factory=list)

    # ietf_draft
    draft_name: str | None = None

    # gemini_search + gemini_listing
    query: str | None = None
    lookback_days: int | None = None

    # gemini_listing: the only host whose cited articles become items
    listing_domain: str | None = None

    # xai_search
    # x_handles is a hard allowlist passed to the search tool; the priority
    # handles are only named in the prompt, so other primary posters still count.
    x_handles: list[str] = Field(default_factory=list, max_length=20)
    x_priority_handles: list[str] = Field(default_factory=list, max_length=40)
    # One call covering several fronts; each candidate is tagged with one.
    x_fronts: dict[Front, str] = Field(default_factory=dict)
    lookback_hours: int = Field(default=36, ge=1, le=72)
    shadow: bool = True

    # Optional analysis-model override per source.
    model: str | None = None

    @property
    def reads_grounded(self) -> bool:
        return self.type is SourceType.GEMINI_LISTING or self.enrich_via == "gemini_grounded"

    def keyword_haystack(self, title: str, content: str) -> str:
        """Return the text the keyword filter matches against."""
        if self.keyword_filter_scope == "title":
            return title
        return f"{title}\n{content}"

    @field_validator("default_tracks", mode="before")
    @classmethod
    def _resolve_track_aliases(cls, value: object) -> object:
        return resolve_track_list(value)

    @model_validator(mode="after")
    def _validate_type_requirements(self) -> Self:
        if not self.default_tracks:
            raise ValueError(f"source {self.slug}: `default_tracks` must not be empty")
        if len(self.default_tracks) != len(set(self.default_tracks)):
            raise ValueError(f"source {self.slug}: `default_tracks` must not contain duplicates")
        url_source_types = {
            SourceType.HTML_PAGE,
            SourceType.RSS_FEED,
            SourceType.CF_BROWSER_RUN,
        }
        if self.type in url_source_types and not self.url:
            raise ValueError(f"source {self.slug}: {self.type} requires `url`")
        # keyword_filter is optional for rss_feed: product-specific changelog
        # feeds (e.g. Cloudflare ai-crawl-control.xml) are pre-filtered at the
        # publisher and don't need another pass. Broad blog feeds should still
        # supply one — but that's a YAML-side convention, not a schema rule.
        if self.type == SourceType.GITHUB_REPO and not self.repo:
            raise ValueError(f"source {self.slug}: github_repo requires `repo`")
        if self.type == SourceType.IETF_DRAFT and not self.draft_name:
            raise ValueError(f"source {self.slug}: ietf_draft requires `draft_name`")
        if self.type == SourceType.GEMINI_SEARCH and not self.query:
            raise ValueError(f"source {self.slug}: gemini_search requires `query`")
        if self.type == SourceType.GEMINI_LISTING and not (self.query and self.listing_domain):
            raise ValueError(
                f"source {self.slug}: gemini_listing requires `query` and `listing_domain`"
            )
        if self.enrich_via and self.type not in {SourceType.RSS_FEED, SourceType.GEMINI_LISTING}:
            raise ValueError(
                f"source {self.slug}: `enrich_via` applies to rss_feed and gemini_listing only"
            )
        if self.type == SourceType.XAI_SEARCH:
            if not self.query:
                raise ValueError(f"source {self.slug}: xai_search requires `query`")
            if self.tier is not SourceTier.COMMENTARY:
                raise ValueError(f"source {self.slug}: xai_search must use commentary tier")
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
