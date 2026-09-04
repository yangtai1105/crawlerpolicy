"""Deterministic daily edition selection from published feed records."""
from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from pipeline.feed import PublicationStatus


class FeedRecord(BaseModel):
    slug: str
    status: PublicationStatus
    importance: float = Field(ge=0, le=1)
    published_at: datetime
    detected_at: datetime
    backfilled: bool = False


class DailyBriefItem(BaseModel):
    slug: str
    status: PublicationStatus
    importance: float = Field(ge=0, le=1)
    published_at: datetime


class DailyBrief(BaseModel):
    schema_version: int = 1
    edition_date: date
    generated_at: datetime
    status: Literal["published", "quiet"]
    note: str
    items: list[DailyBriefItem] = Field(default_factory=list, max_length=5)


def load_feed_records(feed_dir: Path) -> list[FeedRecord]:
    if not feed_dir.exists():
        return []
    records: list[FeedRecord] = []
    for path in sorted(feed_dir.glob("*.md")):
        parts = path.read_text().split("---", 2)
        if len(parts) != 3:
            raise ValueError(f"{path} is missing YAML frontmatter")
        raw = yaml.safe_load(parts[1])
        records.append(FeedRecord.model_validate(raw))
    return records


def build_daily_brief(
    *,
    feed_dir: Path,
    edition_date: date,
    generated_at: datetime,
) -> DailyBrief:
    candidates = [
        item
        for item in load_feed_records(feed_dir)
        if item.detected_at.date() == edition_date and not item.backfilled
    ]
    ordered = sorted(
        candidates,
        key=lambda item: (item.importance, item.published_at, item.slug),
        reverse=True,
    )[:5]
    if not ordered:
        return DailyBrief(
            edition_date=edition_date,
            generated_at=generated_at,
            status="quiet",
            note="No material ecosystem developments were published in this daily window.",
        )
    return DailyBrief(
        edition_date=edition_date,
        generated_at=generated_at,
        status="published",
        note="Highest-consequence developments detected in this daily window.",
        items=[
            DailyBriefItem(
                slug=item.slug,
                status=item.status,
                importance=item.importance,
                published_at=item.published_at,
            )
            for item in ordered
        ],
    )


def save_daily_brief(path: Path, brief: DailyBrief) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(brief.model_dump(mode="json"), indent=2, ensure_ascii=False)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload + "\n")
    os.replace(temporary, path)
