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
    last_hash: str | None = None
    last_seen_guids: list[str] = field(default_factory=list)
    consecutive_failures: int = 0
    first_seen: bool = True


def load_state(state_dir: Path, slug: str) -> SourceState:
    p = state_dir / f"{slug}.json"
    if not p.exists():
        return SourceState()
    raw = json.loads(p.read_text())
    if raw.get("last_checked_at"):
        raw["last_checked_at"] = datetime.fromisoformat(raw["last_checked_at"])
    return SourceState(**raw)


def save_state(state_dir: Path, slug: str, state: SourceState) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    p = state_dir / f"{slug}.json"
    tmp = p.with_suffix(".json.tmp")
    d = asdict(state)
    if d["last_checked_at"]:
        d["last_checked_at"] = d["last_checked_at"].isoformat()
    tmp.write_text(json.dumps(d, indent=2))
    os.replace(tmp, p)
