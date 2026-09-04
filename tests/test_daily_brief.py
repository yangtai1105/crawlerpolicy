from datetime import UTC, date, datetime

from pipeline.daily_brief import build_daily_brief, save_daily_brief


def _write_feed_item(
    root,
    *,
    slug: str,
    importance: float,
    detected_at: datetime,
    published_at: datetime | None = None,
    backfilled: bool = False,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    published = published_at or detected_at
    (root / f"{slug}.md").write_text(
        "---\n"
        "schema_version: 1\n"
        f"slug: {slug}\n"
        f"title: Item {slug}\n"
        "source: example\n"
        "source_tier: primary\n"
        "status: verified\n"
        "primary_track: crawler-controls\n"
        "tracks: [crawler-controls]\n"
        "actors: []\n"
        f"event_date: {published.isoformat()}\n"
        f"published_at: {published.isoformat()}\n"
        f"detected_at: {detected_at.isoformat()}\n"
        "source_urls: [https://example.test/item]\n"
        "change_kind: material\n"
        f"importance: {importance}\n"
        "confidence: high\n"
        "evidence_ids: [example--1]\n"
        f"backfilled: {str(backfilled).lower()}\n"
        "---\n\n"
        "## Summary\n\nSummary.\n\n"
        "## Insight\n\nInsight.\n\n"
        "## Implication\n\nImplication.\n\n"
        "## Why it matters\n\nWhy.\n\n"
        "## Evidence\n\n- Evidence.\n"
    )


def test_daily_brief_uses_detection_date_and_caps_at_five(tmp_path):
    feed_dir = tmp_path / "feed"
    detected = datetime(2026, 9, 3, 8, tzinfo=UTC)
    for index, importance in enumerate([0.65, 0.95, 0.70, 0.90, 0.75, 0.85, 0.80]):
        _write_feed_item(
            feed_dir,
            slug=f"item-{index}",
            importance=importance,
            detected_at=detected,
        )
    _write_feed_item(
        feed_dir,
        slug="yesterday",
        importance=1.0,
        detected_at=datetime(2026, 9, 2, 8, tzinfo=UTC),
    )
    _write_feed_item(
        feed_dir,
        slug="backfilled",
        importance=1.0,
        detected_at=detected,
        published_at=datetime(2026, 7, 1, 8, tzinfo=UTC),
        backfilled=True,
    )

    brief = build_daily_brief(
        feed_dir=feed_dir,
        edition_date=date(2026, 9, 3),
        generated_at=detected,
    )

    assert brief.status == "published"
    assert len(brief.items) == 5
    assert [item.importance for item in brief.items] == [0.95, 0.90, 0.85, 0.80, 0.75]
    assert all(item.slug not in {"yesterday", "backfilled"} for item in brief.items)


def test_daily_brief_writes_truthful_quiet_edition(tmp_path):
    generated_at = datetime(2026, 9, 3, 8, tzinfo=UTC)

    brief = build_daily_brief(
        feed_dir=tmp_path / "feed",
        edition_date=date(2026, 9, 3),
        generated_at=generated_at,
    )

    assert brief.status == "quiet"
    assert brief.items == []
    assert brief.note == (
        "No material ecosystem developments were published in this daily window."
    )

    path = tmp_path / "daily" / "2026-09-03.json"
    save_daily_brief(path, brief)
    first = path.read_bytes()
    save_daily_brief(path, brief)
    assert path.read_bytes() == first
