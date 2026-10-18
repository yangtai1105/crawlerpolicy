"""Propose position changes; never apply them.

This stage is a pure comparison with no model call: the analysis step has
already stated what position a development implies, so here we only diff those
claims against merged state and write `proposals/`. It must never write
`data/positions.json` — only a merged pull request does that.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field

from pipeline.feed import is_primary_tier
from pipeline.positions import (
    EvidenceLevel,
    PositionRegistry,
    PositionStatus,
    may_change,
)


class FeedRecord(BaseModel):
    """The minimal shape of a feed record this stage reads."""

    slug: str
    status: str
    source_tier: str
    source_urls: list[str] = Field(default_factory=list)
    event_date: str
    development_slug: str = ""
    position_claims: list[dict] = Field(default_factory=list)


class Proposal(BaseModel):
    player_slug: str
    protocol_slug: str
    from_status: PositionStatus
    to_status: PositionStatus
    evidence_level: EvidenceLevel
    since: str
    source_urls: list[str] = Field(default_factory=list)
    supporting_development_slug: str = ""
    feed_slug: str = ""
    proposed_by: str = ""


def evidence_level_for(source_tier: str) -> EvidenceLevel:
    """Map a source tier onto the two evidence levels the matrix recognises."""
    if is_primary_tier(source_tier):
        return EvidenceLevel.PRIMARY
    return EvidenceLevel.SECONDARY


def collect_proposals(
    feed_records: list[FeedRecord],
    registry: PositionRegistry,
    *,
    run_id: str,
) -> list[Proposal]:
    """Diff each verified record's position claims against merged state."""
    proposals: list[Proposal] = []

    for record in feed_records:
        if record.status.strip().lower() != "verified":
            continue
        level = evidence_level_for(record.source_tier)
        if not may_change(level):
            continue
        for claim in record.position_claims:
            try:
                to_status = PositionStatus(str(claim["status"]).strip().lower())
                player_slug = str(claim["player"])
                protocol_slug = str(claim["protocol"])
            except (KeyError, ValueError):
                continue
            if to_status is PositionStatus.NONE:
                # `none` means "no public position". The spec forbids inferring
                # absence, so a none-claim can never propose a change — it would
                # silently delete a published cell.
                continue
            current = registry.get(player_slug, protocol_slug)
            from_status = current.status if current else PositionStatus.NONE
            if from_status is to_status:
                continue
            proposals.append(
                Proposal(
                    player_slug=player_slug,
                    protocol_slug=protocol_slug,
                    from_status=from_status,
                    to_status=to_status,
                    evidence_level=level,
                    since=record.event_date[:10],
                    source_urls=list(record.source_urls),
                    supporting_development_slug=record.development_slug,
                    feed_slug=record.slug,
                    proposed_by=run_id,
                )
            )

    return proposals


def save_proposals(
    proposals_dir: Path, proposals: list[Proposal], *, date_str: str
) -> list[Path]:
    """Write one file per proposal. Writes nothing when there is nothing to say.

    Clears this date's existing files first: a same-day re-run that proposes
    fewer cells than an earlier run that day must not leave stale
    higher-index files behind.
    """
    if proposals_dir.exists():
        for stale in proposals_dir.glob(f"{date_str}-*.json"):
            stale.unlink()
    if not proposals:
        return []
    proposals_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for index, proposal in enumerate(proposals, start=1):
        path = proposals_dir / f"{date_str}-{index}.json"
        payload = json.dumps(proposal.model_dump(mode="json"), indent=2, ensure_ascii=False)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(payload + "\n")
        os.replace(temporary, path)
        written.append(path)
    return written
