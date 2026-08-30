"""Generate evidence-constrained weekly Web intelligence issues."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Literal

import yaml
from anthropic import AsyncAnthropic
from pydantic import BaseModel, Field

from pipeline.config import Config
from pipeline.taxonomy import SourceTier, Track
from pipeline.trends import Trend, TrendDelta, TrendStatus, load_trends, save_trends


class MaterialEvent(BaseModel):
    event_id: str
    title: str
    source: str
    source_tier: SourceTier
    primary_track: Track
    tracks: list[Track]
    event_date: datetime
    published_at: datetime
    detected_at: datetime
    source_url: str
    importance: float
    confidence: Literal["low", "medium", "high"]
    actors: list[str] = Field(default_factory=list)
    trend_signals: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    development: str = ""
    implication: str = ""


class ExecutiveShift(BaseModel):
    headline: str
    summary: str
    evidence_event_ids: list[str] = Field(default_factory=list)


class TrackDevelopment(BaseModel):
    track: Track
    material_change: bool
    event_ids: list[str] = Field(default_factory=list)
    summary: str


class ActorMove(BaseModel):
    actor: str
    direction: str
    evidence_event_ids: list[str] = Field(default_factory=list)


class WatchItem(BaseModel):
    question: str
    tracks: list[Track] = Field(default_factory=list)


class SourceLedgerEntry(BaseModel):
    source: str
    tier: SourceTier
    event_ids: list[str]
    latest_event_date: datetime


class CoverageSnapshot(BaseModel):
    configured: int = 0
    completed: int = 0
    fetched: int = 0
    analyzed: int = 0
    published: int = 0
    failed: int = 0
    required_failed: int = 0


class WeeklyIssue(BaseModel):
    schema_version: int = 1
    week: str
    generated_at: datetime
    window_start: date
    window_end: date
    health_status: str = "unknown"
    coverage: CoverageSnapshot = Field(default_factory=CoverageSnapshot)
    thesis: str = ""
    executive_shifts: list[ExecutiveShift] = Field(default_factory=list)
    material_developments: list[TrackDevelopment] = Field(default_factory=list)
    intelligence_read: str = ""
    trend_deltas: list[TrendDelta] = Field(default_factory=list)
    actor_moves: list[ActorMove] = Field(default_factory=list)
    watchlist: list[WatchItem] = Field(default_factory=list)
    source_ledger: list[SourceLedgerEntry] = Field(default_factory=list)
    model_generated: bool = False


def build_weekly_issue(
    *,
    events: list[MaterialEvent],
    trends: list[Trend],
    previous_issue: WeeklyIssue | None,
    health: dict,
    week: str,
    generated_at: datetime,
    window_start: date,
    window_end: date,
) -> WeeklyIssue:
    """Build the complete deterministic issue before optional prose synthesis."""
    ordered_events = sorted(
        events,
        key=lambda event: (event.importance, event.event_date),
        reverse=True,
    )
    allowed_event_ids = {event.event_id for event in ordered_events}
    previous_statuses = _previous_statuses(previous_issue)

    material_developments = []
    for track in Track:
        track_events = [event for event in ordered_events if track in event.tracks]
        material_developments.append(
            TrackDevelopment(
                track=track,
                material_change=bool(track_events),
                event_ids=[event.event_id for event in track_events],
                summary=(
                    f"{len(track_events)} verified material development"
                    f"{'s' if len(track_events) != 1 else ''}."
                    if track_events
                    else "No verified material change in this track."
                ),
            )
        )

    executive_shifts = [
        ExecutiveShift(
            headline=event.title,
            summary=event.implication or event.development,
            evidence_event_ids=[event.event_id],
        )
        for event in ordered_events[:5]
    ]
    trend_deltas = [
        TrendDelta(
            trend_key=trend.key,
            previous_status=previous_statuses.get(
                trend.key,
                trend.previous_status or trend.status,
            ),
            current_status=trend.status,
            accepted=True,
            reason="current verified trend registry",
            evidence_event_ids=[
                event_id
                for event_id in trend.evidence_event_ids
                if event_id in allowed_event_ids
            ],
            explanation=trend.delta_explanation,
        )
        for trend in trends
    ]
    actor_moves = _actor_moves(ordered_events)
    quiet_tracks = [
        development.track
        for development in material_developments
        if not development.material_change
    ]
    watchlist = [
        WatchItem(
            question=f"What primary evidence would make {track.value} materially change?",
            tracks=[track],
        )
        for track in quiet_tracks
    ]

    issue = WeeklyIssue(
        week=week,
        generated_at=generated_at,
        window_start=window_start,
        window_end=window_end,
        health_status=str(health.get("status", "unknown")),
        coverage=CoverageSnapshot.model_validate(health.get("coverage", {})),
        thesis=(
            executive_shifts[0].summary
            if executive_shifts
            else "No verified material developments in the completed window."
        ),
        executive_shifts=executive_shifts,
        material_developments=material_developments,
        intelligence_read=(
            f"{len(ordered_events)} material developments across "
            f"{sum(item.material_change for item in material_developments)} tracks."
        ),
        trend_deltas=trend_deltas,
        actor_moves=actor_moves,
        watchlist=watchlist,
        source_ledger=_source_ledger(ordered_events),
    )
    validate_issue_evidence(issue, allowed_event_ids)
    return issue


def validate_issue_evidence(issue: WeeklyIssue, allowed_event_ids: set[str]) -> None:
    referenced: set[str] = set()
    for shift in issue.executive_shifts:
        referenced.update(shift.evidence_event_ids)
    for development in issue.material_developments:
        referenced.update(development.event_ids)
    for delta in issue.trend_deltas:
        referenced.update(delta.evidence_event_ids)
    for move in issue.actor_moves:
        referenced.update(move.evidence_event_ids)
    for source in issue.source_ledger:
        referenced.update(source.event_ids)
    invented = referenced - allowed_event_ids
    if invented:
        raise ValueError(
            f"weekly issue references unknown event IDs: {', '.join(sorted(invented))}"
        )


def _previous_statuses(previous_issue: WeeklyIssue | None) -> dict[str, TrendStatus]:
    if previous_issue is None:
        return {}
    return {
        delta.trend_key: delta.current_status
        for delta in previous_issue.trend_deltas
    }


def _actor_moves(events: list[MaterialEvent]) -> list[ActorMove]:
    grouped: dict[str, list[MaterialEvent]] = {}
    for event in events:
        for actor in event.actors:
            grouped.setdefault(actor, []).append(event)
    return [
        ActorMove(
            actor=actor,
            direction=actor_events[0].implication or actor_events[0].development,
            evidence_event_ids=[event.event_id for event in actor_events],
        )
        for actor, actor_events in grouped.items()
    ]


def _source_ledger(events: list[MaterialEvent]) -> list[SourceLedgerEntry]:
    grouped: dict[str, list[MaterialEvent]] = {}
    for event in events:
        grouped.setdefault(event.source, []).append(event)
    return [
        SourceLedgerEntry(
            source=source,
            tier=source_events[0].source_tier,
            event_ids=[event.event_id for event in source_events],
            latest_event_date=max(event.event_date for event in source_events),
        )
        for source, source_events in grouped.items()
    ]


def completed_iso_window(now: datetime) -> tuple[str, date, date]:
    """Return the ISO week immediately preceding the current ISO week."""
    current_monday = now.date() - timedelta(days=now.weekday())
    window_end = current_monday - timedelta(days=1)
    window_start = window_end - timedelta(days=6)
    iso = window_end.isocalendar()
    return f"{iso.year}-W{iso.week:02d}", window_start, window_end


def load_material_events(
    events_dir: Path,
    *,
    window_start: date,
    window_end: date,
) -> list[MaterialEvent]:
    if not events_dir.exists():
        return []
    events: list[MaterialEvent] = []
    for path in events_dir.glob("*.md"):
        parsed = _parse_event(path)
        if parsed is None:
            continue
        event_date = parsed.event_date.date()
        if window_start <= event_date <= window_end:
            events.append(parsed)
    return sorted(events, key=lambda event: event.event_date, reverse=True)


def _parse_event(path: Path) -> MaterialEvent | None:
    text = path.read_text()
    if not text.startswith("---\n"):
        return None
    try:
        frontmatter_text, body = text[4:].split("\n---\n", 1)
        frontmatter = yaml.safe_load(frontmatter_text)
    except (ValueError, yaml.YAMLError):
        return None
    if not isinstance(frontmatter, dict):
        return None
    if frontmatter.get("schema_version") != 2:
        return None
    if frontmatter.get("change_kind") != "material":
        return None
    frontmatter["event_id"] = frontmatter.pop("slug")
    frontmatter["development"] = _section(body, "Development")
    frontmatter["implication"] = _section(body, "Why it matters")
    trend_section = _section(body, "Trend impact")
    frontmatter["trend_signals"] = [
        line.removeprefix("- ").strip()
        for line in trend_section.splitlines()
        if line.startswith("- ")
    ]
    try:
        return MaterialEvent.model_validate(frontmatter)
    except (TypeError, ValueError):
        return None


def _section(body: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n+(.*?)(?=^## |\Z)",
        body,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


async def generate_weekly_intelligence(
    *,
    repo_root: Path,
    now: datetime,
    client: AsyncAnthropic | None,
) -> WeeklyIssue:
    cfg = Config(repo_root=repo_root, anthropic_api_key="", alert_emails=[])
    week, window_start, window_end = completed_iso_window(now)
    health_path = cfg.data_dir / "health.json"
    if not health_path.exists():
        raise RuntimeError("weekly intelligence requires data/health.json")
    health = json.loads(health_path.read_text())
    if health.get("status") == "critical":
        raise RuntimeError("weekly intelligence cannot publish with critical health")
    last_attempted = health.get("last_attempted_at")
    try:
        last_attempted_date = datetime.fromisoformat(last_attempted).date()
    except (TypeError, ValueError):
        last_attempted_date = None
    if last_attempted_date is None or last_attempted_date < window_end:
        raise RuntimeError(
            "weekly intelligence requires health from the completed weekly window"
        )

    events = load_material_events(
        cfg.events_dir,
        window_start=window_start,
        window_end=window_end,
    )
    trends = load_trends(cfg.trends_file)
    previous_issue = _load_previous_issue(cfg.intelligence_dir, week)
    issue = build_weekly_issue(
        events=events,
        trends=trends,
        previous_issue=previous_issue,
        health=health,
        week=week,
        generated_at=now,
        window_start=window_start,
        window_end=window_end,
    )
    if client is not None and events:
        issue = await _synthesize_issue(client, issue, events)
    validate_issue_evidence(issue, {event.event_id for event in events})

    cfg.intelligence_dir.mkdir(parents=True, exist_ok=True)
    output_path = cfg.intelligence_dir / f"{week}.json"
    _atomic_json_write(output_path, issue.model_dump(mode="json"))
    save_trends(cfg.trends_file, trends)
    return issue


def _load_previous_issue(directory: Path, current_week: str) -> WeeklyIssue | None:
    if not directory.exists():
        return None
    candidates = sorted(
        path for path in directory.glob("*.json") if path.stem < current_week
    )
    if not candidates:
        return None
    return WeeklyIssue.model_validate_json(candidates[-1].read_text())


async def _synthesize_issue(
    client: AsyncAnthropic,
    issue: WeeklyIssue,
    events: list[MaterialEvent],
) -> WeeklyIssue:
    """Constrain model prose to event IDs selected by the deterministic layer."""
    tool = {
        "name": "emit_weekly_synthesis",
        "description": "Write concise synthesis using only the supplied event IDs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "thesis": {"type": "string"},
                "intelligence_read": {"type": "string"},
                "executive_shifts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "headline": {"type": "string"},
                            "summary": {"type": "string"},
                            "evidence_event_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["headline", "summary", "evidence_event_ids"],
                    },
                },
            },
            "required": ["thesis", "intelligence_read", "executive_shifts"],
        },
    }
    event_payload = [
        {
            "event_id": event.event_id,
            "title": event.title,
            "development": event.development,
            "implication": event.implication,
            "tracks": [track.value for track in event.tracks],
            "source_tier": event.source_tier.value,
        }
        for event in events
    ]
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        system=(
            "You write a weekly Web-content intelligence brief. Use only supplied "
            "facts and event IDs. Never invent an ID or unsupported claim."
        ),
        tools=[tool],
        tool_choice={"type": "tool", "name": "emit_weekly_synthesis"},
        messages=[
            {
                "role": "user",
                "content": json.dumps(event_payload, ensure_ascii=False),
            }
        ],
    )
    for block in response.content:
        if getattr(block, "type", None) != "tool_use":
            continue
        args = dict(block.input or {})
        candidate = issue.model_copy(deep=True)
        candidate.thesis = str(args.get("thesis") or issue.thesis)
        candidate.intelligence_read = str(
            args.get("intelligence_read") or issue.intelligence_read
        )
        candidate.executive_shifts = [
            ExecutiveShift.model_validate(item)
            for item in args.get("executive_shifts", [])
        ]
        candidate.model_generated = True
        validate_issue_evidence(candidate, {event.event_id for event in events})
        return candidate
    raise RuntimeError("weekly synthesis did not return tool_use")


def _atomic_json_write(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    os.replace(temporary, path)


def _cli() -> None:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    cfg = Config.from_env()
    client = (
        AsyncAnthropic(api_key=cfg.anthropic_api_key)
        if cfg.anthropic_api_key
        else None
    )
    issue = asyncio.run(
        generate_weekly_intelligence(
            repo_root=cfg.repo_root,
            now=datetime.now(tz=UTC),
            client=client,
        )
    )
    print(json.dumps(issue.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    _cli()
