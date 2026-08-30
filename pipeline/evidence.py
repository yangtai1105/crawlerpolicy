"""Replayable evidence records persisted before model analysis."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class EvidenceStage(StrEnum):
    FETCHED = "fetched"
    ANALYZED = "analyzed"
    PUBLISHED = "published"
    FAILED_ANALYSIS = "failed_analysis"


class EvidenceRecord(BaseModel):
    evidence_id: str
    source: str
    source_url: str
    published_at: datetime | None = None
    detected_at: datetime
    content_path: str
    content_hash: str | None = None
    external_id: str
    stage: EvidenceStage = EvidenceStage.FETCHED
    analysis_attempts: int = Field(default=0, ge=0)
    last_error: str | None = None
    title: str | None = None
    content: str = ""
    previous_content: str = ""
    unified_diff: str = ""


def make_evidence_id(source_slug: str, external_id: str) -> str:
    """Return a stable, source-scoped ID without exposing the full external ID."""
    digest = hashlib.sha256(f"{source_slug}\0{external_id}".encode()).hexdigest()[:16]
    return f"{source_slug}--{digest}"


def save_evidence(root: Path, record: EvidenceRecord) -> Path:
    """Atomically save one evidence record below its source directory."""
    source_dir = root / record.source
    source_dir.mkdir(parents=True, exist_ok=True)
    destination = source_dir / f"{record.evidence_id}.json"
    payload = json.dumps(record.model_dump(mode="json"), indent=2, ensure_ascii=False)

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=source_dir,
            prefix=f".{record.evidence_id}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(payload)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        os.replace(temp_path, destination)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
    return destination


def load_evidence(path: Path) -> EvidenceRecord:
    return EvidenceRecord.model_validate_json(path.read_text())


def pending_analysis(root: Path) -> list[tuple[Path, EvidenceRecord]]:
    """Return fetched or failed-analysis evidence ordered oldest first."""
    if not root.exists():
        return []
    queued: list[tuple[Path, EvidenceRecord]] = []
    for path in root.glob("*/*.json"):
        record = load_evidence(path)
        if record.stage in {
            EvidenceStage.FETCHED,
            EvidenceStage.FAILED_ANALYSIS,
        }:
            queued.append((path, record))
    return sorted(queued, key=lambda item: (item[1].detected_at, item[1].evidence_id))
