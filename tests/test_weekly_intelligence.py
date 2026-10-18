import json
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.taxonomy import SourceTier, Track
from pipeline.trends import Trend, TrendDelta, TrendStatus
from pipeline.weekly_intelligence import (
    MaterialEvent,
    WeeklyIssue,
    WeeklySynthesis,
    _load_previous_issue,
    build_weekly_issue,
    completed_iso_window,
    generate_weekly_intelligence,
    load_material_events,
    load_reported_developments,
    validate_issue_evidence,
)

NOW = datetime(2026, 8, 31, 13, tzinfo=UTC)


def _event() -> MaterialEvent:
    return MaterialEvent(
        event_id="google-ai-control",
        title="Google adds AI Search publisher control",
        source="google-search-central",
        source_tier=SourceTier.PRIMARY,
        primary_track=Track.SEARCH_DISCOVERY,
        tracks=[Track.SEARCH_DISCOVERY, Track.ACCESS_CONTROLS],
        event_date=datetime(2026, 8, 27, tzinfo=UTC),
        published_at=datetime(2026, 8, 27, tzinfo=UTC),
        detected_at=datetime(2026, 8, 27, 8, tzinfo=UTC),
        source_url="https://developers.google.com/search/blog/example",
        importance=0.86,
        confidence="high",
        actors=["Google", "publishers"],
        trend_signals=["training-search-separation"],
        evidence_ids=["google-search-central--abc123"],
        development="Google documented a separate control.",
        implication="Search and training controls are diverging.",
    )


def _health():
    return {
        "status": "healthy",
        "last_attempted_at": "2026-08-30T08:00:00+00:00",
        "last_fully_successful_at": "2026-08-30T08:00:00+00:00",
        "coverage": {
            "configured": 10,
            "completed": 10,
            "fetched": 10,
            "analyzed": 10,
            "published": 10,
            "failed": 0,
            "required_failed": 0,
        },
    }


def test_weekly_issue_compares_against_previous_status():
    trend = Trend(
        key="training-search-separation",
        title="Training and search controls separate",
        status=TrendStatus.ACCELERATING,
        evidence_event_ids=["google-ai-control"],
    )
    previous = WeeklyIssue(
        week="2026-W34",
        generated_at=datetime(2026, 8, 24, tzinfo=UTC),
        window_start=date(2026, 8, 17),
        window_end=date(2026, 8, 23),
        trend_deltas=[
            TrendDelta(
                trend_key=trend.key,
                previous_status=TrendStatus.EMERGING,
                current_status=TrendStatus.EMERGING,
                accepted=True,
                reason="previous issue",
            )
        ],
    )

    issue = build_weekly_issue(
        events=[_event()],
        trends=[trend],
        previous_issue=previous,
        health=_health(),
        week="2026-W35",
        generated_at=NOW,
        window_start=date(2026, 8, 24),
        window_end=date(2026, 8, 30),
    )

    assert issue.trend_deltas[0].previous_status is TrendStatus.EMERGING
    assert issue.trend_deltas[0].current_status is TrendStatus.ACCELERATING


def test_quiet_tracks_are_explicit():
    issue = build_weekly_issue(
        events=[_event()],
        trends=[],
        previous_issue=None,
        health=_health(),
        week="2026-W35",
        generated_at=NOW,
        window_start=date(2026, 8, 24),
        window_end=date(2026, 8, 30),
    )

    quiet = next(
        group
        for group in issue.material_developments
        if group.track is Track.ASSET_RIGHTS
    )
    assert quiet.material_change is False
    assert quiet.event_ids == []
    assert "No verified material change" in quiet.summary


def test_weekly_issue_rejects_invented_evidence_ids():
    issue = build_weekly_issue(
        events=[_event()],
        trends=[],
        previous_issue=None,
        health=_health(),
        week="2026-W35",
        generated_at=NOW,
        window_start=date(2026, 8, 24),
        window_end=date(2026, 8, 30),
    )
    issue.executive_shifts[0].evidence_event_ids = ["invented-event"]

    with pytest.raises(ValueError, match="invented-event"):
        validate_issue_evidence(issue, {"google-ai-control"})


def _write_schema_v2_event(path: Path, *, event_date: str, schema_version: int = 2):
    path.write_text(
        f"""---
schema_version: {schema_version}
slug: google-ai-control
title: "Google adds AI Search publisher control"
source: google-search-central
source_tier: primary
primary_track: search-discovery
tracks:
  - search-discovery
  - access-controls
actors:
  - Google
event_date: {event_date}
published_at: {event_date}
detected_at: 2026-08-28T08:00:00+00:00
source_url: "https://developers.google.com/search/blog/example"
change_kind: material
importance: 0.86
confidence: high
evidence_ids:
  - google-search-central--abc123
---

## Development

Google documented a separate control.

## Why it matters

Search and training controls are diverging.

## Trend impact

- training-search-separation
"""
    )


def test_completed_iso_window_selects_previous_completed_week():
    week, start, end = completed_iso_window(NOW)

    assert week == "2026-W35"
    assert start == date(2026, 8, 24)
    assert end == date(2026, 8, 30)


def test_event_loader_uses_event_date_and_ignores_legacy(tmp_path):
    _write_schema_v2_event(
        tmp_path / "current.md",
        event_date="2026-08-27T00:00:00+00:00",
    )
    _write_schema_v2_event(
        tmp_path / "legacy.md",
        event_date="2026-08-28T00:00:00+00:00",
        schema_version=1,
    )
    _write_schema_v2_event(
        tmp_path / "outside.md",
        event_date="2026-08-23T00:00:00+00:00",
    )

    events = load_material_events(
        tmp_path,
        window_start=date(2026, 8, 24),
        window_end=date(2026, 8, 30),
    )

    assert len(events) == 1
    assert events[0].event_id == "google-ai-control"
    assert events[0].trend_signals == ["training-search-separation"]


def test_event_loader_resolves_pre_october_2026_track_aliases(tmp_path):
    (tmp_path / "legacy-slugs.md").write_text(
        """---
schema_version: 2
slug: google-ai-control
title: "Google adds AI Search publisher control"
source: google-search-central
source_tier: primary
primary_track: crawler-controls
tracks:
  - crawler-controls
  - agentic-web
actors:
  - Google
event_date: 2026-08-27T00:00:00+00:00
published_at: 2026-08-27T00:00:00+00:00
detected_at: 2026-08-28T08:00:00+00:00
source_url: "https://developers.google.com/search/blog/example"
change_kind: material
importance: 0.86
confidence: high
evidence_ids:
  - google-search-central--abc123
---

## Development

Google documented a separate control.

## Why it matters

Search and training controls are diverging.

## Trend impact

- training-search-separation
"""
    )

    events = load_material_events(
        tmp_path,
        window_start=date(2026, 8, 24),
        window_end=date(2026, 8, 30),
    )

    assert len(events) == 1
    assert events[0].primary_track is Track.ACCESS_CONTROLS
    assert events[0].tracks == [Track.ACCESS_CONTROLS, Track.PLATFORM_ECOSYSTEM]


def test_load_previous_issue_resolves_legacy_track_slugs(tmp_path):
    (tmp_path / "2026-W34.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "week": "2026-W34",
                "generated_at": "2026-08-24T08:00:00+00:00",
                "window_start": "2026-08-17",
                "window_end": "2026-08-23",
                "material_developments": [
                    {
                        "track": "crawler-controls",
                        "material_change": True,
                        "event_ids": ["google-ai-control"],
                        "summary": "Publisher controls diverged.",
                    }
                ],
                "watchlist": [
                    {
                        "question": (
                            "What primary evidence would make agentic-web materially change?"
                        ),
                        "tracks": ["agentic-web"],
                    }
                ],
            }
        )
    )

    previous = _load_previous_issue(tmp_path, "2026-W35")

    assert previous is not None
    assert previous.material_developments[0].track is Track.ACCESS_CONTROLS
    assert previous.watchlist[0].tracks == [Track.PLATFORM_ECOSYSTEM]


async def test_generate_weekly_intelligence_writes_verified_issue(tmp_path):
    events_dir = tmp_path / "content" / "events"
    events_dir.mkdir(parents=True)
    _write_schema_v2_event(
        events_dir / "current.md",
        event_date="2026-08-27T00:00:00+00:00",
    )
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "health.json").write_text(json.dumps(_health()))
    (data_dir / "trends.json").write_text('{"schema_version": 1, "trends": []}')

    issue = await generate_weekly_intelligence(
        repo_root=tmp_path,
        now=NOW,
        model=None,
    )

    output = data_dir / "intelligence" / "2026-W35.json"
    assert output.exists()
    assert issue.week == "2026-W35"
    assert WeeklyIssue.model_validate_json(output.read_text()) == issue


async def test_generate_weekly_intelligence_refuses_critical_health(tmp_path):
    (tmp_path / "content" / "events").mkdir(parents=True)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    health = _health()
    health["status"] = "critical"
    (data_dir / "health.json").write_text(json.dumps(health))
    (data_dir / "trends.json").write_text('{"schema_version": 1, "trends": []}')

    with pytest.raises(RuntimeError, match="critical"):
        await generate_weekly_intelligence(repo_root=tmp_path, now=NOW, model=None)

    assert not (data_dir / "intelligence" / "2026-W35.json").exists()


async def test_generate_weekly_intelligence_refuses_stale_health(tmp_path):
    (tmp_path / "content" / "events").mkdir(parents=True)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    health = _health()
    health["last_attempted_at"] = "2026-08-29T08:00:00+00:00"
    (data_dir / "health.json").write_text(json.dumps(health))
    (data_dir / "trends.json").write_text('{"schema_version": 1, "trends": []}')

    with pytest.raises(RuntimeError, match="completed weekly window"):
        await generate_weekly_intelligence(repo_root=tmp_path, now=NOW, model=None)


async def test_weekly_synthesis_uses_structured_model_and_preserves_evidence(tmp_path):
    events_dir = tmp_path / "content" / "events"
    events_dir.mkdir(parents=True)
    _write_schema_v2_event(
        events_dir / "current.md",
        event_date="2026-08-27T00:00:00+00:00",
    )
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "health.json").write_text(json.dumps(_health()))
    (data_dir / "trends.json").write_text('{"schema_version": 1, "trends": []}')
    model = MagicMock()
    model.generate = AsyncMock(
        return_value=WeeklySynthesis(
            thesis="Access controls are becoming more specific.",
            intelligence_read="One verified development separated search and training controls.",
            executive_shifts=[
                {
                    "headline": "Google separates an AI Search control",
                    "summary": "Publishers gained a more specific control.",
                    "evidence_event_ids": ["google-ai-control"],
                }
            ],
        )
    )

    issue = await generate_weekly_intelligence(
        repo_root=tmp_path,
        now=NOW,
        model=model,
    )

    assert issue.model_generated is True
    assert issue.executive_shifts[0].evidence_event_ids == ["google-ai-control"]
    assert issue.thesis == "Access controls are becoming more specific."


def _write_feed_item(
    path: Path,
    *,
    event_date: str,
    status: str = "reported",
    change_kind: str = "material",
    importance: float = 0.8,
):
    path.write_text(
        f"""---
schema_version: 1
slug: {path.stem}
title: "Cloudflare scores verified bots on behavior"
source: cloudflare-blog
source_tier: specialist
status: {status}
primary_track: crawler-controls
tracks:
  - crawler-controls
change_kind: {change_kind}
importance: {importance}
event_date: {event_date}
---

## Summary

Cloudflare now scores [Verified bots](https://blog.cloudflare.com/x) on behavior.

## Insight

Identity is no longer a one-time check.
"""
    )


def test_reported_loader_keeps_only_material_specialist_items_in_window(tmp_path):
    _write_feed_item(tmp_path / "kept.md", event_date="2026-08-27T00:00:00+00:00")
    _write_feed_item(
        tmp_path / "verified.md",
        event_date="2026-08-27T00:00:00+00:00",
        status="verified",
    )
    _write_feed_item(
        tmp_path / "signal.md",
        event_date="2026-08-27T00:00:00+00:00",
        status="signal",
    )
    _write_feed_item(
        tmp_path / "noise.md",
        event_date="2026-08-27T00:00:00+00:00",
        change_kind="noise",
    )
    _write_feed_item(tmp_path / "outside.md", event_date="2026-08-23T00:00:00+00:00")

    reported = load_reported_developments(
        tmp_path,
        window_start=date(2026, 8, 24),
        window_end=date(2026, 8, 30),
    )

    assert [item.slug for item in reported] == ["kept"]
    assert reported[0].primary_track is Track.ACCESS_CONTROLS
    assert reported[0].summary == "Cloudflare now scores Verified bots on behavior."


async def test_reported_items_are_listed_but_never_move_the_verified_ledger(tmp_path):
    feed_dir = tmp_path / "content" / "feed"
    feed_dir.mkdir(parents=True)
    _write_feed_item(feed_dir / "low.md", event_date="2026-08-26T00:00:00+00:00", importance=0.5)
    _write_feed_item(feed_dir / "high.md", event_date="2026-08-27T00:00:00+00:00", importance=0.9)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "health.json").write_text(json.dumps(_health()))
    (data_dir / "trends.json").write_text('{"schema_version": 1, "trends": []}')
    synthesizer = AsyncMock()

    issue = await generate_weekly_intelligence(
        repo_root=tmp_path,
        now=NOW,
        model=synthesizer,
    )

    assert [item.slug for item in issue.reported_developments] == ["high", "low"]
    assert issue.thesis == "No verified material developments in the completed window."
    assert issue.executive_shifts == []
    assert issue.source_ledger == []
    assert not any(item.material_change for item in issue.material_developments)
    assert "2 reported developments from specialist sources" in issue.intelligence_read
    synthesizer.generate.assert_not_awaited()


def test_issues_written_before_reported_developments_still_load():
    legacy = {
        "week": "2026-W30",
        "generated_at": "2026-07-27T13:00:00Z",
        "window_start": "2026-07-20",
        "window_end": "2026-07-26",
    }

    assert WeeklyIssue.model_validate(legacy).reported_developments == []
