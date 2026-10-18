"""Apply pending proposals onto the map/proposals branch, and render the PR body.

This runs only inside the `map/proposals` branch, whose contents reach
`data/positions.json` on the default branch exclusively through a human merge.
The daily pipeline never calls this module.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from pipeline.map_proposals import Proposal
from pipeline.positions import Position, load_positions, position_key, save_positions

PROPOSALS_DIR = Path("proposals")
POSITIONS_PATH = Path("data/positions.json")


def load_pending(proposals_dir: Path = PROPOSALS_DIR) -> list[Proposal]:
    return [
        Proposal.model_validate_json(path.read_text())
        for path in sorted(proposals_dir.glob("*.json"))
    ]


def apply(
    proposals: list[Proposal],
    positions_path: Path = POSITIONS_PATH,
    *,
    proposals_dir: Path | None = PROPOSALS_DIR,
) -> int:
    """Apply proposals, then clear the queue they came from.

    Deleting the applied files is what makes the queue drain: a proposal left
    in `proposals/` after the merge would be re-proposed every day forever,
    because the comparison would still see merged state it had already moved.
    """
    registry = load_positions(positions_path)
    now = datetime.now(UTC)
    applied = 0
    for proposal in proposals:
        existing = registry.get(proposal.player_slug, proposal.protocol_slug)
        if existing is not None:
            registry.positions.remove(existing)
        registry.positions.append(
            Position(
                player_slug=proposal.player_slug,
                protocol_slug=proposal.protocol_slug,
                status=proposal.to_status,
                since=proposal.since,
                previous_status=proposal.from_status,
                last_changed_at=now,
                evidence_level=proposal.evidence_level,
                source_urls=proposal.source_urls,
                supporting_development_slugs=(
                    [proposal.supporting_development_slug]
                    if proposal.supporting_development_slug
                    else []
                ),
                proposed_by=proposal.proposed_by,
            )
        )
        applied += 1
    registry.positions.sort(key=lambda p: (p.player_slug, p.protocol_slug))
    save_positions(positions_path, registry)
    if proposals_dir is not None:
        for path in sorted(proposals_dir.glob("*.json")):
            path.unlink()
    return applied


def render_body(proposals: list[Proposal]) -> str:
    lines = [
        "Position changes proposed by the daily run. Merging applies them to the map.",
        "",
        "Every change below is backed by a `verified` development from a primary",
        "source. Reported and signal grades cannot move a position.",
        "",
        "This branch is rebuilt from `main` on every run, so edits made directly",
        "on it are lost. To correct a cell, merge and then change it on `main`.",
        "",
    ]
    for proposal in proposals:
        lines.append(
            f"- **{position_key(proposal.player_slug, proposal.protocol_slug)}**: "
            f"`{proposal.from_status.value}` → `{proposal.to_status.value}` "
            f"· effective {proposal.since} · evidence {proposal.evidence_level.value}"
        )
        for url in proposal.source_urls:
            lines.append(f"  - {url}")
        if proposal.supporting_development_slug:
            lines.append(f"  - development: `{proposal.supporting_development_slug}`")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--body", action="store_true", help="print the PR body and exit")
    args = parser.parse_args()
    proposals = load_pending()
    if args.body:
        print(render_body(proposals), end="")
        return
    applied = apply(proposals)
    print(json.dumps({"applied": applied}))


if __name__ == "__main__":
    main()
