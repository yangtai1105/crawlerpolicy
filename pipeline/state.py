"""Per-source state persistence under `state/{slug}.json`."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class SourceState:
    last_checked_at: datetime | None = None
    last_fetch_succeeded_at: datetime | None = None
    last_evidence_at: datetime | None = None
    last_hash: str | None = None
    last_seen_guids: list[str] = field(default_factory=list)
    consecutive_failures: int = 0
    first_seen: bool = True


def load_state(state_dir: Path, slug: str) -> SourceState:
    p = state_dir / f"{slug}.json"
    if not p.exists():
        return SourceState()
    raw = json.loads(p.read_text())
    for field_name in (
        "last_checked_at",
        "last_fetch_succeeded_at",
        "last_evidence_at",
    ):
        if raw.get(field_name):
            raw[field_name] = datetime.fromisoformat(raw[field_name])
    return SourceState(**raw)


def save_state(state_dir: Path, slug: str, state: SourceState) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    p = state_dir / f"{slug}.json"
    tmp = p.with_suffix(".json.tmp")
    d = asdict(state)
    for field_name in (
        "last_checked_at",
        "last_fetch_succeeded_at",
        "last_evidence_at",
    ):
        if d[field_name]:
            d[field_name] = d[field_name].isoformat()
    tmp.write_text(json.dumps(d, indent=2))
    os.replace(tmp, p)
