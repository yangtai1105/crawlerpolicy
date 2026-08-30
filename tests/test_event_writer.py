from datetime import datetime, timezone
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
        implication="",
    )
    detected_at = datetime(2026, 4, 18, 8, 0, 0, tzinfo=timezone.utc)

    path = write_event(
        events_dir=tmp_path,
        source=source,
        analysis=analysis,
        detected_at=detected_at,
        unified_diff="-old\n+new",
    )

    assert path.exists()
    text = path.read_text()
    assert text.startswith("---\n")
    assert "slug: openai-adds-operator-ua" in text
    assert "source: gptbot" in text
    assert "pillar: crawler" in text
    assert "change_kind: material" in text
    assert "importance: 0.82" in text
    assert "## What changed\n\nNew UA string." in text
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
    )
    detected_at = datetime(2026, 4, 18, 12, 0, 0, tzinfo=timezone.utc)

    path = write_event(
        events_dir=tmp_path,
        source=source,
        analysis=analysis,
        detected_at=detected_at,
        unified_diff="",
    )

    assert path.name == "2026-04-18-cloudflare-blog-cloudflare-ships-ai-audit.md"
