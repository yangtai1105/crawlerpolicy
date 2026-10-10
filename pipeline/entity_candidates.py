"""Review queue for entities analysis saw outside the controlled registries.

Appending here is the only way a protocol or player reaches the registries:
a human reads the queue and edits `entities/*.yaml`. Nothing in this module
writes those files.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

DEFAULT_CANDIDATES_PATH = Path("data/entity-candidates.json")

EntityKind = Literal["player", "protocol"]


class EntityCandidate(BaseModel):
    kind: EntityKind
    observed_name: str
    first_seen_at: datetime
    last_seen_at: datetime
    occurrences: int = 1
    evidence_ids: list[str] = Field(default_factory=list)
    feed_slugs: list[str] = Field(default_factory=list)


def _key(kind: str, name: str) -> str:
    return f"{kind}:{name.strip().casefold()}"


def load_candidates(path: Path = DEFAULT_CANDIDATES_PATH) -> dict[str, EntityCandidate]:
    """Load the queue. A missing file is an empty queue, not an error."""
    if not path.exists():
        return {}
    raw = json.loads(path.read_text() or "{}")
    return {
        key: EntityCandidate.model_validate(value)
        for key, value in raw.get("candidates", {}).items()
    }


def record_candidates(
    path: Path,
    kind: EntityKind,
    names: list[str],
    *,
    evidence_ids: list[str],
    feed_slug: str,
    now: datetime,
) -> None:
    """Merge observed out-of-vocabulary names into the queue.

    Re-recording the same `feed_slug` for a name is a no-op, so replaying a
    day never inflates `occurrences`.
    """
    candidates = load_candidates(path)
    changed = False

    for name in names:
        cleaned = name.strip()
        if not cleaned:
            continue
        key = _key(kind, cleaned)
        existing = candidates.get(key)
        if existing is None:
            candidates[key] = EntityCandidate(
                kind=kind,
                observed_name=cleaned,
                first_seen_at=now,
                last_seen_at=now,
                occurrences=1,
                evidence_ids=list(dict.fromkeys(evidence_ids)),
                feed_slugs=[feed_slug],
            )
            changed = True
            continue
        if feed_slug in existing.feed_slugs:
            continue
        existing.feed_slugs.append(feed_slug)
        existing.occurrences += 1
        existing.last_seen_at = now
        existing.evidence_ids = list(dict.fromkeys([*existing.evidence_ids, *evidence_ids]))
        changed = True

    if not changed:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "candidates": {
            key: json.loads(value.model_dump_json()) for key, value in sorted(candidates.items())
        },
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
