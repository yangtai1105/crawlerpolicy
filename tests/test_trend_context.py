from pipeline.trend_context import format_trend_context, load_recent_events_for_source


def _write_event(path, *, schema_version, event_date, detected_at, title):
    path.write_text(
        f"""---
schema_version: {schema_version}
slug: example
title: "{title}"
source: source-a
primary_track: search-discovery
tracks:
  - search-discovery
event_date: {event_date}
detected_at: {detected_at}
importance: 0.80
---

## Why it matters

Implication for publishers.
"""
    )


def test_recent_events_ignore_schema_v1_and_order_by_event_date(tmp_path):
    _write_event(
        tmp_path / "legacy.md",
        schema_version=1,
        event_date="2025-01-01T00:00:00+00:00",
        detected_at="2026-08-29T12:00:00+00:00",
        title="Legacy event detected recently",
    )
    _write_event(
        tmp_path / "newer.md",
        schema_version=2,
        event_date="2026-08-28T00:00:00+00:00",
        detected_at="2026-08-29T09:00:00+00:00",
        title="Newer current event",
    )
    _write_event(
        tmp_path / "older.md",
        schema_version=2,
        event_date="2026-08-27T00:00:00+00:00",
        detected_at="2026-08-29T10:00:00+00:00",
        title="Older current event",
    )

    events = load_recent_events_for_source(tmp_path, "source-a")

    assert [event["title"] for event in events] == [
        "Newer current event",
        "Older current event",
    ]
    assert format_trend_context(events).startswith("RECENT ITEMS")
    assert "2026-08-28" in format_trend_context(events)
