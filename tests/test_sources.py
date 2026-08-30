from pathlib import Path

import pytest
from pydantic import ValidationError

from pipeline.sources import Source, SourceType, load_sources
from pipeline.taxonomy import SourceRole, SourceTier, Track


def test_html_page_source_minimum_fields():
    s = Source(
        slug="gptbot",
        type=SourceType.HTML_PAGE,
        url="https://platform.openai.com/docs/gptbot",
        display_name="OpenAI GPTBot",
        default_tracks=[Track.CRAWLER_CONTROLS],
        tier=SourceTier.PRIMARY,
        role=SourceRole.PLATFORM_DOCS,
        required_for_coverage=True,
    )
    assert s.slug == "gptbot"
    assert s.default_tracks == [Track.CRAWLER_CONTROLS]
    assert s.required_for_coverage is True


def test_rss_feed_accepts_no_keyword_filter():
    # Product-specific changelog feeds don't need a keyword filter — they're
    # already pre-filtered at the publisher. Only `url` is schema-required.
    s = Source(
        slug="cf-ai-crawl-control",
        type=SourceType.RSS_FEED,
        url="https://developers.cloudflare.com/changelog/rss/ai-crawl-control.xml",
        display_name="Cloudflare AI Crawl Control",
        default_tracks=[Track.CRAWLER_CONTROLS],
        tier=SourceTier.PRIMARY,
        role=SourceRole.INFRASTRUCTURE,
    )
    assert s.keyword_filter is None


def test_github_repo_requires_repo_field():
    with pytest.raises(ValidationError):
        Source(
            slug="mcp",
            type=SourceType.GITHUB_REPO,
            display_name="MCP",
            default_tracks=[Track.STANDARDS_PROTOCOLS],
            tier=SourceTier.PRIMARY,
            role=SourceRole.STANDARDS,
        )


def test_ietf_draft_requires_draft_name():
    with pytest.raises(ValidationError):
        Source(
            slug="wba",
            type=SourceType.IETF_DRAFT,
            display_name="Web Bot Auth",
            default_tracks=[Track.STANDARDS_PROTOCOLS],
            tier=SourceTier.PRIMARY,
            role=SourceRole.STANDARDS,
        )


def test_source_rejects_empty_or_duplicate_default_tracks():
    common = {
        "slug": "bad-source",
        "type": SourceType.HTML_PAGE,
        "url": "https://example.test",
        "display_name": "Bad Source",
        "tier": SourceTier.PRIMARY,
        "role": SourceRole.PLATFORM_DOCS,
    }

    with pytest.raises(ValidationError):
        Source(default_tracks=[], **common)

    with pytest.raises(ValidationError):
        Source(
            default_tracks=[Track.CRAWLER_CONTROLS, Track.CRAWLER_CONTROLS],
            **common,
        )


def test_load_sources_from_yaml(tmp_path):
    yaml_text = """
- slug: gptbot
  type: html_page
  url: https://platform.openai.com/docs/gptbot
  display_name: OpenAI GPTBot
  default_tracks: [crawler-controls]
  tier: primary
  role: platform-docs
  required_for_coverage: true
- slug: cloudflare-blog
  type: rss_feed
  url: https://blog.cloudflare.com/rss/
  keyword_filter: ["AI bot", "crawler"]
  display_name: Cloudflare Blog
  default_tracks: [crawler-controls, measurement-economics]
  tier: specialist
  role: reporting
"""
    p = tmp_path / "sources.yaml"
    p.write_text(yaml_text)
    sources = load_sources(p)
    assert len(sources) == 2
    assert sources[0].slug == "gptbot"
    assert sources[0].tier is SourceTier.PRIMARY
    assert sources[1].keyword_filter == ["AI bot", "crawler"]


def test_load_sources_rejects_duplicate_slugs(tmp_path):
    yaml_text = """
- slug: dup
  type: html_page
  url: https://a.example
  display_name: A
  default_tracks: [crawler-controls]
  tier: primary
  role: platform-docs
- slug: dup
  type: html_page
  url: https://b.example
  display_name: B
  default_tracks: [crawler-controls]
  tier: primary
  role: platform-docs
"""
    p = tmp_path / "sources.yaml"
    p.write_text(yaml_text)
    with pytest.raises(ValueError, match="duplicate slug"):
        load_sources(p)


def test_repository_sources_use_track_tier_and_role_schema():
    sources = load_sources(Path("sources.yaml"))

    assert len(sources) >= 30
    assert all(source.default_tracks for source in sources)
    assert all(source.tier for source in sources)
    assert all(source.role for source in sources)
