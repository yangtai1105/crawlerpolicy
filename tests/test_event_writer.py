from datetime import UTC, datetime
from pathlib import Path

from pipeline.analyzer import AnalysisResult
from pipeline.event_writer import write_event
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Track


def test_write_event_creates_file_with_frontmatter(tmp_path: Path):
    source = Source(
        slug="gptbot",
        type=SourceType.HTML_PAGE,
        url="https://x",
        display_name="OpenAI GPTBot",
        default_tracks=[Track.CRAWLER_CONTROLS],
        tier=SourceTier.PRIMARY,
        role=SourceRole.PLATFORM_DOCS,
    )
    analysis = AnalysisResult(
        change_kind="material",
        importance=0.82,
        title="OpenAI adds Operator UA",
        what_changed="New UA string.",
        implication="Search and training controls now differ.",
        primary_track=Track.SEARCH_DISCOVERY,
        tracks=[Track.SEARCH_DISCOVERY, Track.CRAWLER_CONTROLS],
        actors=["OpenAI", "publishers"],
        trend_signals=["training-search-separation"],
        confidence="high",
    )
    event_date = datetime(2026, 4, 17, 0, 0, 0, tzinfo=UTC)
    published_at = datetime(2026, 4, 17, 6, 0, 0, tzinfo=UTC)
    detected_at = datetime(2026, 4, 18, 8, 0, 0, tzinfo=UTC)

    path = write_event(
        events_dir=tmp_path,
        source=source,
        analysis=analysis,
        event_date=event_date,
        published_at=published_at,
        detected_at=detected_at,
        evidence_ids=["gptbot--abc123"],
        unified_diff="-old\n+new",
    )

    assert path.exists()
    text = path.read_text()
    assert text.startswith("---\n")
    assert "slug: openai-adds-operator-ua" in text
    assert "schema_version: 2" in text
    assert "source: gptbot" in text
    assert "source_tier: primary" in text
    assert "primary_track: search-discovery" in text
    assert "tracks:\n  - search-discovery\n  - crawler-controls" in text
    assert "event_date: 2026-04-17T00:00:00+00:00" in text
    assert "published_at: 2026-04-17T06:00:00+00:00" in text
    assert "detected_at: 2026-04-18T08:00:00+00:00" in text
    assert "change_kind: material" in text
    assert "importance: 0.82" in text
    assert "confidence: high" in text
    assert "## Development\n\nNew UA string." in text
    assert "## Why it matters\n\nSearch and training controls now differ." in text
    assert "## Trend impact" in text
    assert "training-search-separation" in text
    assert "## Evidence" in text
    assert "gptbot--abc123" in text
    assert "```diff\n-old\n+new" in text


def test_write_event_filename_convention(tmp_path: Path):
    source = Source(
        slug="cloudflare-blog",
        type=SourceType.RSS_FEED,
        url="https://x/rss",
        keyword_filter=["AI"],
        display_name="Cloudflare",
        default_tracks=[Track.MEASUREMENT_ECONOMICS],
        tier=SourceTier.SPECIALIST,
        role=SourceRole.REPORTING,
    )
    analysis = AnalysisResult(
        change_kind="material",
        importance=0.6,
        title="Cloudflare ships AI Audit",
        what_changed="Details.",
        implication="Implications here.",
        primary_track=Track.MEASUREMENT_ECONOMICS,
        tracks=[Track.MEASUREMENT_ECONOMICS],
        actors=["Cloudflare"],
        trend_signals=[],
        confidence="medium",
    )
    detected_at = datetime(2026, 4, 18, 12, 0, 0, tzinfo=UTC)

    path = write_event(
        events_dir=tmp_path,
        source=source,
        analysis=analysis,
        event_date=detected_at,
        published_at=detected_at,
        detected_at=detected_at,
        evidence_ids=["cloudflare-blog--abc123"],
        unified_diff="",
    )

    assert path.name == "2026-04-18-cloudflare-blog-cloudflare-ships-ai-audit.md"
