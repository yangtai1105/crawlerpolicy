"""Build persistent, evidence-aware insight threads from published feed items."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from pipeline.feed import PublicationStatus

_KEY_RX = re.compile(r"[^a-z0-9]+")
_TITLE_ACRONYMS = {
    "ai",
    "api",
    "cdn",
    "dns",
    "dsa",
    "eu",
    "ip",
    "mcp",
    "uk",
    "us",
    "vlose",
    "waf",
}


class ThreadFeedRecord(BaseModel):
    slug: str
    status: PublicationStatus
    detected_at: datetime
    trend_signals: list[str] = Field(default_factory=list)
    development_slug: str | None = None
    insight: str


class InsightThread(BaseModel):
    key: str
    title: str
    thesis: str
    direction: Literal["emerging", "developing"]
    confidence: Literal["low", "medium", "high"]
    first_observed_at: datetime
    last_updated_at: datetime
    related_feed_slugs: list[str] = Field(default_factory=list)
    verified_development_slugs: list[str] = Field(default_factory=list)


class InsightThreadRegistry(BaseModel):
    schema_version: int = 1
    threads: list[InsightThread] = Field(default_factory=list)


def _normalize_key(value: str) -> str:
    return _KEY_RX.sub("-", value.casefold()).strip("-")


def _title_for_key(key: str) -> str:
    return " ".join(
        part.upper() if part in _TITLE_ACRONYMS else part.capitalize()
        for part in key.split("-")
        if part
    )


def _section(body: str, heading: str) -> str:
    escaped = re.escape(heading)
    match = re.search(
        rf"^## {escaped}\s*$\n+([\s\S]*?)(?=^## |\Z)",
        body,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def _load_event_signals(events_dir: Path | None) -> dict[str, list[str]]:
    if events_dir is None or not events_dir.exists():
        return {}
    signals_by_slug: dict[str, list[str]] = {}
    for path in sorted(events_dir.glob("*.md")):
        parts = path.read_text().split("---", 2)
        if len(parts) != 3:
            continue
        frontmatter = yaml.safe_load(parts[1]) or {}
        slug = frontmatter.get("slug")
        impact = _section(parts[2], "Trend impact")
        signals = [
            line[2:].strip()
            for line in impact.splitlines()
            if line.startswith("- ") and line[2:].strip()
        ]
        if slug and signals:
            signals_by_slug[str(slug)] = signals
    return signals_by_slug


def _load_feed_records(
    feed_dir: Path,
    event_signals: dict[str, list[str]],
) -> list[ThreadFeedRecord]:
    if not feed_dir.exists():
        return []
    records: list[ThreadFeedRecord] = []
    for path in sorted(feed_dir.glob("*.md")):
        parts = path.read_text().split("---", 2)
        if len(parts) != 3:
            raise ValueError(f"{path} is missing YAML frontmatter")
        frontmatter = yaml.safe_load(parts[1])
        frontmatter["insight"] = _section(parts[2], "Insight")
        record = ThreadFeedRecord.model_validate(frontmatter)
        if not record.trend_signals and record.development_slug:
            record = record.model_copy(
                update={
                    "trend_signals": event_signals.get(record.development_slug, [])
                }
            )
        records.append(record)
    return records


def _confidence(records: list[ThreadFeedRecord]) -> Literal["low", "medium", "high"]:
    if any(
        record.status is PublicationStatus.VERIFIED and record.development_slug
        for record in records
    ):
        return "high"
    if any(record.status is PublicationStatus.REPORTED for record in records):
        return "medium"
    return "low"


def build_insight_threads(
    feed_dir: Path,
    events_dir: Path | None = None,
) -> InsightThreadRegistry:
    grouped: dict[str, list[ThreadFeedRecord]] = {}
    event_signals = _load_event_signals(events_dir)
    for record in _load_feed_records(feed_dir, event_signals):
        keys = list(
            dict.fromkeys(
                key
                for signal in record.trend_signals
                if (key := _normalize_key(signal))
            )
        )
        for key in keys:
            grouped.setdefault(key, []).append(record)

    threads: list[InsightThread] = []
    for key, records in sorted(grouped.items()):
        ordered = sorted(records, key=lambda item: (item.detected_at, item.slug))
        latest = ordered[-1]
        verified = list(
            dict.fromkeys(
                record.development_slug
                for record in ordered
                if record.status is PublicationStatus.VERIFIED
                and record.development_slug is not None
            )
        )
        threads.append(
            InsightThread(
                key=key,
                title=_title_for_key(key),
                thesis=latest.insight,
                direction="developing" if len(ordered) > 1 else "emerging",
                confidence=_confidence(ordered),
                first_observed_at=ordered[0].detected_at,
                last_updated_at=latest.detected_at,
                related_feed_slugs=[record.slug for record in ordered],
                verified_development_slugs=verified,
            )
        )
    return InsightThreadRegistry(threads=threads)


def save_insight_threads(path: Path, registry: InsightThreadRegistry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(registry.model_dump(mode="json"), indent=2, ensure_ascii=False)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload + "\n")
    os.replace(temporary, path)


def update_insight_threads(
    *,
    feed_dir: Path,
    events_dir: Path | None,
    path: Path,
) -> InsightThreadRegistry:
    registry = build_insight_threads(feed_dir, events_dir)
    save_insight_threads(path, registry)
    return registry
