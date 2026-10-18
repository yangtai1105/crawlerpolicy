"""Validate data/positions.seed.yaml before it is applied by hand.

A seed row is a published matrix cell. The gate is deliberately strict: a
primary source URL, a real effective date, and names that already exist in the
controlled registries. `none` is rejected because absence is not recorded —
an unwritten cell already reads as none.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from pipeline.entities import EntityRegistry, load_registry  # noqa: E402
from pipeline.positions import (  # noqa: E402
    EvidenceLevel,
    Position,
    PositionRegistry,
    PositionStatus,
)

SEED_PATH = Path("data/positions.seed.yaml")


class SeedRow(BaseModel):
    player: str
    protocol: str
    status: str
    since: str
    source_url: str
    note: str = ""


def validate_seed(rows: list[SeedRow], registry: EntityRegistry) -> list[str]:
    """Return human-readable errors; an empty list means the seed is applicable."""
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()

    for index, row in enumerate(rows, start=1):
        where = f"row {index} ({row.player} × {row.protocol})"

        player_slug = registry.resolve_player(row.player)
        if player_slug is None:
            errors.append(f"{where}: player {row.player!r} is not in entities/players.yaml")
        protocol_slug = registry.resolve_protocol(row.protocol)
        if protocol_slug is None:
            errors.append(
                f"{where}: protocol {row.protocol!r} is not in entities/protocols.yaml"
            )

        if not row.source_url.strip():
            errors.append(f"{where}: source_url is required — every cell needs its evidence")
        elif not row.source_url.startswith("http"):
            errors.append(f"{where}: source_url {row.source_url!r} is not a URL")

        if not row.since.strip():
            errors.append(f"{where}: since is required — the date the status took effect")
        else:
            try:
                date.fromisoformat(row.since)
            except ValueError:
                errors.append(f"{where}: since {row.since!r} is not an ISO date")

        try:
            status = PositionStatus(row.status.strip().lower())
        except ValueError:
            errors.append(f"{where}: status {row.status!r} is not a published status")
        else:
            if status is PositionStatus.NONE:
                errors.append(
                    f"{where}: status 'none' is not recorded — an absent cell already reads none"
                )

        if player_slug and protocol_slug:
            pair = (player_slug, protocol_slug)
            if pair in seen:
                errors.append(f"{where}: duplicate cell {player_slug}×{protocol_slug}")
            seen.add(pair)

    return errors


def seed_to_registry(rows: list[SeedRow], registry: EntityRegistry) -> PositionRegistry:
    """Convert validated rows into a position registry ready to write."""
    positions = []
    for row in rows:
        player_slug = registry.resolve_player(row.player)
        protocol_slug = registry.resolve_protocol(row.protocol)
        if player_slug is None or protocol_slug is None:
            continue
        positions.append(
            Position(
                player_slug=player_slug,
                protocol_slug=protocol_slug,
                status=PositionStatus(row.status.strip().lower()),
                since=row.since,
                last_changed_at=f"{row.since}T00:00:00+00:00",
                evidence_level=EvidenceLevel.PRIMARY,
                source_urls=[row.source_url],
                proposed_by="seed",
                note=row.note,
            )
        )
    positions.sort(key=lambda p: (p.player_slug, p.protocol_slug))
    return PositionRegistry(positions=positions)


def main() -> int:
    raw = yaml.safe_load(SEED_PATH.read_text()) or {}
    rows = [SeedRow(**row) for row in (raw.get("rows") or [])]
    errors = validate_seed(rows, load_registry())
    if errors:
        print(f"Seed is not applicable ({len(errors)} error(s)):")
        for error in errors:
            print(f"  {error}")
        return 1
    print(f"Seed is applicable: {len(rows)} row(s), every cell sourced and dated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
