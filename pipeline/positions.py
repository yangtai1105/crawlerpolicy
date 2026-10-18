"""Position state for the comparison matrix.

One record per (player, protocol) that has ever held a non-default position.
An absent record means `none` and is not stored, so this file grows with
observed positions rather than with the size of the grid.

The pipeline never writes this file. Only a merged pull request does — see
`pipeline/map_proposals.py`, which writes proposals and nothing else.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class PositionStatus(StrEnum):
    SHIPPED = "shipped"
    PREVIEW = "preview"
    STATED = "stated"
    DECLINED = "declined"
    NONE = "none"


class EvidenceLevel(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"


class Position(BaseModel):
    player_slug: str
    protocol_slug: str
    status: PositionStatus
    since: str
    previous_status: PositionStatus = PositionStatus.NONE
    last_changed_at: datetime
    evidence_level: EvidenceLevel
    source_urls: list[str] = Field(default_factory=list)
    supporting_development_slugs: list[str] = Field(default_factory=list)
    proposed_by: str = ""
    # Set by the human merge, never by the pipeline.
    merged_at: datetime | None = None
    note: str = ""


class PositionRegistry(BaseModel):
    schema_version: int = 1
    positions: list[Position] = Field(default_factory=list)

    def get(self, player_slug: str, protocol_slug: str) -> Position | None:
        for position in self.positions:
            if position.player_slug == player_slug and position.protocol_slug == protocol_slug:
                return position
        return None


def position_key(player_slug: str, protocol_slug: str) -> str:
    """Stable identifier for a cell, for proposal filenames and log lines."""
    return f"{player_slug}×{protocol_slug}"


def may_change(evidence_level: EvidenceLevel) -> bool:
    """Only primary evidence may move a published position (spec §5.1)."""
    return evidence_level is EvidenceLevel.PRIMARY


def load_positions(path: Path) -> PositionRegistry:
    """Load merged position state. A missing file is an empty registry."""
    if not path.exists():
        return PositionRegistry()
    return PositionRegistry.model_validate_json(path.read_text())


def save_positions(path: Path, registry: PositionRegistry) -> None:
    """Write atomically, matching the pattern in pipeline/trends.py."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(registry.model_dump(mode="json"), indent=2, ensure_ascii=False)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload + "\n")
    os.replace(temporary, path)


def changes_within(
    registry: PositionRegistry, now: datetime, days: int = 7
) -> list[Position]:
    """Positions whose `last_changed_at` falls inside the window.

    "Changes this week" is derived from this, never stored as a counter.
    """
    cutoff = now.timestamp() - days * 86400
    return [p for p in registry.positions if p.last_changed_at.timestamp() >= cutoff]
