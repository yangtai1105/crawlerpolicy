# Positions and Proposals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the position store, the propose-then-merge pipeline, and the weekly reading layer, so the comparison matrix has real, evidence-backed state that only a human merge can change.

**Architecture:** The analysis step — which already reads the evidence and already emits controlled entity slugs — additionally states what position each development implies. The proposal stage is then **pure comparison with no model call**: it reads verified feed records, diffs their claims against merged state, and writes `proposals/` only. A workflow turns proposals into one long-lived pull request; merging is the only thing that writes `data/positions.json`.

**Tech Stack:** Python 3.12, uv, pydantic v2, pytest, ruff (line-length 100, `E,F,I,UP,B,SIM`), GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-10-agentic-map-layer-design.md` §5, §6, §7

## Global Constraints

- Python `>=3.12`; run everything through `uv run`.
- ruff: `line-length = 100`, `target-version = "py312"`, lint select `["E", "F", "I", "UP", "B", "SIM"]`. All imports at top of file.
- **The pipeline never writes `data/positions.json` or `data/readings/`.** Only a merged pull request does. A stage that writes either is a design error.
- **`signal`- and `reported`-grade evidence can never move a position.** Only `status: verified` with a primary-grade source.
- **Every published change carries `evidence_level: primary`.** `secondary` is corroboration only and can never be the sole basis for a status.
- **`declined` requires an explicit public statement in a primary source.** The distinction between `none` and `declined` is never inferred.
- **An absent record means `none` and is not stored.** The file grows with observed positions, not with the size of the grid.
- **The daily feed is unaffected.** A proposal-stage failure records `degraded` and never blocks publication; required coverage for the feed does not include map proposals.
- **No silent registry growth.** Entity names outside the registries go to `data/entity-candidates.json`; the pipeline cannot add a protocol or player.
- Nothing under `content/` is rewritten. Historical records are not backfilled.
- All writes to `data/` use the temp-file-plus-replace pattern already in `pipeline/trends.py:111-113`.
- Tests make no network calls; model providers are stubbed.
- Do not push. Commit on a feature branch.

## Two decisions taken while planning, with their evidence

**1. The proposal stage reads feed records, not development records — and `pipeline/event_writer.py` is not touched.**

Spec §7 says the stage reads "the day's `verified` developments with their entity links". Measured on the current corpus: `content/events/*.md` carry `actors` only and **no** entity links, while every one of the 18 development-bearing feed records carries `development_slug`. Everything a proposal needs is already on the feed record — `status` (the evidence gate), `players` / `protocols` (entity links), `development_slug` (for `supporting_development_slugs`), `source_urls` and `source_tier` (evidence level). The development record would add nothing, so adding fields to `event_writer` would be dead weight. A "verified development" in this project *is* a verified feed record that also produced a development, so this is an implementation reading of §7, not a departure from it.

**2. The position a development implies is stated by the analysis step, not inferred by the proposal stage.**

§7 says the stage "compares implied positions against merged state" without saying what supplies the implication. A feed record carries entity links but no per-pair status, and deciding between `shipped` / `preview` / `stated` / `declined` from prose is a judgement. Three options: have the analyzer state it (it already holds the evidence in context and already emits controlled slugs), make a second model call inside the proposal stage, or keyword-match. Keyword matching is far too fragile for something that moves published state, and a second model call adds a failure mode and a cost to a stage that should be deterministic. So the analyzer emits `position_claims`, and the proposal stage becomes pure comparison that cannot fail from a model error.

## What this plan does not do

- No matrix page, protocol page or player page — sub-project 3b.
- No reading *rendering* — this plan produces `data/readings/`; 3b renders it.
- **No populated matrix.** Task 7 builds the seeding harness and a validator; filling it needs a per-cell research pass with a primary source URL for every cell, which is a separate effort. See Task 7's note.

## File Structure

| File | Responsibility |
|---|---|
| `pipeline/positions.py` (create) | Position models, load/save, the invariant gate, `changes_within` |
| `pipeline/config.py` (modify) | `positions_path`, `readings_dir`, `proposals_dir` properties |
| `pipeline/analyzer.py` (modify) | Emit and resolve `position_claims` |
| `pipeline/feed_writer.py` (modify) | Persist `position_claims` to frontmatter |
| `pipeline/map_proposals.py` (create) | Deterministic comparison; writes `proposals/` only |
| `pipeline/check.py` (modify) | Run the proposal stage after publication, non-required |
| `pipeline/readings.py` (create) | The reading model and generator — one subject at a time |
| `pipeline/weekly_readings.py` (create) | The weekly runner: windowing, grouping, PR body |
| `pipeline/apply_proposals.py` (create) | Applies proposals inside the review branch; drains the queue |
| `.github/workflows/map-proposals.yml` (create) | Proposals → one long-lived pull request |
| `.github/workflows/map-readings.yml` (create) | Weekly readings → a second long-lived pull request |
| `data/positions.seed.yaml` (create) | Human-authored seed, one row per cell with its source |
| `scripts/validate_seed.py` (create) | Refuses a seed row without a primary source URL and a date |

---

### Task 1: The position store

**Files:**
- Create: `pipeline/positions.py`
- Modify: `pipeline/config.py`
- Test: `tests/test_positions.py`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `PositionStatus` — `StrEnum`: `SHIPPED = "shipped"`, `PREVIEW = "preview"`, `STATED = "stated"`, `DECLINED = "declined"`, `NONE = "none"`
  - `EvidenceLevel` — `StrEnum`: `PRIMARY = "primary"`, `SECONDARY = "secondary"`
  - `Position` — pydantic model, fields per spec §5
  - `PositionRegistry` — `{schema_version: int, positions: list[Position]}` with `.get(player_slug, protocol_slug) -> Position | None`
  - `position_key(player_slug: str, protocol_slug: str) -> str` → `f"{player}×{protocol}"`
  - `load_positions(path: Path) -> PositionRegistry` — a missing file is an empty registry
  - `save_positions(path: Path, registry: PositionRegistry) -> None` — atomic
  - `may_change(evidence_level: EvidenceLevel) -> bool`
  - `changes_within(registry: PositionRegistry, now: datetime, days: int = 7) -> list[Position]`
  - `Config.positions_path`, `Config.readings_dir`, `Config.proposals_dir`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_positions.py`:

```python
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from pipeline.positions import (
    EvidenceLevel,
    Position,
    PositionRegistry,
    PositionStatus,
    changes_within,
    load_positions,
    may_change,
    position_key,
    save_positions,
)

NOW = datetime(2026, 10, 17, 8, 0, tzinfo=UTC)


def _position(**overrides) -> Position:
    base = dict(
        player_slug="cloudflare",
        protocol_slug="web-bot-auth",
        status=PositionStatus.SHIPPED,
        since="2026-07-11",
        previous_status=PositionStatus.NONE,
        last_changed_at=NOW,
        evidence_level=EvidenceLevel.PRIMARY,
        source_urls=["https://blog.cloudflare.com/web-bot-auth"],
        supporting_development_slugs=["cloudflare-signs-bots"],
        proposed_by="run-2026-10-17",
        merged_at=NOW,
    )
    base.update(overrides)
    return Position(**base)


def test_absent_pair_reads_as_none_and_is_not_stored(tmp_path):
    path = tmp_path / "positions.json"
    save_positions(path, PositionRegistry(positions=[_position()]))

    registry = load_positions(path)

    assert registry.get("cloudflare", "web-bot-auth").status is PositionStatus.SHIPPED
    assert registry.get("akamai", "web-bot-auth") is None
    assert len(registry.positions) == 1


def test_loading_a_missing_file_is_an_empty_registry(tmp_path):
    registry = load_positions(tmp_path / "nope.json")

    assert registry.positions == []
    assert registry.get("cloudflare", "web-bot-auth") is None


def test_save_is_atomic_and_leaves_no_temp_file(tmp_path):
    path = tmp_path / "positions.json"

    save_positions(path, PositionRegistry(positions=[_position()]))

    assert path.exists()
    assert list(tmp_path.glob("*.tmp")) == []
    assert path.read_text().endswith("\n")


def test_only_primary_evidence_may_change_a_position():
    assert may_change(EvidenceLevel.PRIMARY) is True
    assert may_change(EvidenceLevel.SECONDARY) is False


def test_declined_is_a_first_class_status_distinct_from_none():
    declined = _position(status=PositionStatus.DECLINED)

    assert declined.status is not PositionStatus.NONE
    assert declined.status.value == "declined"


def test_changes_within_uses_last_changed_at():
    recent = _position(last_changed_at=NOW - timedelta(days=2))
    old = _position(protocol_slug="rsl", last_changed_at=NOW - timedelta(days=30))
    registry = PositionRegistry(positions=[recent, old])

    changed = changes_within(registry, NOW, days=7)

    assert [p.protocol_slug for p in changed] == ["web-bot-auth"]


def test_position_key_is_stable():
    assert position_key("cloudflare", "web-bot-auth") == "cloudflare×web-bot-auth"


def test_merged_at_is_optional_so_the_pipeline_can_never_set_it():
    unmerged = _position(merged_at=None)

    assert unmerged.merged_at is None
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_positions.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pipeline.positions'`

- [ ] **Step 3: Write the module**

Create `pipeline/positions.py`:

```python
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
```

- [ ] **Step 4: Add the three Config properties**

In `pipeline/config.py`, beside the existing `data_dir` property, add:

```python
    @property
    def positions_path(self) -> Path:
        return self.data_dir / "positions.json"

    @property
    def readings_dir(self) -> Path:
        return self.data_dir / "readings"

    @property
    def proposals_dir(self) -> Path:
        return self.repo_root / "proposals"
```

`proposals_dir` sits at the repository root rather than under `data/`, because `data/` is published pipeline output while `proposals/` is a staging area that only the workflow reads.

- [ ] **Step 5: Run the tests and the linter**

Run: `uv run pytest tests/test_positions.py -v && uv run ruff check pipeline tests`
Expected: all pass, no ruff findings.

- [ ] **Step 6: Commit**

```bash
git add pipeline/positions.py pipeline/config.py tests/test_positions.py
git commit -m "feat: add the position store

One record per (player, protocol) that has ever held a non-default
position; an absent record reads as none and is not stored, so the file
grows with observed positions rather than with the grid. Writes are
atomic, matching trends.py. may_change() encodes spec §5.1: only primary
evidence moves a published position, and merged_at is optional so the
pipeline can never set it."
```

---

### Task 2: The analysis step states what position a development implies

**Files:**
- Modify: `pipeline/analyzer.py`
- Modify: `pipeline/feed_writer.py`
- Test: `tests/test_analyzer.py`
- Test: `tests/test_feed_writer.py`

**Interfaces:**
- Consumes: `PositionStatus` from `pipeline.positions`; `EntityRegistry.resolve_player` / `.resolve_protocol` from `pipeline.entities`
- Produces:
  - `PositionClaim` — pydantic model: `player: str`, `protocol: str`, `status: str` (the raw model output, before resolution)
  - `ResolvedPositionClaim` — `player_slug: str`, `protocol_slug: str`, `status: PositionStatus`
  - `AnalyzerResponse.position_claims: list[PositionClaim]` (defaults to `[]`)
  - `AnalysisResult.position_claims: list[ResolvedPositionClaim]` (defaults to `[]`)
  - `resolve_position_claims(registry, claims) -> tuple[list[ResolvedPositionClaim], list[str], list[str]]` returning `(resolved, unknown_players, unknown_protocols)`
  - Frontmatter key `position_claims`, written only when non-empty

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_analyzer.py`:

```python
from pipeline.analyzer import PositionClaim, resolve_position_claims
from pipeline.positions import PositionStatus


def test_resolve_position_claims_keeps_registry_members():
    resolved, unknown_players, unknown_protocols = resolve_position_claims(
        REGISTRY,
        [
            PositionClaim(player="Cloudflare", protocol="Web Bot Auth", status="shipped"),
            PositionClaim(player="Akamai", protocol="AIPREF", status="stated"),
        ],
    )

    assert [(c.player_slug, c.protocol_slug, c.status) for c in resolved] == [
        ("cloudflare", "web-bot-auth", PositionStatus.SHIPPED),
        ("akamai", "aipref-vocab", PositionStatus.STATED),
    ]
    assert unknown_players == []
    assert unknown_protocols == []


def test_resolve_position_claims_resolves_a_bot_name_to_its_operator():
    resolved, _, _ = resolve_position_claims(
        REGISTRY, [PositionClaim(player="ClaudeBot", protocol="MCP", status="shipped")]
    )

    assert resolved[0].player_slug == "anthropic"


def test_resolve_position_claims_reports_out_of_vocabulary_names():
    resolved, unknown_players, unknown_protocols = resolve_position_claims(
        REGISTRY,
        [PositionClaim(player="Totally Unknown Inc", protocol="Imaginary", status="shipped")],
    )

    assert resolved == []
    assert unknown_players == ["Totally Unknown Inc"]
    assert unknown_protocols == ["Imaginary"]


def test_resolve_position_claims_drops_an_unknown_status():
    resolved, _, _ = resolve_position_claims(
        REGISTRY, [PositionClaim(player="Cloudflare", protocol="RSL", status="enthusiastic")]
    )

    assert resolved == []
```

Append to `tests/test_feed_writer.py`:

```python
def test_frontmatter_carries_position_claims(tmp_path, source, analysis):
    from pipeline.analyzer import ResolvedPositionClaim
    from pipeline.positions import PositionStatus

    analysis.position_claims = [
        ResolvedPositionClaim(
            player_slug="cloudflare",
            protocol_slug="web-bot-auth",
            status=PositionStatus.SHIPPED,
        )
    ]

    frontmatter = _written(tmp_path, source, analysis)

    assert frontmatter["position_claims"] == [
        {"player": "cloudflare", "protocol": "web-bot-auth", "status": "shipped"}
    ]


def test_frontmatter_omits_position_claims_when_empty(tmp_path, source, analysis):
    frontmatter = _written(tmp_path, source, analysis)

    assert "position_claims" not in frontmatter
```

`_written`, `source` and `analysis` are the existing helpers in that file.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_analyzer.py tests/test_feed_writer.py -v`
Expected: FAIL — `ImportError: cannot import name 'PositionClaim' from 'pipeline.analyzer'`

- [ ] **Step 3: Add the models and the resolver**

In `pipeline/analyzer.py`, extend the imports:

```python
from pipeline.positions import PositionStatus
```

Add the two models at module level, above `AnalyzerResponse`:

```python
class PositionClaim(BaseModel):
    """What the model says a development implies, before resolution."""

    player: str
    protocol: str
    status: str


class ResolvedPositionClaim(BaseModel):
    """A claim whose names resolved to registry slugs and whose status is valid."""

    player_slug: str
    protocol_slug: str
    status: PositionStatus
```

Add `position_claims` to `AnalyzerResponse`, after `protocols`:

```python
    position_claims: list[PositionClaim] = Field(default_factory=list)
```

Add it to `AnalysisResult`, after `protocols`:

```python
    position_claims: list[ResolvedPositionClaim] = Field(default_factory=list)
```

Add the resolver at module level:

```python
def resolve_position_claims(
    registry: EntityRegistry,
    claims: list[PositionClaim],
) -> tuple[list[ResolvedPositionClaim], list[str], list[str]]:
    """Resolve claim names to registry slugs and validate the status.

    A claim survives only when both names resolve and the status is one of the
    five published values. Everything else is reported for review rather than
    guessed at — a wrong cell is a factual error on a published matrix.
    """
    resolved: list[ResolvedPositionClaim] = []
    unknown_players: list[str] = []
    unknown_protocols: list[str] = []

    for claim in claims:
        player_slug = registry.resolve_player(claim.player)
        protocol_slug = registry.resolve_protocol(claim.protocol)
        if player_slug is None:
            unknown_players.append(claim.player)
        if protocol_slug is None:
            unknown_protocols.append(claim.protocol)
        if player_slug is None or protocol_slug is None:
            continue
        try:
            status = PositionStatus(claim.status.strip().lower())
        except ValueError:
            continue
        resolved.append(
            ResolvedPositionClaim(
                player_slug=player_slug, protocol_slug=protocol_slug, status=status
            )
        )

    return resolved, unknown_players, unknown_protocols
```

- [ ] **Step 4: Extend the system instruction and wire the resolver in**

Find the system instruction in `analyze_change` — the string that already tells the model about `subject` and `protocols` — and append:

```python
    "When the evidence states a named company's position on a named protocol, "
    "add it to `position_claims` with `status` one of: shipped (in production), "
    "preview (limited or beta), stated (publicly committed but not shipped), "
    "declined (publicly refused or rejected). Omit the claim entirely when the "
    "evidence does not say. Never infer `declined` from silence — it requires an "
    "explicit public refusal."
```

In `analyze_change`, after the existing `resolve_entities(...)` call, add:

```python
    claims, claim_unknown_players, claim_unknown_protocols = resolve_position_claims(
        _registry(), raw.position_claims
    )
```

Then merge the unknowns into the lists already being returned on the result, and pass the claims through:

```python
        unknown_players=list(dict.fromkeys([*unknown_players, *claim_unknown_players])),
        unknown_protocols=list(dict.fromkeys([*unknown_protocols, *claim_unknown_protocols])),
        position_claims=claims,
```

The existing `record_candidates` call site in `check.py` then queues claim-derived unknowns too, with no change there.

- [ ] **Step 5: Persist the claims to frontmatter**

In `pipeline/feed_writer.py`, add a mapping-list helper beside `_yaml_list`:

```python
def _yaml_claims(claims) -> str:
    return "".join(
        f'  - player: "{claim.player_slug}"\n'
        f'    protocol: "{claim.protocol_slug}"\n'
        f'    status: {claim.status.value}\n'
        for claim in claims
    )
```

Then, beside the existing conditional `players` / `protocols` appends:

```python
    if analysis.position_claims:
        frontmatter += f"position_claims:\n{_yaml_claims(analysis.position_claims)}"
```

- [ ] **Step 6: Confirm the site still builds with the new frontmatter key**

The Astro feed schema is `z.object({...}).superRefine(...)`, and a zod object strips unknown keys rather than erroring — but verify rather than assume, because a `.strict()` anywhere would fail the build:

```bash
cd site && npm run check && npm run build
```

Expected: clean. If the build rejects the unknown key, add `position_claims` as an optional field to the feed collection schema in `site/src/content.config.ts` and say so in your report.

- [ ] **Step 7: Run everything and commit**

Run: `uv run pytest -q && uv run ruff check pipeline tests`
Expected: all pass (172 before this task, plus your new tests).

```bash
git add pipeline/analyzer.py pipeline/feed_writer.py tests/test_analyzer.py tests/test_feed_writer.py
git commit -m "feat: have analysis state the position a development implies

The proposal stage needs a per-pair status, and deciding between shipped,
preview, stated and declined from prose is a judgement. The analyzer
already holds the evidence and already emits controlled entity slugs, so
it states the claim; the proposal stage stays a pure comparison that
cannot fail from a model error. Unresolvable names and invalid statuses
are reported for review rather than guessed at."
```

---

### Task 3: The proposal stage

**Files:**
- Create: `pipeline/map_proposals.py`
- Test: `tests/test_map_proposals.py`

**Interfaces:**
- Consumes: `load_positions`, `PositionStatus`, `EvidenceLevel`, `may_change`, `position_key` from `pipeline.positions`
- Produces:
  - `Proposal` — pydantic model: `player_slug`, `protocol_slug`, `from_status: PositionStatus`, `to_status: PositionStatus`, `evidence_level: EvidenceLevel`, `since: str`, `source_urls: list[str]`, `supporting_development_slug: str`, `feed_slug: str`, `proposed_by: str`
  - `evidence_level_for(source_tier: str) -> EvidenceLevel`
  - `collect_proposals(feed_records, registry, *, run_id) -> list[Proposal]`
  - `save_proposals(proposals_dir: Path, proposals: list[Proposal], *, date_str: str) -> list[Path]`
  - `FeedRecord` — the minimal shape the stage reads: `slug`, `status`, `source_tier`, `source_urls`, `event_date`, `development_slug`, `position_claims`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_map_proposals.py`:

```python
import json
from datetime import UTC, datetime
from pathlib import Path

from pipeline.map_proposals import (
    FeedRecord,
    collect_proposals,
    evidence_level_for,
    save_proposals,
)
from pipeline.positions import (
    EvidenceLevel,
    Position,
    PositionRegistry,
    PositionStatus,
)

NOW = datetime(2026, 10, 17, 8, 0, tzinfo=UTC)


def _record(**overrides) -> FeedRecord:
    base = dict(
        slug="cloudflare-signs-bots",
        status="verified",
        source_tier="primary",
        source_urls=["https://blog.cloudflare.com/web-bot-auth"],
        event_date="2026-07-11",
        development_slug="cloudflare-signs-bots",
        position_claims=[
            {"player": "cloudflare", "protocol": "web-bot-auth", "status": "shipped"}
        ],
    )
    base.update(overrides)
    return FeedRecord(**base)


def test_a_verified_primary_record_proposes_a_change_from_none():
    proposals = collect_proposals([_record()], PositionRegistry(), run_id="run-1")

    assert len(proposals) == 1
    p = proposals[0]
    assert (p.player_slug, p.protocol_slug) == ("cloudflare", "web-bot-auth")
    assert p.from_status is PositionStatus.NONE
    assert p.to_status is PositionStatus.SHIPPED
    assert p.evidence_level is EvidenceLevel.PRIMARY
    assert p.since == "2026-07-11"
    assert p.supporting_development_slug == "cloudflare-signs-bots"
    assert p.proposed_by == "run-1"


def test_reported_and_signal_records_never_propose():
    for status in ("reported", "signal"):
        proposals = collect_proposals([_record(status=status)], PositionRegistry(), run_id="r")
        assert proposals == [], status


def test_a_non_primary_tier_never_proposes():
    for tier in ("specialist", "commentary"):
        proposals = collect_proposals(
            [_record(source_tier=tier)], PositionRegistry(), run_id="r"
        )
        assert proposals == [], tier


def test_a_claim_matching_merged_state_proposes_nothing():
    merged = PositionRegistry(
        positions=[
            Position(
                player_slug="cloudflare",
                protocol_slug="web-bot-auth",
                status=PositionStatus.SHIPPED,
                since="2026-07-11",
                last_changed_at=NOW,
                evidence_level=EvidenceLevel.PRIMARY,
            )
        ]
    )

    assert collect_proposals([_record()], merged, run_id="r") == []


def test_a_claim_that_moves_an_existing_position_carries_the_previous_status():
    merged = PositionRegistry(
        positions=[
            Position(
                player_slug="cloudflare",
                protocol_slug="web-bot-auth",
                status=PositionStatus.PREVIEW,
                since="2026-05-01",
                last_changed_at=NOW,
                evidence_level=EvidenceLevel.PRIMARY,
            )
        ]
    )

    proposals = collect_proposals([_record()], merged, run_id="r")

    assert proposals[0].from_status is PositionStatus.PREVIEW
    assert proposals[0].to_status is PositionStatus.SHIPPED


def test_evidence_level_mapping():
    assert evidence_level_for("primary") is EvidenceLevel.PRIMARY
    assert evidence_level_for("measurement") is EvidenceLevel.PRIMARY
    assert evidence_level_for("specialist") is EvidenceLevel.SECONDARY
    assert evidence_level_for("commentary") is EvidenceLevel.SECONDARY


def test_save_proposals_writes_one_file_per_proposal_and_nothing_else(tmp_path):
    proposals = collect_proposals([_record()], PositionRegistry(), run_id="run-1")

    written = save_proposals(tmp_path, proposals, date_str="2026-10-17")

    assert [p.name for p in written] == ["2026-10-17-1.json"]
    payload = json.loads(written[0].read_text())
    assert payload["player_slug"] == "cloudflare"
    assert payload["to_status"] == "shipped"
    assert not (tmp_path / "positions.json").exists()


def test_save_proposals_writes_nothing_when_there_is_nothing_to_propose(tmp_path):
    assert save_proposals(tmp_path, [], date_str="2026-10-17") == []
    assert list(tmp_path.glob("*")) == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_map_proposals.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pipeline.map_proposals'`

- [ ] **Step 3: Write the module**

Create `pipeline/map_proposals.py`:

```python
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

from pipeline.positions import (
    EvidenceLevel,
    PositionRegistry,
    PositionStatus,
    may_change,
)

# Tiers the project treats as first-party factual evidence. `verified` status is
# already gated on these upstream; requiring the tier here too makes the
# invariant local and testable rather than inherited.
_PRIMARY_TIERS = {"primary", "measurement"}


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
    if source_tier.strip().lower() in _PRIMARY_TIERS:
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
    """Write one file per proposal. Writes nothing when there is nothing to say."""
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
```

- [ ] **Step 4: Run the tests and the linter**

Run: `uv run pytest tests/test_map_proposals.py -v && uv run ruff check pipeline tests`
Expected: all pass, no ruff findings.

- [ ] **Step 5: Commit**

```bash
git add pipeline/map_proposals.py tests/test_map_proposals.py
git commit -m "feat: add the proposal stage

Pure comparison, no model call: diff each verified primary record's
position claims against merged state and write proposals/ only. Reported
and signal grades propose nothing, and neither does a non-primary tier —
the invariant is enforced locally rather than inherited, so it is
testable. The stage cannot write data/positions.json."
```

---

### Task 4: Run the proposal stage from the daily check, without ever blocking publication

**Files:**
- Modify: `pipeline/check.py`
- Test: `tests/test_check.py`

**Interfaces:**
- Consumes: `collect_proposals`, `save_proposals`, `FeedRecord` from `pipeline.map_proposals`; `load_positions` from `pipeline.positions`; `Config.positions_path` / `.proposals_dir`
- Produces: a `map_proposals` key in the health payload: `{"status": "ok" | "failed" | "skipped", "proposed": int, "error": str}`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_check.py`, modelled on the existing `test_reported_item_writes_feed_without_development` (reuse its fixture setup and the `_material_analysis()` helper):

```python
async def test_proposal_stage_writes_proposals_without_touching_positions(repo):
    analysis = _material_analysis()
    from pipeline.analyzer import ResolvedPositionClaim
    from pipeline.positions import PositionStatus

    analysis.position_claims = [
        ResolvedPositionClaim(
            player_slug="cloudflare",
            protocol_slug="web-bot-auth",
            status=PositionStatus.SHIPPED,
        )
    ]

    # ... same run_check(...) invocation as the neighbouring test,
    # with analyze_change=AsyncMock(return_value=analysis)

    written = sorted((repo / "proposals").glob("*.json"))
    assert len(written) == 1
    assert not (repo / "data" / "positions.json").exists()


async def test_a_failing_proposal_stage_degrades_health_without_failing_the_publish(
    repo, monkeypatch
):
    def boom(*args, **kwargs):
        raise RuntimeError("proposal stage exploded")

    monkeypatch.setattr("pipeline.check.collect_proposals", boom)

    # ... same run_check(...) invocation

    health = json.loads((repo / "data" / "health.json").read_text())
    assert health["map_proposals"]["status"] == "failed"
    # publication still happened
    assert list((repo / "content" / "feed").glob("*.md"))
```

Add `import json` to the test file if it is not already imported.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_check.py -k proposal -v`
Expected: FAIL — the `proposals/` directory is never created and the health payload has no `map_proposals` key.

- [ ] **Step 3: Wire the stage in after publication**

In `pipeline/check.py`, add the imports:

```python
from pipeline.map_proposals import FeedRecord, collect_proposals, save_proposals
from pipeline.positions import load_positions
```

Then, in `run_check`, **after** the feed and development writes and after `save_evidence(...)` — the same placement rule the entity-candidate queueing already follows, so a failure here cannot mark a successful publish as failed — add:

```python
    map_proposals_payload: dict[str, object]
    try:
        merged = load_positions(cfg.positions_path)
        records = [
            FeedRecord(
                slug=item.slug,
                status=item.status,
                source_tier=item.source_tier,
                source_urls=item.source_urls,
                event_date=item.event_date,
                development_slug=item.development_slug,
                # ResolvedPositionClaim uses *_slug field names; FeedRecord mirrors
                # the frontmatter shape. Convert rather than renaming either —
                # the frontmatter keys are already written to content/feed.
                position_claims=[
                    {
                        "player": claim.player_slug,
                        "protocol": claim.protocol_slug,
                        "status": claim.status.value,
                    }
                    for claim in item.position_claims
                ],
            )
            for item in published_this_run
        ]
        proposals = collect_proposals(records, merged, run_id=run_id)
        written = save_proposals(cfg.proposals_dir, proposals, date_str=now.date().isoformat())
        map_proposals_payload = {"status": "ok", "proposed": len(written)}
    except Exception as error:  # noqa: BLE001 - non-required stage, must never block
        log.exception("map proposal stage failed")
        map_proposals_payload = {"status": "failed", "proposed": 0, "error": str(error)}
```

`published_this_run` is whatever local list the function already uses to track the records it wrote this run; read the surrounding code and use the real name, carrying `slug`, `status`, `source_tier`, `source_urls`, `event_date`, `development_slug` and `position_claims` from each. If no such list exists, build one as you write each feed item. `run_id` likewise: use the identifier the run already has, or `now.isoformat()` if there is none, and say which in your report.

Then add the payload to the health dict beside the existing `daily_brief` and `insight_threads` keys.

- [ ] **Step 4: Confirm the stage is not required for coverage**

`build_run_health` in `pipeline/health.py` degrades on `required_failed`, `core_failed`, a low `completion_ratio`, or `discovery_failed`. Read it and confirm none of those consume the `map_proposals` key — the payload is reported, not graded. State in your report that you checked, and quote the branch conditions.

- [ ] **Step 5: Run everything and commit**

Run: `uv run pytest -q && uv run ruff check pipeline tests`
Expected: all pass.

```bash
git add pipeline/check.py tests/test_check.py
git commit -m "feat: run the proposal stage from the daily check

Placed after save_evidence so a proposal failure cannot mark a successful
publish as analysis-failed, and wrapped so it degrades the health payload
instead of raising. The stage reports into health but is not graded by it:
required coverage for the feed does not include map proposals."
```

---

### Task 5: Proposals become one long-lived pull request

**Files:**
- Create: `.github/workflows/map-proposals.yml`

**Interfaces:**
- Consumes: `proposals/*.json` written by Task 4
- Produces: a single pull request from branch `map/proposals` into the default branch

- [ ] **Step 1: Write the workflow**

Create `.github/workflows/map-proposals.yml`, following the shape of the existing `weekly-reading.yml` (checkout, `astral-sh/setup-uv@v3`, then steps):

```yaml
name: Map Proposals

on:
  workflow_run:
    workflows: ["Daily Check"]
    types: [completed]
  workflow_dispatch: {}

permissions:
  contents: write
  pull-requests: write

concurrency:
  group: map-proposals
  cancel-in-progress: false

jobs:
  propose:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Stop if there is nothing to propose
        id: check
        run: |
          if [ -z "$(ls -A proposals 2>/dev/null)" ]; then
            echo "empty=true" >> "$GITHUB_OUTPUT"
          else
            echo "empty=false" >> "$GITHUB_OUTPUT"
          fi

      - name: Apply proposals onto the map/proposals branch
        if: steps.check.outputs.empty == 'false'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          COUNT=$(ls proposals/*.json | wc -l | tr -d ' ')
          # Render the body BEFORE applying: apply drains the queue, so a body
          # rendered afterwards would describe nothing.
          uv run python -m pipeline.apply_proposals --body > /tmp/pr-body.md
          # Rebuild the branch from main every run. The branch is derived state:
          # positions.json on it is a function of main plus the pending queue, so
          # branching from the previous map/proposals would accumulate stale
          # cells that main has already moved on from.
          git fetch origin main
          git checkout -B map/proposals origin/main
          uv run python -m pipeline.apply_proposals
          git add -A data/positions.json proposals
          git commit -m "map: apply ${COUNT} proposal(s)" || exit 0
          git push -f origin map/proposals

      - name: Open or update the pull request
        if: steps.check.outputs.empty == 'false'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          if gh pr view map/proposals --json number >/dev/null 2>&1; then
            gh pr edit map/proposals --body-file /tmp/pr-body.md
          else
            gh pr create --base main --head map/proposals \
              --title "Map proposals: position changes awaiting review" \
              --body-file /tmp/pr-body.md
          fi
```

- [ ] **Step 2: Write the applier the workflow calls**

The workflow needs a module that applies proposals to `positions.json` **inside the branch** (which is a human-reviewed pull request, so this is the merge path, not the pipeline writing published state) and renders the pull request body. Create `pipeline/apply_proposals.py`:

```python
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
```

- [ ] **Step 3: Test the applier and the body renderer**

Create `tests/test_apply_proposals.py`:

```python
from pathlib import Path

from pipeline.apply_proposals import apply, load_pending, render_body
from pipeline.map_proposals import Proposal
from pipeline.positions import EvidenceLevel, PositionStatus, load_positions


def _proposal(**overrides) -> Proposal:
    base = dict(
        player_slug="akamai",
        protocol_slug="aipref-vocab",
        from_status=PositionStatus.NONE,
        to_status=PositionStatus.STATED,
        evidence_level=EvidenceLevel.PRIMARY,
        since="2026-10-08",
        source_urls=["https://techdocs.akamai.com/aipref"],
        supporting_development_slug="akamai-aipref",
        feed_slug="akamai-aipref",
        proposed_by="run-1",
    )
    base.update(overrides)
    return Proposal(**base)


def test_apply_creates_a_position_and_records_the_previous_status(tmp_path):
    path = tmp_path / "positions.json"

    # proposals_dir=None: never let a test delete the repository's real queue.
    assert apply([_proposal()], path, proposals_dir=None) == 1

    position = load_positions(path).get("akamai", "aipref-vocab")
    assert position.status is PositionStatus.STATED
    assert position.previous_status is PositionStatus.NONE
    assert position.supporting_development_slugs == ["akamai-aipref"]
    assert position.merged_at is None


def test_apply_replaces_rather_than_duplicating_an_existing_cell(tmp_path):
    path = tmp_path / "positions.json"
    apply([_proposal()], path, proposals_dir=None)

    apply(
        [_proposal(from_status=PositionStatus.STATED, to_status=PositionStatus.SHIPPED)],
        path,
        proposals_dir=None,
    )

    registry = load_positions(path)
    assert len(registry.positions) == 1
    assert registry.get("akamai", "aipref-vocab").status is PositionStatus.SHIPPED


def test_apply_drains_the_queue_so_nothing_is_proposed_twice(tmp_path):
    queue = tmp_path / "proposals"
    queue.mkdir()
    (queue / "2026-10-17-1.json").write_text(_proposal().model_dump_json())

    apply(load_pending(queue), tmp_path / "positions.json", proposals_dir=queue)

    assert list(queue.glob("*.json")) == []


def test_load_pending_reads_every_proposal_file(tmp_path):
    (tmp_path / "2026-10-17-1.json").write_text(_proposal().model_dump_json())
    (tmp_path / "2026-10-17-2.json").write_text(
        _proposal(protocol_slug="rsl").model_dump_json()
    )

    assert len(load_pending(tmp_path)) == 2


def test_render_body_names_the_cell_the_transition_and_the_evidence():
    body = render_body([_proposal()])

    assert "akamai×aipref-vocab" in body
    assert "`none` → `stated`" in body
    assert "https://techdocs.akamai.com/aipref" in body
    assert "effective 2026-10-08" in body
```

- [ ] **Step 4: Run the tests, lint the workflow, and commit**

Run: `uv run pytest tests/test_apply_proposals.py -v && uv run ruff check pipeline tests`
Expected: all pass.

Then confirm the workflow YAML parses:

```bash
uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/map-proposals.yml')); print('ok')"
```

```bash
git add .github/workflows/map-proposals.yml pipeline/apply_proposals.py tests/test_apply_proposals.py
git commit -m "feat: turn proposals into one long-lived pull request

The workflow maintains a single map/proposals branch and one open PR,
updating it rather than opening a PR per change. apply_proposals runs only
inside that branch, so data/positions.json on the default branch still
changes exclusively through a human merge. The PR body renders each change
as cell, transition, effective date and evidence links."
```

---

### Task 6: The weekly reading layer

**Files:**
- Create: `pipeline/readings.py`
- Test: `tests/test_readings.py`

**Interfaces:**
- Consumes: `load_positions`, `PositionRegistry` from `pipeline.positions`; `StructuredModel` from `pipeline.model_provider`
- Produces:
  - `Reading` — pydantic model: `subject_kind: Literal["protocol", "front"]`, `subject_slug: str`, `stance: str`, `adoption_shape: str`, `new_entrants: str`, `watch_for: str`, `built_from: list[str]`, `development_count: int`, `generated_at: datetime`, `merged_at: datetime | None`
  - `ReadingResponse` — the model's raw reply: `stance`, `adoption_shape`, `new_entrants`, `watch_for`
  - `build_reading(model, *, subject_kind, subject_slug, developments) -> Reading | None`
  - `save_reading(readings_dir: Path, reading: Reading) -> Path` → `protocol-<slug>.json` / `front-<slug>.json`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_readings.py`:

```python
import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.readings import Reading, ReadingResponse, build_reading, save_reading

NOW = datetime(2026, 10, 17, 8, 0, tzinfo=UTC)


@pytest.fixture
def fake_model():
    model = MagicMock()
    model.generate = AsyncMock(
        return_value=ReadingResponse(
            stance="A2A is moving from message format to delegated authority.",
            adoption_shape="Only platform operators have shipped; defenders are absent.",
            new_entrants="Payment networks arrived this quarter via the authorisation layer.",
            watch_for="Whether defenders propose an observability extension within six months.",
        )
    )
    return model


async def test_build_reading_carries_provenance(fake_model):
    reading = await build_reading(
        fake_model,
        subject_kind="protocol",
        subject_slug="a2a",
        developments=["visa-ap2-credentials", "google-a2a-registry"],
        now=NOW,
    )

    assert reading.subject_kind == "protocol"
    assert reading.subject_slug == "a2a"
    assert reading.built_from == ["visa-ap2-credentials", "google-a2a-registry"]
    assert reading.development_count == 2
    assert reading.generated_at == NOW
    assert reading.merged_at is None
    assert reading.stance.startswith("A2A is moving")


async def test_build_reading_returns_none_with_no_developments(fake_model):
    reading = await build_reading(
        fake_model, subject_kind="protocol", subject_slug="x402", developments=[], now=NOW
    )

    assert reading is None
    fake_model.generate.assert_not_called()


def test_save_reading_names_the_file_by_kind_and_slug(tmp_path):
    reading = Reading(
        subject_kind="front",
        subject_slug="agents-identity",
        stance="s",
        adoption_shape="a",
        new_entrants="n",
        watch_for="w",
        built_from=["one"],
        development_count=1,
        generated_at=NOW,
    )

    path = save_reading(tmp_path, reading)

    assert path.name == "front-agents-identity.json"
    assert json.loads(path.read_text())["subject_slug"] == "agents-identity"
    assert list(tmp_path.glob("*.tmp")) == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_readings.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pipeline.readings'`

- [ ] **Step 3: Write the module**

Create `pipeline/readings.py`:

```python
"""The qualitative reading layer.

Coloured cells state facts and answer nothing; a reading attaches an editorial
judgement to one axis of the map. The three angles are fixed on purpose —
free-form commentary is hard to generate consistently and harder to keep honest.

Cadence is weekly, aligned with Weekly Intelligence. Like positions, readings
reach `data/readings/` only through a merged pull request: a wrong cell is a
visible factual error, a wrong reading is a judgement error that costs
credibility.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from pipeline.model_provider import StructuredModel

SubjectKind = Literal["protocol", "front"]

_SYSTEM = (
    "You write one short editorial reading of a protocol or front in an "
    "intelligence publication about AI crawlers and agents. Answer exactly three "
    "angles and one stance sentence. `adoption_shape`: what the pattern of "
    "positions means — who moved, who did not, and why that grouping matters. "
    "`new_entrants`: who arrived recently and what they are trying to control. "
    "`watch_for`: the one thing whose presence or absence in the next months "
    "would change the read. Ground every sentence in the developments supplied; "
    "never speculate beyond them."
)


class ReadingResponse(BaseModel):
    stance: str
    adoption_shape: str
    new_entrants: str
    watch_for: str


class Reading(BaseModel):
    subject_kind: SubjectKind
    subject_slug: str
    stance: str
    adoption_shape: str
    new_entrants: str
    watch_for: str
    built_from: list[str] = Field(default_factory=list)
    development_count: int = 0
    generated_at: datetime
    # Set by the human merge, never by the pipeline.
    merged_at: datetime | None = None


async def build_reading(
    model: StructuredModel,
    *,
    subject_kind: SubjectKind,
    subject_slug: str,
    developments: list[str],
    now: datetime,
) -> Reading | None:
    """Generate one reading, or None when there is nothing to read from.

    A subject with no developments in the window is skipped rather than given an
    invented reading.
    """
    if not developments:
        return None
    raw = await model.generate(
        response_model=ReadingResponse,
        system_instruction=_SYSTEM,
        prompt=f"{subject_kind}: {subject_slug}\ndevelopments:\n"
        + "\n".join(f"- {slug}" for slug in developments),
    )
    return Reading(
        subject_kind=subject_kind,
        subject_slug=subject_slug,
        stance=raw.stance.strip(),
        adoption_shape=raw.adoption_shape.strip(),
        new_entrants=raw.new_entrants.strip(),
        watch_for=raw.watch_for.strip(),
        built_from=list(developments),
        development_count=len(developments),
        generated_at=now,
    )


def save_reading(readings_dir: Path, reading: Reading) -> Path:
    """Write one reading atomically as `<kind>-<slug>.json`."""
    readings_dir.mkdir(parents=True, exist_ok=True)
    path = readings_dir / f"{reading.subject_kind}-{reading.subject_slug}.json"
    payload = json.dumps(reading.model_dump(mode="json"), indent=2, ensure_ascii=False)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload + "\n")
    os.replace(temporary, path)
    return path
```

- [ ] **Step 4: Run the tests and commit**

Run: `uv run pytest tests/test_readings.py -v && uv run ruff check pipeline tests`
Expected: all pass.

```bash
git add pipeline/readings.py tests/test_readings.py
git commit -m "feat: add the weekly reading layer

One stance sentence plus three fixed angles per protocol and front, with
built_from provenance and a development count. A subject with no
developments in the window is skipped rather than given an invented
reading, and merged_at stays optional so the pipeline can never set it."
```

---

### Task 7: The seeding harness

Spec §5 gives the matrix no bootstrap path: positions only appear as verified developments arrive and are merged. Measured on the current corpus, **5 of 54 feed records carry entity links and exactly 1 carries a protocol**, so without seeding the matrix stays empty for months and sub-project 3b would ship a blank grid.

**This task builds the mechanism, not the data.** Filling the seed needs one verified primary source URL per cell, which is a research pass, not an implementation step. A validator that refuses an unsourced row is what makes that pass safe to do later — and what stops a well-meaning future session from pasting in remembered adoption facts.

**Files:**
- Create: `data/positions.seed.yaml`
- Create: `scripts/validate_seed.py`
- Test: `tests/test_validate_seed.py`

**Interfaces:**
- Consumes: `load_registry` from `pipeline.entities`; `PositionStatus` from `pipeline.positions`
- Produces:
  - `SeedRow` — `player`, `protocol`, `status`, `since`, `source_url`, `note`
  - `validate_seed(rows, registry) -> list[str]` returning human-readable errors, empty when valid
  - `seed_to_registry(rows, registry) -> PositionRegistry`
  - `scripts/validate_seed.py` as a CLI exiting non-zero on any error

- [ ] **Step 1: Write the seed file with its contract in a header comment**

Create `data/positions.seed.yaml`:

```yaml
# Human-authored seed for data/positions.json.
#
# Every row needs a PRIMARY source URL and the date the status took effect in
# the world. `scripts/validate_seed.py` refuses a row without them, and refuses
# a player or protocol that is not in entities/*.yaml — the registries are the
# controlled vocabulary and the seed cannot grow them.
#
# `declined` requires an explicit public refusal in the source. Never record
# `declined` because a player is silent; absence is `none`, which is simply not
# written here.
#
# This file is applied by hand, reviewed like any other change. It is empty of
# rows on purpose: populating it is a research pass with one source per cell,
# not an implementation step.
rows: []
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_validate_seed.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.entities import load_registry  # noqa: E402
from pipeline.positions import PositionStatus  # noqa: E402
from scripts.validate_seed import SeedRow, seed_to_registry, validate_seed  # noqa: E402

REGISTRY = load_registry()


def _row(**overrides) -> dict:
    base = dict(
        player="Cloudflare",
        protocol="Web Bot Auth",
        status="shipped",
        since="2026-07-11",
        source_url="https://blog.cloudflare.com/web-bot-auth",
        note="",
    )
    base.update(overrides)
    return base


def test_a_complete_row_validates():
    assert validate_seed([SeedRow(**_row())], REGISTRY) == []


def test_a_row_without_a_source_url_is_refused():
    errors = validate_seed([SeedRow(**_row(source_url=""))], REGISTRY)

    assert any("source_url" in e for e in errors)


def test_a_row_without_a_since_date_is_refused():
    errors = validate_seed([SeedRow(**_row(since=""))], REGISTRY)

    assert any("since" in e for e in errors)


def test_a_player_outside_the_registry_is_refused():
    errors = validate_seed([SeedRow(**_row(player="Totally Unknown Inc"))], REGISTRY)

    assert any("Totally Unknown Inc" in e for e in errors)


def test_a_protocol_outside_the_registry_is_refused():
    errors = validate_seed([SeedRow(**_row(protocol="Imaginary Protocol"))], REGISTRY)

    assert any("Imaginary Protocol" in e for e in errors)


def test_an_unknown_status_is_refused():
    errors = validate_seed([SeedRow(**_row(status="enthusiastic"))], REGISTRY)

    assert any("enthusiastic" in e for e in errors)


def test_status_none_is_refused_because_absence_is_not_recorded():
    errors = validate_seed([SeedRow(**_row(status="none"))], REGISTRY)

    assert any("none" in e for e in errors)


def test_a_bot_name_resolves_to_its_operator():
    rows = [SeedRow(**_row(player="ClaudeBot", protocol="MCP"))]

    assert validate_seed(rows, REGISTRY) == []
    registry = seed_to_registry(rows, REGISTRY)
    assert registry.get("anthropic", "mcp").status is PositionStatus.SHIPPED


def test_the_shipped_seed_file_is_valid():
    import yaml

    raw = yaml.safe_load(Path("data/positions.seed.yaml").read_text()) or {}
    rows = [SeedRow(**row) for row in (raw.get("rows") or [])]

    assert validate_seed(rows, REGISTRY) == []
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/test_validate_seed.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.validate_seed'`

- [ ] **Step 4: Write the validator**

Create `scripts/__init__.py` as an empty file so the test can import the module, then create `scripts/validate_seed.py`:

```python
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

import yaml
from pydantic import BaseModel

from pipeline.entities import EntityRegistry, load_registry
from pipeline.positions import EvidenceLevel, Position, PositionRegistry, PositionStatus

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
```

- [ ] **Step 5: Run the tests and the CLI, then commit**

Run: `uv run pytest tests/test_validate_seed.py -v && uv run ruff check pipeline tests scripts`
Expected: all pass.

Run the CLI against the shipped empty seed:

```bash
uv run python scripts/validate_seed.py
```
Expected: `Seed is applicable: 0 row(s), every cell sourced and dated.`

Then prove the gate bites — add one unsourced row to a scratch copy, point the CLI at it, and confirm it exits 1 naming the missing `source_url`. Paste both outcomes into your report.

```bash
git add data/positions.seed.yaml scripts/__init__.py scripts/validate_seed.py tests/test_validate_seed.py
git commit -m "feat: add the position seeding harness

The matrix has no bootstrap path in the spec: positions only appear as
verified developments arrive. With 5 of 54 records carrying entity links
and one carrying a protocol, the grid would stay empty for months. This
adds the seed format and a validator that refuses any row without a
primary source URL, an effective date, and registry-resolvable names, and
refuses 'none' because an absent cell already reads none. The seed ships
with no rows: filling it is a research pass, one source per cell."
```

---

### Task 8: Run the readings weekly, on their own review branch

Task 6 builds `pipeline/readings.py` but nothing calls it, so spec §6 is not yet
implemented. This task adds the runner and the gate.

**Readings get their own branch `map/readings`, not `map/proposals`.** §6 says
readings pass "the same pull request gate as positions" — the same *gate*, which
is human review. They cannot share the same *branch*: Task 5's workflow rebuilds
`map/proposals` from `origin/main` on every daily run, so any reading sitting
there would be destroyed within a day. Two long-lived branches, two open pull
requests, one gate each.

**Files:**
- Create: `pipeline/weekly_readings.py`
- Create: `.github/workflows/map-readings.yml`
- Test: `tests/test_weekly_readings.py`

**Interfaces:**
- Consumes: `Reading`, `build_reading`, `save_reading` from `pipeline.readings`; `completed_iso_window` from `pipeline.weekly_intelligence`; `FRONT_TRACKS`, `Front`, `Track`, `resolve_track` from `pipeline.taxonomy`
- Produces:
  - `WindowRecord` — `slug`, `status`, `event_date`, `protocols: list[str]`, `tracks: list[str]`
  - `front_for_track(track: Track) -> Front | None` — derived by inverting `FRONT_TRACKS`
  - `group_by_protocol(records) -> dict[str, list[str]]`
  - `group_by_front(records) -> dict[str, list[str]]`
  - `render_body(readings: list[Reading]) -> str`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_weekly_readings.py`:

```python
from pipeline.taxonomy import Front, Track
from pipeline.weekly_readings import (
    WindowRecord,
    front_for_track,
    group_by_front,
    group_by_protocol,
    render_body,
)


def _record(**overrides) -> WindowRecord:
    base = dict(
        slug="cloudflare-signs-bots",
        status="verified",
        event_date="2026-10-13",
        protocols=["web-bot-auth"],
        tracks=["identity-authorization"],
    )
    base.update(overrides)
    return WindowRecord(**base)


def test_front_for_track_inverts_the_rollup_table():
    assert front_for_track(Track.IDENTITY_AUTHORIZATION) is Front.AGENTS_IDENTITY
    assert front_for_track(Track.LITIGATION_LEGAL) is Front.GOVERNANCE_LAW
    assert front_for_track(Track.MEASUREMENT_ECONOMICS) is Front.MEASUREMENT_ECONOMICS


def test_group_by_protocol_collects_development_slugs():
    records = [
        _record(),
        _record(slug="akamai-aipref", protocols=["web-bot-auth", "aipref-vocab"]),
    ]

    grouped = group_by_protocol(records)

    assert grouped["web-bot-auth"] == ["cloudflare-signs-bots", "akamai-aipref"]
    assert grouped["aipref-vocab"] == ["akamai-aipref"]


def test_grouping_ignores_records_that_are_not_verified():
    records = [_record(status="reported"), _record(slug="sig", status="signal")]

    assert group_by_protocol(records) == {}
    assert group_by_front(records) == {}


def test_group_by_front_uses_the_track_rollup_and_resolves_legacy_slugs():
    records = [_record(tracks=["agentic-web"])]

    grouped = group_by_front(records)

    assert grouped["agents-identity"] == ["cloudflare-signs-bots"]


def test_a_record_with_no_protocols_still_counts_toward_its_front():
    records = [_record(protocols=[])]

    assert group_by_protocol(records) == {}
    assert group_by_front(records)["agents-identity"] == ["cloudflare-signs-bots"]


def test_render_body_names_each_subject_and_its_development_count():
    from datetime import UTC, datetime

    from pipeline.readings import Reading

    body = render_body(
        [
            Reading(
                subject_kind="protocol",
                subject_slug="web-bot-auth",
                stance="Verification is consolidating among defenders.",
                adoption_shape="a",
                new_entrants="n",
                watch_for="w",
                built_from=["cloudflare-signs-bots"],
                development_count=1,
                generated_at=datetime(2026, 10, 17, tzinfo=UTC),
            )
        ]
    )

    assert "protocol · web-bot-auth" in body
    assert "Verification is consolidating among defenders." in body
    assert "1 development" in body
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_weekly_readings.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pipeline.weekly_readings'`

- [ ] **Step 3: Write the runner**

Create `pipeline/weekly_readings.py`:

```python
"""Generate the week's readings and stage them for review.

Runs weekly, after Weekly Intelligence. Writes `data/readings/` only inside the
`map/readings` branch, whose contents reach the default branch exclusively
through a human merge — the same gate positions pass.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from pipeline.model_provider import StructuredModel
from pipeline.readings import Reading, build_reading, save_reading
from pipeline.taxonomy import FRONT_TRACKS, Front, Track, resolve_track
from pipeline.weekly_intelligence import completed_iso_window

FEED_DIR = Path("content/feed")
READINGS_DIR = Path("data/readings")

_FRONT_BY_TRACK: dict[Track, Front] = {
    track: front for front, tracks in FRONT_TRACKS.items() for track in tracks
}


class WindowRecord(BaseModel):
    """A feed record inside the reading window."""

    slug: str
    status: str
    event_date: str
    protocols: list[str] = Field(default_factory=list)
    tracks: list[str] = Field(default_factory=list)


def front_for_track(track: Track) -> Front | None:
    """Invert FRONT_TRACKS. Returns None for a track in no front."""
    return _FRONT_BY_TRACK.get(track)


def _verified(records: list[WindowRecord]) -> list[WindowRecord]:
    return [r for r in records if r.status.strip().lower() == "verified"]


def group_by_protocol(records: list[WindowRecord]) -> dict[str, list[str]]:
    """Development slugs per protocol, verified records only."""
    grouped: dict[str, list[str]] = {}
    for record in _verified(records):
        for protocol in record.protocols:
            grouped.setdefault(protocol, []).append(record.slug)
    return grouped


def group_by_front(records: list[WindowRecord]) -> dict[str, list[str]]:
    """Development slugs per front, verified records only.

    A record with no protocol still belongs to a front, so a front reading can
    speak about developments the protocol axis cannot see.
    """
    grouped: dict[str, list[str]] = {}
    for record in _verified(records):
        fronts: set[str] = set()
        for raw in record.tracks:
            front = front_for_track(resolve_track(raw))
            if front is not None:
                fronts.add(front.value)
        for front_slug in sorted(fronts):
            slugs = grouped.setdefault(front_slug, [])
            if record.slug not in slugs:
                slugs.append(record.slug)
    return grouped


def load_window_records(
    feed_dir: Path, window_start: str, window_end: str
) -> list[WindowRecord]:
    """Read feed frontmatter for records whose event_date is inside the window."""
    records: list[WindowRecord] = []
    for path in sorted(feed_dir.glob("*.md")):
        text = path.read_text()
        if not text.startswith("---"):
            continue
        _, _, rest = text.partition("---\n")
        raw_frontmatter, _, _ = rest.partition("\n---")
        data = yaml.safe_load(raw_frontmatter) or {}
        event_date = str(data.get("event_date", ""))[:10]
        if not (window_start <= event_date <= window_end):
            continue
        records.append(
            WindowRecord(
                slug=str(data.get("slug", path.stem)),
                status=str(data.get("status", "")),
                event_date=event_date,
                protocols=[str(p) for p in (data.get("protocols") or [])],
                tracks=[str(t) for t in (data.get("tracks") or [])],
            )
        )
    return records


def render_body(readings: list[Reading]) -> str:
    lines = [
        "Weekly readings generated from this week's verified developments.",
        "",
        "Each reading is one stance sentence plus three fixed angles. A wrong cell",
        "is a visible factual error; a wrong reading is a judgement error, so these",
        "are reviewed before they publish.",
        "",
        "This branch is rebuilt from `main` on every run — edit on `main` after merging.",
        "",
    ]
    for reading in readings:
        plural = "s" if reading.development_count != 1 else ""
        lines.append(f"### {reading.subject_kind} · {reading.subject_slug}")
        lines.append(f"_{reading.development_count} development{plural}_")
        lines.append("")
        lines.append(reading.stance)
        lines.append("")
        lines.append(f"- **Adoption shape:** {reading.adoption_shape}")
        lines.append(f"- **New entrants:** {reading.new_entrants}")
        lines.append(f"- **Watch for:** {reading.watch_for}")
        lines.append("")
    return "\n".join(lines) + "\n"


async def generate(
    model: StructuredModel,
    *,
    feed_dir: Path = FEED_DIR,
    readings_dir: Path = READINGS_DIR,
    now: datetime | None = None,
    write: bool = True,
) -> list[Reading]:
    """Build every reading the window supports, newest window first."""
    now = now or datetime.now(UTC)
    _, window_start, window_end = completed_iso_window(now)
    records = load_window_records(
        feed_dir, window_start.isoformat(), window_end.isoformat()
    )

    readings: list[Reading] = []
    for subject_kind, grouped in (
        ("protocol", group_by_protocol(records)),
        ("front", group_by_front(records)),
    ):
        for subject_slug, developments in sorted(grouped.items()):
            reading = await build_reading(
                model,
                subject_kind=subject_kind,
                subject_slug=subject_slug,
                developments=developments,
                now=now,
            )
            if reading is None:
                continue
            readings.append(reading)
            if write:
                save_reading(readings_dir, reading)
    return readings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--body",
        action="store_true",
        help="print the PR body for the readings already in data/readings",
    )
    args = parser.parse_args()

    if args.body:
        readings = [
            Reading.model_validate_json(path.read_text())
            for path in sorted(READINGS_DIR.glob("*.json"))
        ]
        print(render_body(readings), end="")
        return 0

    from pipeline.model_provider import GeminiStructuredModel

    readings = asyncio.run(generate(GeminiStructuredModel()))
    print(f"wrote {len(readings)} reading(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

If `GeminiStructuredModel()` does not construct without arguments, read how
`pipeline/check.py` builds its model and use the same construction here; say
which you used in your report.

- [ ] **Step 4: Write the workflow**

Create `.github/workflows/map-readings.yml`:

```yaml
name: Map Readings

on:
  schedule:
    - cron: "0 14 * * 1"   # Mondays at 14:00 UTC, after Weekly Intelligence
  workflow_dispatch: {}

permissions:
  contents: write
  pull-requests: write

concurrency:
  group: map-readings
  cancel-in-progress: false

jobs:
  readings:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: astral-sh/setup-uv@v3

      - run: uv sync

      - name: Generate readings onto the map/readings branch
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git fetch origin main
          git checkout -B map/readings origin/main
          uv run python -m pipeline.weekly_readings
          uv run python -m pipeline.weekly_readings --body > /tmp/readings-body.md
          git add -A data/readings
          git commit -m "map: weekly readings" || exit 0
          git push -f origin map/readings

      - name: Open or update the pull request
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          if [ ! -s /tmp/readings-body.md ]; then exit 0; fi
          if gh pr view map/readings --json number >/dev/null 2>&1; then
            gh pr edit map/readings --body-file /tmp/readings-body.md
          else
            gh pr create --base main --head map/readings \
              --title "Map readings: weekly qualitative reads awaiting review" \
              --body-file /tmp/readings-body.md
          fi
```

Here `--body` runs *after* generation, because readings are written to
`data/readings/` rather than drained from a queue — the opposite of the proposal
workflow, where the body must be rendered first.

- [ ] **Step 5: Run everything, check the YAML, and commit**

Run: `uv run pytest -q && uv run ruff check pipeline tests scripts`
Expected: all pass.

```bash
uv run python -c "import yaml; yaml.safe_load(open('.github/workflows/map-readings.yml')); print('ok')"
```

```bash
git add pipeline/weekly_readings.py .github/workflows/map-readings.yml tests/test_weekly_readings.py
git commit -m "feat: run the readings weekly on their own review branch

Task 6 built the reading layer but nothing called it, leaving spec §6
unimplemented. Readings get map/readings rather than map/proposals: the
daily proposal workflow rebuilds its branch from origin/main every run, so
a reading staged there would be destroyed within a day. Same gate — human
review — on two branches. Fronts group by the FRONT_TRACKS rollup with
legacy track slugs resolved, so a development with no protocol still
reaches a front reading."
```

---

## Verification

The sub-project is green when all of these pass from the repository root:

```bash
uv run pytest -q
uv run ruff check pipeline tests scripts
uv run python scripts/validate_seed.py
cd site && npm run check:tokens && npm run check && npm run build
```

Plus the invariants that no test can assert on its own:

```bash
# The pipeline must never write published map state.
grep -rn "save_positions\|save_reading" pipeline/ --include=*.py | grep -v __pycache__
```

Expected exactly four call sites, no others:

- `save_positions` — `pipeline/positions.py` (its definition) and `pipeline/apply_proposals.py`
- `save_reading` — `pipeline/readings.py` (its definition) and `pipeline/weekly_readings.py`

Both writers run only inside a review branch. **A hit in `check.py` is a design failure, not a style nit** — it would mean the daily pipeline writes published map state.

```bash
# A proposal run must leave published state alone.
git status --short data/positions.json data/readings/
```

Expected: nothing — the daily stage writes `proposals/` only.
