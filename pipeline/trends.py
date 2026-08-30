"""Durable trend registry with deterministic evidence-tier gating."""
from __future__ import annotations

import json
import os
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from pipeline.taxonomy import SourceTier


class TrendStatus(StrEnum):
    ACCELERATING = "accelerating"
    STABLE = "stable"
    EMERGING = "emerging"
    REVERSING = "reversing"
    STALLED = "stalled"


class EventEvidence(BaseModel):
    event_id: str
    source_tier: SourceTier
    evidence_ids: list[str] = Field(default_factory=list)
    event_date: datetime


class Trend(BaseModel):
    key: str
    title: str
    status: TrendStatus
    previous_status: TrendStatus | None = None
    thesis: str = ""
    evidence_event_ids: list[str] = Field(default_factory=list)
    last_material_update: datetime | None = None
    delta_explanation: str = ""


class TrendDelta(BaseModel):
    trend_key: str
    previous_status: TrendStatus
    current_status: TrendStatus
    accepted: bool
    reason: str
    evidence_event_ids: list[str] = Field(default_factory=list)
    explanation: str = ""


class TrendRegistry(BaseModel):
    schema_version: int = 1
    trends: list[Trend] = Field(default_factory=list)


def propose_delta(
    trend: Trend,
    events: list[EventEvidence],
    *,
    proposed: TrendStatus,
) -> TrendDelta:
    """Accept status movement only with resolvable authoritative evidence."""
    if proposed is trend.status:
        return TrendDelta(
            trend_key=trend.key,
            previous_status=trend.status,
            current_status=trend.status,
            accepted=True,
            reason="status unchanged",
        )

    authoritative = [
        event
        for event in events
        if event.source_tier in {SourceTier.PRIMARY, SourceTier.MEASUREMENT}
        and event.evidence_ids
    ]
    if not authoritative:
        return TrendDelta(
            trend_key=trend.key,
            previous_status=trend.status,
            current_status=trend.status,
            accepted=False,
            reason="status changes require primary or measurement evidence",
        )

    return TrendDelta(
        trend_key=trend.key,
        previous_status=trend.status,
        current_status=proposed,
        accepted=True,
        reason="supported by authoritative evidence",
        evidence_event_ids=[event.event_id for event in authoritative],
    )


def load_trends(path: Path) -> list[Trend]:
    if not path.exists():
        return []
    registry = TrendRegistry.model_validate_json(path.read_text())
    return registry.trends


def save_trends(path: Path, trends: list[Trend]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        TrendRegistry(trends=trends).model_dump(mode="json"),
        indent=2,
        ensure_ascii=False,
    )
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload + "\n")
    os.replace(temporary, path)
