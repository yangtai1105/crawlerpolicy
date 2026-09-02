"""Select historical direct-source evidence for reader-facing backfill."""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from pipeline.evidence import EvidenceRecord, load_evidence
from pipeline.sources import Source, SourceType


@dataclass(frozen=True)
class BackfillCandidate:
    path: Path
    record: EvidenceRecord
    source: Source
    item_date: datetime


class BackfillSelectionCounts(BaseModel):
    total_evidence: int = 0
    eligible: int = 0
    excluded_search: int = 0
    unknown_source: int = 0
    outside_window: int = 0
    duplicate: int = 0
    invalid: int = 0


class BackfillOutcome(StrEnum):
    PUBLISHED = "published"
    IRRELEVANT = "irrelevant"
    DUPLICATE = "duplicate"
    FAILED = "failed"
    EXCLUDED_SOURCE = "excluded_source"
    OUTSIDE_WINDOW = "outside_window"

    @property
    def is_terminal(self) -> bool:
        return self is not BackfillOutcome.FAILED


class BackfillEntry(BaseModel):
    evidence_id: str
    outcome: BackfillOutcome
    updated_at: datetime
    feed_path: str | None = None
    development_path: str | None = None
    reason: str | None = None


class BackfillManifest(BaseModel):
    batch_id: str
    since: datetime
    until: datetime
    entries: dict[str, BackfillEntry] = Field(default_factory=dict)
    summary: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


def batch_id(since: datetime, until: datetime) -> str:
    return f"direct-evidence_{since.date().isoformat()}_{until.date().isoformat()}"


def manifest_path(data_dir: Path, since: datetime, until: datetime) -> Path:
    return data_dir / "backfills" / f"{batch_id(since, until)}.json"


def load_manifest(
    path: Path, *, since: datetime, until: datetime
) -> BackfillManifest:
    expected_id = batch_id(since, until)
    if not path.exists():
        return BackfillManifest(batch_id=expected_id, since=since, until=until)
    manifest = BackfillManifest.model_validate_json(path.read_text())
    if (
        manifest.batch_id != expected_id
        or manifest.since != since
        or manifest.until != until
    ):
        raise ValueError("backfill manifest window does not match requested window")
    return manifest


def save_manifest(path: Path, manifest: BackfillManifest) -> None:
    """Atomically persist progress so an interrupted batch can resume safely."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = manifest.model_dump_json(indent=2)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.stem}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(payload)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


@dataclass
class BackfillSelection:
    candidates: list[BackfillCandidate] = field(default_factory=list)
    excluded_search_ids: list[str] = field(default_factory=list)
    unknown_source_ids: list[str] = field(default_factory=list)
    outside_window_ids: list[str] = field(default_factory=list)
    duplicate_ids: list[str] = field(default_factory=list)
    invalid_paths: list[str] = field(default_factory=list)

    @property
    def counts(self) -> BackfillSelectionCounts:
        groups = (
            self.candidates,
            self.excluded_search_ids,
            self.unknown_source_ids,
            self.outside_window_ids,
            self.duplicate_ids,
            self.invalid_paths,
        )
        return BackfillSelectionCounts(
            total_evidence=sum(len(group) for group in groups),
            eligible=len(self.candidates),
            excluded_search=len(self.excluded_search_ids),
            unknown_source=len(self.unknown_source_ids),
            outside_window=len(self.outside_window_ids),
            duplicate=len(self.duplicate_ids),
            invalid=len(self.invalid_paths),
        )


def load_published_evidence_ids(feed_dir: Path) -> set[str]:
    """Return evidence IDs already represented in the public feed."""
    published: set[str] = set()
    if not feed_dir.exists():
        return published
    for path in feed_dir.glob("**/*.md"):
        text = path.read_text()
        if not text.startswith("---"):
            continue
        try:
            frontmatter = yaml.safe_load(text.split("---", 2)[1]) or {}
        except (ValueError, yaml.YAMLError):
            continue
        evidence_ids = frontmatter.get("evidence_ids", [])
        if isinstance(evidence_ids, list):
            published.update(item for item in evidence_ids if isinstance(item, str))
    return published


def select_candidates(
    *,
    evidence_dir: Path,
    feed_dir: Path,
    sources: list[Source],
    since: datetime,
    until: datetime,
) -> BackfillSelection:
    """Classify all evidence and return eligible direct records newest first."""
    selection = BackfillSelection()
    source_by_slug = {source.slug: source for source in sources}
    published_ids = load_published_evidence_ids(feed_dir)

    if not evidence_dir.exists():
        return selection

    for path in sorted(evidence_dir.glob("*/*.json")):
        try:
            record = load_evidence(path)
        except (OSError, ValueError):
            selection.invalid_paths.append(str(path))
            continue

        source = source_by_slug.get(record.source)
        if source is None:
            selection.unknown_source_ids.append(record.evidence_id)
            continue
        if source.type is SourceType.GEMINI_SEARCH:
            selection.excluded_search_ids.append(record.evidence_id)
            continue

        item_date = record.published_at or record.detected_at
        if item_date < since or item_date > until:
            selection.outside_window_ids.append(record.evidence_id)
            continue
        if record.evidence_id in published_ids:
            selection.duplicate_ids.append(record.evidence_id)
            continue

        selection.candidates.append(
            BackfillCandidate(path=path, record=record, source=source, item_date=item_date)
        )

    selection.candidates.sort(
        key=lambda candidate: (candidate.item_date, candidate.record.evidence_id),
        reverse=True,
    )
    selection.excluded_search_ids.sort()
    selection.unknown_source_ids.sort()
    selection.outside_window_ids.sort()
    selection.duplicate_ids.sort()
    selection.invalid_paths.sort()
    return selection
