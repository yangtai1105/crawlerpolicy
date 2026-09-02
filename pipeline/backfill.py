"""Select historical direct-source evidence for reader-facing backfill."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import yaml
from pydantic import BaseModel

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
