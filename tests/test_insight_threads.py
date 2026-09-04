from datetime import UTC, datetime

from pipeline.insight_threads import update_insight_threads


def _write_feed_record(
    root,
    *,
    slug: str,
    status: str,
    detected_at: datetime,
    trend_signals: list[str],
    development_slug: str | None = None,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    development = (
        f"development_slug: {development_slug}\n" if development_slug else ""
    )
    signals = "".join(f"  - {signal}\n" for signal in trend_signals) or "  []\n"
    (root / f"{slug}.md").write_text(
        "---\n"
        "schema_version: 1\n"
        f"slug: {slug}\n"
        f"title: Item {slug}\n"
        "source: example\n"
        f"source_tier: {'primary' if status == 'verified' else 'commentary'}\n"
        f"status: {status}\n"
        "primary_track: agentic-web\n"
        "tracks: [agentic-web]\n"
        "actors: []\n"
        f"event_date: {detected_at.isoformat()}\n"
        f"published_at: {detected_at.isoformat()}\n"
        f"detected_at: {detected_at.isoformat()}\n"
        "source_urls: [https://example.test/item]\n"
        "change_kind: material\n"
        "importance: 0.8\n"
        "confidence: high\n"
        "evidence_ids: [example--1]\n"
        "trend_signals:\n"
        f"{signals}"
        f"{development}"
        "backfilled: false\n"
        "---\n\n"
        "## Summary\n\nSummary.\n\n"
        f"## Insight\n\nInsight from {slug}.\n\n"
        "## Implication\n\nImplication.\n\n"
        "## Why it matters\n\nWhy.\n\n"
        "## Evidence\n\n- Evidence.\n"
    )


def test_signal_adds_context_without_verified_evidence(tmp_path):
    feed_dir = tmp_path / "feed"
    path = tmp_path / "insight-threads.json"
    _write_feed_record(
        feed_dir,
        slug="x-signal",
        status="signal",
        detected_at=datetime(2026, 9, 3, 7, tzinfo=UTC),
        trend_signals=["verifiable-agent-identity"],
    )

    registry = update_insight_threads(feed_dir=feed_dir, events_dir=None, path=path)

    thread = registry.threads[0]
    assert thread.key == "verifiable-agent-identity"
    assert thread.title == "Verifiable Agent Identity"
    assert thread.related_feed_slugs == ["x-signal"]
    assert thread.verified_development_slugs == []
    assert thread.confidence == "low"
    assert thread.direction == "emerging"


def test_verified_item_adds_durable_thread_evidence_and_newest_thesis(tmp_path):
    feed_dir = tmp_path / "feed"
    path = tmp_path / "insight-threads.json"
    _write_feed_record(
        feed_dir,
        slug="older-signal",
        status="signal",
        detected_at=datetime(2026, 9, 2, 7, tzinfo=UTC),
        trend_signals=["verifiable-agent-identity"],
    )
    _write_feed_record(
        feed_dir,
        slug="verified-change",
        status="verified",
        detected_at=datetime(2026, 9, 3, 7, tzinfo=UTC),
        trend_signals=["Verifiable Agent Identity"],
        development_slug="signed-agents-enforced",
    )

    registry = update_insight_threads(feed_dir=feed_dir, events_dir=None, path=path)

    thread = registry.threads[0]
    assert thread.related_feed_slugs == ["older-signal", "verified-change"]
    assert thread.verified_development_slugs == ["signed-agents-enforced"]
    assert thread.confidence == "high"
    assert thread.direction == "developing"
    assert thread.thesis == "Insight from verified-change."
    assert thread.last_updated_at == datetime(2026, 9, 3, 7, tzinfo=UTC)


def test_rebuilding_same_feed_is_byte_stable(tmp_path):
    feed_dir = tmp_path / "feed"
    path = tmp_path / "insight-threads.json"
    _write_feed_record(
        feed_dir,
        slug="reported-item",
        status="reported",
        detected_at=datetime(2026, 9, 3, 7, tzinfo=UTC),
        trend_signals=["publisher-compensation"],
    )

    update_insight_threads(feed_dir=feed_dir, events_dir=None, path=path)
    first = path.read_bytes()
    update_insight_threads(feed_dir=feed_dir, events_dir=None, path=path)

    assert path.read_bytes() == first


def test_existing_verified_feed_uses_linked_event_trend_impact(tmp_path):
    feed_dir = tmp_path / "feed"
    events_dir = tmp_path / "events"
    path = tmp_path / "insight-threads.json"
    _write_feed_record(
        feed_dir,
        slug="existing-verified",
        status="verified",
        detected_at=datetime(2026, 9, 1, 7, tzinfo=UTC),
        trend_signals=[],
        development_slug="signed-agents-enforced",
    )
    events_dir.mkdir(parents=True)
    (events_dir / "2026-09-01-event.md").write_text(
        "---\n"
        "schema_version: 2\n"
        "slug: signed-agents-enforced\n"
        "---\n\n"
        "## Development\n\nSigned agents shipped.\n\n"
        "## Trend impact\n\n"
        "- verifiable-agent-identity\n"
        "- accountable-agent-traffic\n\n"
        "## Evidence\n\n- Source.\n"
    )

    registry = update_insight_threads(
        feed_dir=feed_dir,
        events_dir=events_dir,
        path=path,
    )

    assert [thread.key for thread in registry.threads] == [
        "accountable-agent-traffic",
        "verifiable-agent-identity",
    ]
    assert all(thread.confidence == "high" for thread in registry.threads)
