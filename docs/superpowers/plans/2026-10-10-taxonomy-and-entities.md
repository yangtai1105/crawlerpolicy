# Taxonomy and Entities Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the editorial taxonomy into two orthogonal axes and add controlled protocol/player registries, so that any domain can be expressed for crawlers or agents and every development can be joined to the entities it concerns.

**Architecture:** `pipeline/taxonomy.py` grows a renamed, subject-free `Track` enum plus a new `Subject` enum and an alias map that resolves pre-2026-10 slugs at read time, so the 62 existing content files are never rewritten. Two new YAML registries under `entities/` become the project's controlled vocabulary, loaded by a new `pipeline/entities.py`. The analyzer gains controlled extraction: it may only emit registry slugs, and anything it believes it saw outside the registries goes to a review queue that is the sole path by which the registries grow.

**Tech Stack:** Python 3.12, uv, pydantic v2, PyYAML, pytest, ruff (line-length 100, `E,F,I,UP,B,SIM`), Astro + zod for the site schema.

**Spec:** `docs/superpowers/specs/2026-10-10-agentic-map-layer-design.md`

## Global Constraints

- Python `>=3.12`; run everything through `uv run`.
- ruff: `line-length = 100`, `target-version = "py312"`, lint select `["E", "F", "I", "UP", "B", "SIM"]`.
- Existing content is never rewritten. The 62 files in `content/feed` and `content/events` that carry `crawler-controls` or `agentic-web` keep those slugs; both the Python loader and the Astro schema resolve them to canonical tracks at read time.
- `subject` is additive and defaults to `unknown`. Historical records are not backfilled.
- The pipeline never writes to `entities/protocols.yaml` or `entities/players.yaml`. Registry growth happens only through the candidate queue plus a human edit.
- Tests make no network calls. Model providers are stubbed, following the existing pattern in `tests/test_analyzer.py`.
- `legacy-events` content and loaders stay untouched.
- Commit after each task. Do not push.

## Deviation from the spec, decided during planning

Spec §4.3 says `actors` is promoted to controlled extraction with free text preserved in a new `actors_raw`. This plan instead **leaves `actors` exactly as it is** (free-text display names, already consistent across 62 files and already rendered by the site) and adds **two new controlled fields, `players` and `protocols`**, carrying registry slugs.

Rationale: it satisfies the same requirement — a controlled join key for the map, with nothing observed lost — while avoiding a field whose meaning changes between old and new records, and it leaves existing site code untouched. `actors` is already the raw field, so `actors_raw` would be redundant.

## File Structure

| File | Responsibility |
|---|---|
| `pipeline/taxonomy.py` (modify) | `Track` (10, subject-free), new `Subject`, `TRACK_ALIASES`, `resolve_track`, updated `FRONT_TRACKS` |
| `pipeline/sources.py` (modify) | Drop the dead `Pillar` enum; add `default_subject`; tolerate legacy track slugs in `sources.yaml` |
| `sources.yaml` (modify) | Rename the 30 legacy track occurrences to canonical slugs |
| `entities/protocols.yaml` (create) | Protocol registry — the matrix columns |
| `entities/players.yaml` (create) | Player registry — the matrix rows |
| `pipeline/entities.py` (create) | Registry models, loader, slug resolution by name/alias |
| `pipeline/entity_candidates.py` (create) | The review queue for entities seen outside the registries |
| `pipeline/analyzer.py` (modify) | Controlled extraction of `subject`, `players`, `protocols` with graceful fallback |
| `pipeline/feed_writer.py` (modify) | Emit the three new frontmatter fields |
| `site/src/lib/taxonomy.ts` (modify) | Canonical tracks, legacy aliases, `normalizeTrack`, labels, subjects |
| `site/src/content.config.ts` (modify) | Accept canonical + legacy track slugs; accept the new optional fields |
| `site/src/lib/sources.ts:59` (modify) | Replace the hardcoded `"crawler-controls"` filter |
| `tests/test_taxonomy.py` (modify) | Alias resolution, subject enum, front roll-up |
| `tests/test_entities.py` (create) | Registry loading, duplicate and alias collision rejection, resolution |
| `tests/test_entity_candidates.py` (create) | Queue merge, idempotency |
| `tests/test_analyzer.py` (modify) | Controlled extraction, unknown entities queued, fallbacks |
| `tests/test_feed_writer.py` (modify) | New frontmatter fields |

---

### Task 1: Two-axis taxonomy

Renames two tracks to remove subject words, adds the identity track, adds the `Subject` axis, and resolves legacy slugs so nothing on disk needs rewriting. The mechanical rename across `pipeline/` (7 occurrences) and `tests/` (61 occurrences) is part of this task because the suite does not pass until it is done.

**Files:**
- Modify: `pipeline/taxonomy.py`
- Modify: `pipeline/sources.py` (remove `Pillar`, add `default_subject`, add track-alias validator)
- Modify: `sources.yaml` (30 occurrences)
- Modify: `pipeline/check.py`, `pipeline/state_of_play.py`, `pipeline/analyzer.py` (enum references)
- Test: `tests/test_taxonomy.py`

**Interfaces:**
- Consumes: nothing (first task)
- Produces:
  - `Track` with members `POLICY_REGULATION`, `LITIGATION_LEGAL`, `SEARCH_DISCOVERY`, `ACCESS_CONTROLS`, `PLATFORM_ECOSYSTEM`, `IDENTITY_AUTHORIZATION`, `LICENSING_MONETIZATION`, `STANDARDS_PROTOCOLS`, `ASSET_RIGHTS`, `MEASUREMENT_ECONOMICS`
  - `Subject` with members `CRAWLER = "crawler"`, `AGENT = "agent"`, `BOTH = "both"`, `UNKNOWN = "unknown"`
  - `TRACK_ALIASES: dict[str, Track]`
  - `resolve_track(value: str) -> Track`
  - `Source.default_subject: Subject` (defaults to `Subject.UNKNOWN`)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_taxonomy.py`:

```python
from pipeline.taxonomy import TRACK_ALIASES, Subject, resolve_track


def test_resolve_track_accepts_canonical_slugs():
    assert resolve_track("access-controls") is Track.ACCESS_CONTROLS
    assert resolve_track("platform-ecosystem") is Track.PLATFORM_ECOSYSTEM
    assert resolve_track("identity-authorization") is Track.IDENTITY_AUTHORIZATION


def test_resolve_track_resolves_pre_october_2026_slugs():
    assert resolve_track("crawler-controls") is Track.ACCESS_CONTROLS
    assert resolve_track("agentic-web") is Track.PLATFORM_ECOSYSTEM
    assert set(TRACK_ALIASES) == {"crawler-controls", "agentic-web"}


def test_resolve_track_rejects_unknown_slugs():
    with pytest.raises(ValueError):
        resolve_track("not-a-track")


def test_track_slugs_carry_no_subject_words():
    for track in Track:
        assert "crawler" not in track.value
        assert "agent" not in track.value


def test_identity_authorization_rolls_up_to_agents_identity():
    assert Track.IDENTITY_AUTHORIZATION in FRONT_TRACKS[Front.AGENTS_IDENTITY]


def test_subject_axis_values():
    assert [subject.value for subject in Subject] == ["crawler", "agent", "both", "unknown"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_taxonomy.py -v`
Expected: FAIL — `ImportError: cannot import name 'TRACK_ALIASES' from 'pipeline.taxonomy'`

- [ ] **Step 3: Rewrite the taxonomy enums and alias map**

In `pipeline/taxonomy.py`, replace the `Track` class and add `Subject` plus the alias map:

```python
class Track(StrEnum):
    POLICY_REGULATION = "policy-regulation"
    LITIGATION_LEGAL = "litigation-legal"
    SEARCH_DISCOVERY = "search-discovery"
    ACCESS_CONTROLS = "access-controls"
    PLATFORM_ECOSYSTEM = "platform-ecosystem"
    IDENTITY_AUTHORIZATION = "identity-authorization"
    LICENSING_MONETIZATION = "licensing-monetization"
    STANDARDS_PROTOCOLS = "standards-protocols"
    ASSET_RIGHTS = "asset-rights"
    MEASUREMENT_ECONOMICS = "measurement-economics"


class Subject(StrEnum):
    """What a development is about, orthogonal to its domain Track."""

    CRAWLER = "crawler"
    AGENT = "agent"
    BOTH = "both"
    UNKNOWN = "unknown"


# Slugs used before 2026-10. Content on disk keeps them; readers resolve.
TRACK_ALIASES: dict[str, Track] = {
    "crawler-controls": Track.ACCESS_CONTROLS,
    "agentic-web": Track.PLATFORM_ECOSYSTEM,
}


def resolve_track(value: str) -> Track:
    """Resolve a track slug, including pre-2026-10 slugs, to a canonical Track."""
    alias = TRACK_ALIASES.get(value)
    if alias is not None:
        return alias
    return Track(value)
```

Then update `FRONT_TRACKS` so the two renamed tracks and the new one are placed:

```python
FRONT_TRACKS: dict[Front, tuple[Track, ...]] = {
    Front.ACCESS_DISCOVERY: (
        Track.ACCESS_CONTROLS,
        Track.SEARCH_DISCOVERY,
    ),
    Front.AGENTS_IDENTITY: (
        Track.PLATFORM_ECOSYSTEM,
        Track.STANDARDS_PROTOCOLS,
        Track.IDENTITY_AUTHORIZATION,
    ),
    Front.RIGHTS_MARKETS: (
        Track.LICENSING_MONETIZATION,
        Track.ASSET_RIGHTS,
    ),
    Front.GOVERNANCE_LAW: (
        Track.POLICY_REGULATION,
        Track.LITIGATION_LEGAL,
    ),
    Front.MEASUREMENT_ECONOMICS: (Track.MEASUREMENT_ECONOMICS,),
}
```

- [ ] **Step 4: Rename the enum references across the codebase**

```bash
cd ~/Documents/Claude/Skills/ai-ecosystem-tracker
grep -rl "CRAWLER_CONTROLS\|AGENTIC_WEB" pipeline tests | grep -v __pycache__ | \
  xargs sed -i '' -e 's/Track\.CRAWLER_CONTROLS/Track.ACCESS_CONTROLS/g' \
                  -e 's/Track\.AGENTIC_WEB/Track.PLATFORM_ECOSYSTEM/g'
grep -rl "crawler-controls\|agentic-web" sources.yaml tests/fixtures | \
  xargs sed -i '' -e 's/crawler-controls/access-controls/g' \
                  -e 's/agentic-web/platform-ecosystem/g'
```

Then fix remaining bare string literals by hand:

```bash
grep -rn "crawler-controls\|agentic-web\|CRAWLER_CONTROLS\|AGENTIC_WEB" pipeline tests sources.yaml | grep -v __pycache__
```

Expected after the sweep: only `TRACK_ALIASES` in `pipeline/taxonomy.py` and the alias tests in `tests/test_taxonomy.py` still mention the legacy slugs. Any other hit is a literal that needs updating to the canonical slug.

- [ ] **Step 5: Remove the dead `Pillar` enum and add the source subject**

In `pipeline/sources.py`, delete the `Pillar` class entirely (it is schema-v1 vestige; the only live consumer is the legacy Astro collection, which reads the string from frontmatter and does not import this enum):

```python
class Pillar(StrEnum):
    CRAWLER = "crawler"
    ECOSYSTEM = "ecosystem"
    AGENT = "agent"
```

Add the field to `Source`, directly below `default_tracks`:

```python
    default_subject: Subject = Subject.UNKNOWN
```

And add an alias-tolerant validator to `Source` so a `sources.yaml` carrying a legacy slug still loads:

```python
    @field_validator("default_tracks", mode="before")
    @classmethod
    def _resolve_track_aliases(cls, value: object) -> object:
        if isinstance(value, list):
            return [resolve_track(item) if isinstance(item, str) else item for item in value]
        return value
```

Replace the two existing import lines at the top of `pipeline/sources.py` with:

```python
from pydantic import BaseModel, Field, field_validator, model_validator

from pipeline.taxonomy import SourceRole, SourceTier, Subject, Track, resolve_track
```

- [ ] **Step 6: Run the full suite and the linter**

Run: `uv run pytest -q && uv run ruff check pipeline tests`
Expected: all tests pass, ruff reports no findings. If `tests/test_sources.py` asserts on `Pillar`, delete that assertion — the enum is gone by design.

- [ ] **Step 7: Commit**

```bash
git add pipeline/taxonomy.py pipeline/sources.py pipeline/check.py pipeline/state_of_play.py \
        pipeline/analyzer.py sources.yaml tests/
git commit -m "feat: split taxonomy into domain and subject axes

Tracks lose their subject words: crawler-controls becomes
access-controls, agentic-web becomes platform-ecosystem, and a new
identity-authorization track covers identity, delegated authority, and
agent payment credentials. A Subject axis (crawler/agent/both/unknown)
carries what a development is about, so any domain can be expressed for
either subject without adding tracks.

TRACK_ALIASES resolves the pre-2026-10 slugs at read time, so the 62
existing content files keep their frontmatter. Drops the dead Pillar
enum, which was the schema-v1 ancestor of this axis."
```

---

### Task 2: Entity registries

**Files:**
- Create: `entities/protocols.yaml`
- Create: `entities/players.yaml`
- Create: `pipeline/entities.py`
- Test: `tests/test_entities.py`

**Interfaces:**
- Consumes: `Front` from `pipeline.taxonomy` (Task 1 left it unchanged)
- Produces:
  - `ProtocolKind`, `SpecStatus`, `PlayerCategory` — `StrEnum`
  - `Protocol`, `Player` — pydantic models
  - `EntityRegistry` with `protocols: dict[str, Protocol]`, `players: dict[str, Player]`, methods `resolve_protocol(name: str) -> str | None` and `resolve_player(name: str) -> str | None` returning a slug or `None`
  - `load_registry(protocols_path: Path, players_path: Path) -> EntityRegistry`
  - `DEFAULT_PROTOCOLS_PATH`, `DEFAULT_PLAYERS_PATH` — `Path` constants

- [ ] **Step 1: Write the failing tests**

Create `tests/test_entities.py`:

```python
from pathlib import Path

import pytest

from pipeline.entities import (
    PlayerCategory,
    ProtocolKind,
    SpecStatus,
    load_registry,
)
from pipeline.taxonomy import Front

PROTOCOLS = Path("entities/protocols.yaml")
PLAYERS = Path("entities/players.yaml")


def _write(tmp_path: Path, protocols: str, players: str) -> tuple[Path, Path]:
    p = tmp_path / "protocols.yaml"
    q = tmp_path / "players.yaml"
    p.write_text(protocols)
    q.write_text(players)
    return p, q


MINIMAL_PROTOCOLS = """
protocols:
  - slug: web-bot-auth
    display_name: Web Bot Auth
    kind: identity
    steward: IETF webbotauth WG
    spec_url: https://datatracker.ietf.org/wg/webbotauth/about/
    spec_status: standards-track
    front: agents-identity
    first_observed: 2026-10-10
    aliases: ["WBA", "web bot auth"]
"""

MINIMAL_PLAYERS = """
players:
  - slug: cloudflare
    display_name: Cloudflare
    category: defense-infra
    short_descriptor: CDN and bot management
    home_url: https://www.cloudflare.com
    bots: ["CloudflareBot"]
"""


def test_shipped_registry_loads_and_is_internally_consistent():
    registry = load_registry(PROTOCOLS, PLAYERS)

    assert registry.protocols
    assert registry.players
    for protocol in registry.protocols.values():
        assert protocol.front in set(Front)
        assert isinstance(protocol.kind, ProtocolKind)
        assert isinstance(protocol.spec_status, SpecStatus)
    for player in registry.players.values():
        assert isinstance(player.category, PlayerCategory)
        assert player.short_descriptor


def test_resolve_matches_slug_display_name_and_alias_case_insensitively(tmp_path):
    p, q = _write(tmp_path, MINIMAL_PROTOCOLS, MINIMAL_PLAYERS)
    registry = load_registry(p, q)

    assert registry.resolve_protocol("web-bot-auth") == "web-bot-auth"
    assert registry.resolve_protocol("Web Bot Auth") == "web-bot-auth"
    assert registry.resolve_protocol("wba") == "web-bot-auth"
    assert registry.resolve_player("CLOUDFLARE") == "cloudflare"
    assert registry.resolve_protocol("a2a") is None
    assert registry.resolve_player("Totally Unknown Inc") is None


def test_duplicate_slugs_are_rejected(tmp_path):
    duplicated = MINIMAL_PLAYERS + """
  - slug: cloudflare
    display_name: Cloudflare Again
    category: defense-infra
    short_descriptor: duplicate
    home_url: https://example.com
"""
    p, q = _write(tmp_path, MINIMAL_PROTOCOLS, duplicated)

    with pytest.raises(ValueError, match="duplicate player slug: cloudflare"):
        load_registry(p, q)


def test_alias_colliding_with_another_entry_is_rejected(tmp_path):
    colliding = MINIMAL_PLAYERS + """
  - slug: akamai
    display_name: Akamai
    category: defense-infra
    short_descriptor: CDN and bot management
    home_url: https://www.akamai.com
    aliases: ["Cloudflare"]
"""
    p, q = _write(tmp_path, MINIMAL_PROTOCOLS, colliding)

    with pytest.raises(ValueError, match="ambiguous player name: cloudflare"):
        load_registry(p, q)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_entities.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pipeline.entities'`

- [ ] **Step 3: Write the registry module**

Create `pipeline/entities.py`:

```python
"""Controlled registries for the protocols and players the map tracks."""
from __future__ import annotations

from datetime import date
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from pipeline.taxonomy import Front

DEFAULT_PROTOCOLS_PATH = Path("entities/protocols.yaml")
DEFAULT_PLAYERS_PATH = Path("entities/players.yaml")


class ProtocolKind(StrEnum):
    IDENTITY = "identity"
    ACCESS = "access"
    PAYMENTS = "payments"
    PROVENANCE = "provenance"
    LICENSING = "licensing"
    TRANSPORT = "transport"


class SpecStatus(StrEnum):
    DRAFT = "draft"
    WG_DRAFT = "wg-draft"
    STANDARDS_TRACK = "standards-track"
    RFC = "rfc"
    STABLE = "stable"
    DEPRECATED = "deprecated"


class PlayerCategory(StrEnum):
    DEFENSE_INFRA = "defense-infra"
    AGENT_OPERATOR = "agent-operator"
    IDENTITY_PAYMENTS = "identity-payments"
    MONETIZATION = "monetization"
    STANDARDS_BODY = "standards-body"
    PUBLISHER = "publisher"


class Protocol(BaseModel):
    slug: str
    display_name: str
    kind: ProtocolKind
    steward: str
    spec_url: str
    spec_status: SpecStatus
    front: Front
    first_observed: date
    supersedes: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)


class Player(BaseModel):
    slug: str
    display_name: str
    category: PlayerCategory
    short_descriptor: str
    home_url: str
    bots: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)


class EntityRegistry(BaseModel):
    protocols: dict[str, Protocol]
    players: dict[str, Player]
    protocol_index: dict[str, str]
    player_index: dict[str, str]

    def resolve_protocol(self, name: str) -> str | None:
        return self.protocol_index.get(name.strip().casefold())

    def resolve_player(self, name: str) -> str | None:
        return self.player_index.get(name.strip().casefold())


def _build_index(entries: dict[str, BaseModel], label: str) -> dict[str, str]:
    index: dict[str, str] = {}
    for slug, entry in entries.items():
        names = [slug, entry.display_name, *entry.aliases]
        for name in names:
            key = name.strip().casefold()
            existing = index.get(key)
            if existing is not None and existing != slug:
                raise ValueError(f"ambiguous {label} name: {key}")
            index[key] = slug
    return index


def _load_entries(path: Path, key: str, model: type[BaseModel], label: str) -> dict[str, BaseModel]:
    raw = yaml.safe_load(path.read_text()) or {}
    entries: dict[str, BaseModel] = {}
    for item in raw.get(key, []):
        entry = model.model_validate(item)
        if entry.slug in entries:
            raise ValueError(f"duplicate {label} slug: {entry.slug}")
        entries[entry.slug] = entry
    if not entries:
        raise ValueError(f"{path} defines no {key}")
    return entries


def load_registry(
    protocols_path: Path = DEFAULT_PROTOCOLS_PATH,
    players_path: Path = DEFAULT_PLAYERS_PATH,
) -> EntityRegistry:
    """Load both registries and build case-insensitive name indexes."""
    protocols = _load_entries(protocols_path, "protocols", Protocol, "protocol")
    players = _load_entries(players_path, "players", Player, "player")
    return EntityRegistry(
        protocols=protocols,
        players=players,
        protocol_index=_build_index(protocols, "protocol"),
        player_index=_build_index(players, "player"),
    )
```

- [ ] **Step 4: Write the protocol registry**

Create `entities/protocols.yaml`:

```yaml
# Protocol registry — the columns of the map.
# `spec_status` describes the protocol itself, never any player's position on it.
# The pipeline never writes this file; entries arrive by human edit after review.
protocols:
  - slug: web-bot-auth
    display_name: Web Bot Auth
    kind: identity
    steward: IETF webbotauth WG
    spec_url: https://datatracker.ietf.org/wg/webbotauth/about/
    spec_status: standards-track
    front: agents-identity
    first_observed: 2026-10-10
    aliases: ["WBA", "web-bot-auth", "HTTP Message Signatures for bots"]

  - slug: a2a
    display_name: A2A
    kind: transport
    steward: Linux Foundation (Agentic AI Foundation)
    spec_url: https://a2a-protocol.org
    spec_status: stable
    front: agents-identity
    first_observed: 2026-10-10
    aliases: ["Agent2Agent", "agent-to-agent"]
    related: ["ap2"]

  - slug: mcp
    display_name: MCP
    kind: transport
    steward: Anthropic (open specification)
    spec_url: https://modelcontextprotocol.io
    spec_status: stable
    front: agents-identity
    first_observed: 2026-10-10
    aliases: ["Model Context Protocol"]

  - slug: ap2
    display_name: AP2
    kind: payments
    steward: Google and partners
    spec_url: https://ap2-protocol.org
    spec_status: draft
    front: agents-identity
    first_observed: 2026-10-10
    aliases: ["Agent Payments Protocol"]
    related: ["a2a", "acp"]

  - slug: acp
    display_name: ACP
    kind: payments
    steward: OpenAI and Stripe
    spec_url: https://agenticcommerce.dev
    spec_status: draft
    front: agents-identity
    first_observed: 2026-10-10
    aliases: ["Agentic Commerce Protocol"]
    related: ["ap2"]

  - slug: x402
    display_name: x402
    kind: payments
    steward: open
    spec_url: https://x402.org
    spec_status: draft
    front: agents-identity
    first_observed: 2026-10-10

  - slug: aipref-vocab
    display_name: AIPREF Vocabulary
    kind: access
    steward: IETF aipref WG
    spec_url: https://datatracker.ietf.org/doc/draft-ietf-aipref-vocab/
    spec_status: wg-draft
    front: access-discovery
    first_observed: 2026-10-10
    aliases: ["AIPREF", "aipref"]
    related: ["aipref-attach"]

  - slug: aipref-attach
    display_name: AIPREF Attachment
    kind: access
    steward: IETF aipref WG
    spec_url: https://datatracker.ietf.org/doc/html/draft-ietf-aipref-attach-04
    spec_status: wg-draft
    front: access-discovery
    first_observed: 2026-10-10
    related: ["aipref-vocab", "robots-txt"]

  - slug: rsl
    display_name: RSL
    kind: licensing
    steward: RSL Collective
    spec_url: https://rslstandard.org
    spec_status: stable
    front: rights-markets
    first_observed: 2026-10-10
    aliases: ["Really Simple Licensing"]

  - slug: tdmrep
    display_name: TDMRep
    kind: licensing
    steward: W3C
    spec_url: https://www.w3.org/community/tdmrep/
    spec_status: stable
    front: rights-markets
    first_observed: 2026-10-10
    aliases: ["TDM Reservation Protocol"]

  - slug: c2pa
    display_name: C2PA
    kind: provenance
    steward: C2PA
    spec_url: https://c2pa.org/specifications/
    spec_status: stable
    front: rights-markets
    first_observed: 2026-10-10
    aliases: ["Content Credentials"]

  - slug: robots-txt
    display_name: robots.txt
    kind: access
    steward: IETF
    spec_url: https://www.rfc-editor.org/rfc/rfc9309.html
    spec_status: rfc
    front: access-discovery
    first_observed: 2026-10-10
    aliases: ["RFC 9309", "Robots Exclusion Protocol"]
```

- [ ] **Step 5: Write the player registry**

Create `entities/players.yaml`. `short_descriptor` is the line rendered under the name in the matrix first column, so keep it under about 24 characters.

```yaml
# Player registry — the rows of the map.
# The pipeline never writes this file; entries arrive by human edit after
# review of data/entity-candidates.json.
players:
  # --- defense-infra ---
  - slug: cloudflare
    display_name: Cloudflare
    category: defense-infra
    short_descriptor: CDN · bot management
    home_url: https://www.cloudflare.com
  - slug: akamai
    display_name: Akamai
    category: defense-infra
    short_descriptor: CDN · bot management
    home_url: https://www.akamai.com
  - slug: fastly
    display_name: Fastly
    category: defense-infra
    short_descriptor: CDN
    home_url: https://www.fastly.com
  - slug: datadome
    display_name: DataDome
    category: defense-infra
    short_descriptor: bot defense
    home_url: https://datadome.co
  - slug: human-security
    display_name: HUMAN Security
    category: defense-infra
    short_descriptor: bot defense
    home_url: https://www.humansecurity.com
    aliases: ["HUMAN", "White Ops"]
  - slug: imperva
    display_name: Imperva
    category: defense-infra
    short_descriptor: WAF · bot management
    home_url: https://www.imperva.com
    aliases: ["Thales Imperva"]
  - slug: f5
    display_name: F5
    category: defense-infra
    short_descriptor: WAF · bot defense
    home_url: https://www.f5.com
  - slug: vercel
    display_name: Vercel
    category: defense-infra
    short_descriptor: hosting · BotID
    home_url: https://vercel.com

  # --- agent-operator ---
  - slug: openai
    display_name: OpenAI
    category: agent-operator
    short_descriptor: GPTBot · ChatGPT agent
    home_url: https://openai.com
    bots: ["GPTBot", "OAI-SearchBot", "ChatGPT-User"]
  - slug: anthropic
    display_name: Anthropic
    category: agent-operator
    short_descriptor: ClaudeBot
    home_url: https://www.anthropic.com
    bots: ["ClaudeBot", "Claude-User"]
  - slug: google
    display_name: Google
    category: agent-operator
    short_descriptor: Google-Extended
    home_url: https://www.google.com
    bots: ["Google-Extended", "Googlebot"]
  - slug: microsoft
    display_name: Microsoft
    category: agent-operator
    short_descriptor: Bingbot · Copilot
    home_url: https://www.microsoft.com
    bots: ["bingbot", "msnbot"]
  - slug: perplexity
    display_name: Perplexity
    category: agent-operator
    short_descriptor: PerplexityBot
    home_url: https://www.perplexity.ai
    bots: ["PerplexityBot", "Perplexity-User"]
  - slug: amazon
    display_name: Amazon
    category: agent-operator
    short_descriptor: Amazonbot · AgentCore
    home_url: https://www.amazon.com
    bots: ["Amazonbot"]
    aliases: ["AWS", "Amazon Web Services"]
  - slug: meta
    display_name: Meta
    category: agent-operator
    short_descriptor: Meta-ExternalAgent
    home_url: https://www.meta.com
    bots: ["Meta-ExternalAgent", "meta-externalagent"]

  # --- identity-payments ---
  - slug: visa
    display_name: Visa
    category: identity-payments
    short_descriptor: agent payments
    home_url: https://www.visa.com
  - slug: mastercard
    display_name: Mastercard
    category: identity-payments
    short_descriptor: agent payments
    home_url: https://www.mastercard.com
  - slug: stripe
    display_name: Stripe
    category: identity-payments
    short_descriptor: payments · ACP
    home_url: https://stripe.com
  - slug: okta
    display_name: Okta
    category: identity-payments
    short_descriptor: agent identity
    home_url: https://www.okta.com
    aliases: ["Auth0"]
  - slug: stytch
    display_name: Stytch
    category: identity-payments
    short_descriptor: agent identity
    home_url: https://stytch.com
  - slug: skyfire
    display_name: Skyfire
    category: identity-payments
    short_descriptor: KYA · agent wallet
    home_url: https://skyfire.xyz

  # --- monetization ---
  - slug: tollbit
    display_name: TollBit
    category: monetization
    short_descriptor: pay-per-crawl
    home_url: https://tollbit.com
  - slug: prorata
    display_name: ProRata
    category: monetization
    short_descriptor: attribution payouts
    home_url: https://prorata.ai
    aliases: ["ProRata.ai", "Gist"]
  - slug: rsl-collective
    display_name: RSL Collective
    category: monetization
    short_descriptor: rights collective
    home_url: https://rslcollective.org

  # --- standards-body ---
  - slug: ietf
    display_name: IETF
    category: standards-body
    short_descriptor: standards body
    home_url: https://www.ietf.org
  - slug: w3c
    display_name: W3C
    category: standards-body
    short_descriptor: standards body
    home_url: https://www.w3.org
  - slug: linux-foundation
    display_name: Linux Foundation
    category: standards-body
    short_descriptor: A2A · AP2 steward
    home_url: https://www.linuxfoundation.org
    aliases: ["Agentic AI Foundation"]
  - slug: nist
    display_name: NIST
    category: standards-body
    short_descriptor: agent standards
    home_url: https://www.nist.gov

  # --- publisher ---
  - slug: reddit
    display_name: Reddit
    category: publisher
    short_descriptor: platform · publisher
    home_url: https://www.reddit.com
  - slug: news-media-alliance
    display_name: News/Media Alliance
    category: publisher
    short_descriptor: publisher trade body
    home_url: https://www.newsmediaalliance.org
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `uv run pytest tests/test_entities.py -v && uv run ruff check pipeline tests`
Expected: PASS, no ruff findings.

- [ ] **Step 7: Commit**

```bash
git add entities/ pipeline/entities.py tests/test_entities.py
git commit -m "feat: add protocol and player registries

Two human-maintained YAML registries become the controlled vocabulary
the map joins against: 12 protocols as columns, 31 players as rows.
Loading rejects duplicate slugs and aliases that would make a name
ambiguous, and builds case-insensitive indexes so free-text names from
analysis can resolve to a slug or cleanly fail to."
```

---

### Task 3: Entity candidate queue

The only path by which the registries grow. Analysis appends what it believes it saw outside the vocabulary; a human reads the queue and edits the YAML.

**Files:**
- Create: `pipeline/entity_candidates.py`
- Test: `tests/test_entity_candidates.py`

**Interfaces:**
- Consumes: nothing from earlier tasks
- Produces:
  - `EntityCandidate` — pydantic model with `kind: Literal["player", "protocol"]`, `observed_name: str`, `first_seen_at: datetime`, `last_seen_at: datetime`, `occurrences: int`, `evidence_ids: list[str]`, `feed_slugs: list[str]`
  - `DEFAULT_CANDIDATES_PATH: Path` = `Path("data/entity-candidates.json")`
  - `load_candidates(path: Path = DEFAULT_CANDIDATES_PATH) -> dict[str, EntityCandidate]` keyed `"<kind>:<casefolded name>"`
  - `record_candidates(path: Path, kind: str, names: list[str], *, evidence_ids: list[str], feed_slug: str, now: datetime) -> None`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_entity_candidates.py`:

```python
from datetime import UTC, datetime

from pipeline.entity_candidates import load_candidates, record_candidates

NOW = datetime(2026, 10, 10, 8, 0, tzinfo=UTC)
LATER = datetime(2026, 10, 11, 8, 0, tzinfo=UTC)


def test_recording_creates_the_queue_file_with_one_entry_per_name(tmp_path):
    path = tmp_path / "entity-candidates.json"

    record_candidates(
        path,
        "player",
        ["Scalepost", "Human Native"],
        evidence_ids=["ev-1"],
        feed_slug="2026-10-10-example",
        now=NOW,
    )

    candidates = load_candidates(path)
    assert set(candidates) == {"player:scalepost", "player:human native"}
    entry = candidates["player:scalepost"]
    assert entry.observed_name == "Scalepost"
    assert entry.occurrences == 1
    assert entry.first_seen_at == NOW
    assert entry.evidence_ids == ["ev-1"]


def test_recording_the_same_feed_slug_again_is_idempotent(tmp_path):
    path = tmp_path / "entity-candidates.json"
    args = dict(evidence_ids=["ev-1"], feed_slug="2026-10-10-example", now=NOW)

    record_candidates(path, "player", ["Scalepost"], **args)
    record_candidates(path, "player", ["Scalepost"], **args)

    entry = load_candidates(path)["player:scalepost"]
    assert entry.occurrences == 1
    assert entry.feed_slugs == ["2026-10-10-example"]
    assert entry.evidence_ids == ["ev-1"]


def test_a_new_feed_slug_bumps_occurrences_and_last_seen(tmp_path):
    path = tmp_path / "entity-candidates.json"

    record_candidates(
        path, "player", ["Scalepost"],
        evidence_ids=["ev-1"], feed_slug="first", now=NOW,
    )
    record_candidates(
        path, "player", ["scalepost"],
        evidence_ids=["ev-2"], feed_slug="second", now=LATER,
    )

    entry = load_candidates(path)["player:scalepost"]
    assert entry.occurrences == 2
    assert entry.feed_slugs == ["first", "second"]
    assert entry.evidence_ids == ["ev-1", "ev-2"]
    assert entry.first_seen_at == NOW
    assert entry.last_seen_at == LATER
    assert entry.observed_name == "Scalepost"


def test_loading_a_missing_file_returns_an_empty_queue(tmp_path):
    assert load_candidates(tmp_path / "nope.json") == {}


def test_blank_names_are_ignored(tmp_path):
    path = tmp_path / "entity-candidates.json"

    record_candidates(
        path, "protocol", ["  ", ""],
        evidence_ids=["ev-1"], feed_slug="first", now=NOW,
    )

    assert load_candidates(path) == {}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_entity_candidates.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pipeline.entity_candidates'`

- [ ] **Step 3: Write the queue module**

Create `pipeline/entity_candidates.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_entity_candidates.py -v && uv run ruff check pipeline tests`
Expected: PASS, no ruff findings.

- [ ] **Step 5: Commit**

```bash
git add pipeline/entity_candidates.py tests/test_entity_candidates.py
git commit -m "feat: add entity candidate review queue

Analysis appends names it saw outside the registries here; a human reads
the queue and edits entities/*.yaml. Re-recording the same feed slug is
a no-op, so replaying a day never inflates occurrence counts."
```

---

### Task 4: Controlled extraction in the analyzer

**Files:**
- Modify: `pipeline/analyzer.py`
- Test: `tests/test_analyzer.py`

**Interfaces:**
- Consumes: `EntityRegistry`, `load_registry` from `pipeline.entities` (Task 2); `record_candidates` from `pipeline.entity_candidates` (Task 3); `Subject`, `resolve_track` from `pipeline.taxonomy` (Task 1)
- Produces:
  - `AnalyzerResponse` gains `subject: str = "unknown"` and `protocols: list[str] = []`
  - `AnalysisResult` gains `subject: Subject`, `players: list[str]`, `protocols: list[str]` (both registry slugs); `actors: list[str]` keeps its existing free-text meaning
  - `AnalysisResult` also gains `unknown_players: list[str]` and `unknown_protocols: list[str]`, which carry out-of-vocabulary names to the caller for queueing and are **never written to frontmatter**
  - `resolve_entities(registry, *, actors, protocols) -> tuple[list[str], list[str], list[str], list[str]]` returning `(player_slugs, protocol_slugs, unknown_players, unknown_protocols)`
  - `_validated_subject(raw: AnalyzerResponse, source: Source) -> Subject`
  - **`analyze_change`'s signature and return type are unchanged.** `pipeline/backfill_feed.py:36` declares `Analyze = Callable[..., Awaitable[AnalysisResult]]` and both `check.py` and `backfill_feed.py` inject the function through that seam; returning a tuple instead would break every injection site, so the unknowns ride on the result object.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_analyzer.py`:

```python
from pipeline.analyzer import AnalyzerResponse, _validated_subject, resolve_entities
from pipeline.entities import load_registry
from pipeline.taxonomy import Subject

REGISTRY = load_registry()


def test_resolve_entities_keeps_registry_members_and_reports_the_rest():
    players, protocols, unknown_players, unknown_protocols = resolve_entities(
        REGISTRY,
        actors=["Cloudflare", "DataDome", "Totally Unknown Inc"],
        protocols=["Web Bot Auth", "wba", "Imaginary Protocol"],
    )

    assert players == ["cloudflare", "datadome"]
    assert protocols == ["web-bot-auth"]
    assert unknown_players == ["Totally Unknown Inc"]
    assert unknown_protocols == ["Imaginary Protocol"]


def test_resolve_entities_deduplicates_aliases_of_one_entity():
    players, protocols, _, _ = resolve_entities(
        REGISTRY, actors=["Amazon", "AWS"], protocols=["AIPREF", "aipref-vocab"]
    )

    assert players == ["amazon"]
    assert protocols == ["aipref-vocab"]


def _response(**overrides) -> AnalyzerResponse:
    base = dict(
        change_kind="material",
        importance=0.5,
        title="t",
        summary="s",
        insight="i",
        implication="im",
        why_it_matters="w",
        primary_track="access-controls",
        tracks=["access-controls"],
        actors=[],
        trend_signals=[],
        confidence="high",
    )
    base.update(overrides)
    return AnalyzerResponse(**base)


def test_validated_subject_accepts_known_values(crawler_source):
    assert _validated_subject(_response(subject="agent"), crawler_source) is Subject.AGENT
    assert _validated_subject(_response(subject="both"), crawler_source) is Subject.BOTH


def test_validated_subject_falls_back_to_the_source_default(crawler_source):
    crawler_source.default_subject = Subject.CRAWLER

    assert _validated_subject(_response(subject="nonsense"), crawler_source) is Subject.CRAWLER
    assert _validated_subject(_response(), crawler_source) is Subject.CRAWLER
```

`crawler_source` and `fake_model` are existing fixtures in this file (`tests/test_analyzer.py:19` and `:11`); reuse them rather than adding new ones. Task 1 already rewrote `crawler_source`'s `default_tracks` to `[Track.ACCESS_CONTROLS]`.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_analyzer.py -v`
Expected: FAIL — `ImportError: cannot import name 'resolve_entities' from 'pipeline.analyzer'`

- [ ] **Step 3: Extend the analyzer models and add resolution**

In `pipeline/analyzer.py`, extend the imports:

```python
from pipeline.entities import EntityRegistry
from pipeline.taxonomy import Subject, Track, validate_tracks
```

Add the two new fields to `AnalyzerResponse`, after `actors`:

```python
    subject: str = "unknown"
    protocols: list[str] = Field(default_factory=list)
```

Add five fields to `AnalysisResult`, after `actors`:

```python
    subject: Subject = Subject.UNKNOWN
    players: list[str] = Field(default_factory=list)
    protocols: list[str] = Field(default_factory=list)
    # Carried to the caller for the review queue; never written to frontmatter.
    unknown_players: list[str] = Field(default_factory=list)
    unknown_protocols: list[str] = Field(default_factory=list)
```

Add the resolution helper and the subject validator at module level:

```python
def resolve_entities(
    registry: EntityRegistry,
    *,
    actors: list[str],
    protocols: list[str],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Split observed names into registry slugs and out-of-vocabulary names.

    Slugs are deduplicated, so two aliases of one entity collapse to one slug.
    """
    player_slugs: list[str] = []
    protocol_slugs: list[str] = []
    unknown_players: list[str] = []
    unknown_protocols: list[str] = []

    for name in actors:
        slug = registry.resolve_player(name)
        if slug is None:
            unknown_players.append(name)
        elif slug not in player_slugs:
            player_slugs.append(slug)

    for name in protocols:
        slug = registry.resolve_protocol(name)
        if slug is None:
            unknown_protocols.append(name)
        elif slug not in protocol_slugs:
            protocol_slugs.append(slug)

    return player_slugs, protocol_slugs, unknown_players, unknown_protocols


def _validated_subject(raw: AnalyzerResponse, source: Source) -> Subject:
    """Fall back to the source's declared subject, mirroring track fallback."""
    try:
        return Subject(raw.subject)
    except ValueError:
        return source.default_subject
```

- [ ] **Step 4: Wire resolution into the analysis call**

Extend the system instruction so the model is told the vocabulary is closed. Find the existing instruction string (the one containing `facts, dates, actors, or URLs.` near line 64) and append:

```python
    "Name only entities you are confident appear in the evidence. "
    "Set `subject` to `crawler` when the development concerns automated "
    "crawling, `agent` when it concerns delegated agents acting for a user, "
    "`both` when it genuinely concerns both, and `unknown` when the evidence "
    "does not say. List protocol names in `protocols`."
```

Then extend the construction of `AnalysisResult` at the end of the analysis function. Add a `registry` parameter to that function's signature (defaulting to a lazily loaded module-level registry so existing callers keep working):

```python
_REGISTRY: EntityRegistry | None = None


def _registry() -> EntityRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        from pipeline.entities import load_registry

        _REGISTRY = load_registry()
    return _REGISTRY
```

In `analyze_change` (line 94), after `primary_track, tracks, confidence = _validated_classification(raw, source)`:

```python
    actors = _clean_string_list(raw.actors)
    players, protocols, unknown_players, unknown_protocols = resolve_entities(
        _registry(),
        actors=actors,
        protocols=_clean_string_list(raw.protocols),
    )
```

and pass the new values into the existing `AnalysisResult(...)` construction, replacing its current `actors=` line:

```python
        actors=actors,
        subject=_validated_subject(raw, source),
        players=players,
        protocols=protocols,
        unknown_players=unknown_players,
        unknown_protocols=unknown_protocols,
```

The signature and return type stay as they are, so the `Analyze` seam in `pipeline/backfill_feed.py:36` and the injected `analyze_change` callables in `pipeline/check.py` keep working untouched.

- [ ] **Step 5: Queue the unknowns at the call site that writes the feed item**

The analyzer must not import the queue — it would turn analysis into a file-writing step and force every analyzer test to touch disk. The caller that already knows the feed slug and evidence ids does the queueing.

In `pipeline/check.py`, add the imports:

```python
from pipeline.entity_candidates import DEFAULT_CANDIDATES_PATH, record_candidates
```

Immediately after the `write_feed_item(...)` call that publishes a feed item, add:

```python
        if analysis.unknown_players or analysis.unknown_protocols:
            record_candidates(
                DEFAULT_CANDIDATES_PATH,
                "player",
                analysis.unknown_players,
                evidence_ids=evidence_ids,
                feed_slug=feed_path.stem,
                now=detected_at,
            )
            record_candidates(
                DEFAULT_CANDIDATES_PATH,
                "protocol",
                analysis.unknown_protocols,
                evidence_ids=evidence_ids,
                feed_slug=feed_path.stem,
                now=detected_at,
            )
```

Bind `feed_path` to the return value of `write_feed_item` if the current code discards it. Use the same `evidence_ids` and `detected_at` values already passed to `write_feed_item` at that site, so the queue entry and the feed record agree.

- [ ] **Step 6: Run the full suite**

Run: `uv run pytest -q && uv run ruff check pipeline tests`
Expected: all pass. Existing analyzer tests keep working unchanged, because `analyze_change` still returns a single `AnalysisResult`. If a test asserts on the exact set of `AnalysisResult` fields, extend it with the five new ones.

- [ ] **Step 7: Commit**

```bash
git add pipeline/analyzer.py pipeline/check.py tests/test_analyzer.py
git commit -m "feat: extract subject and controlled entities in analysis

Analysis now classifies the subject axis and emits player and protocol
slugs drawn only from the registries. Names it reports outside the
vocabulary are returned to the caller and queued for human review rather
than entering a record. Subject falls back to the source default the
same way track classification already does."
```

---

### Task 5: Feed frontmatter and site schema

**Files:**
- Modify: `pipeline/feed_writer.py`
- Modify: `site/src/lib/taxonomy.ts`
- Modify: `site/src/content.config.ts`
- Modify: `site/src/lib/sources.ts:59`
- Test: `tests/test_feed_writer.py`

**Interfaces:**
- Consumes: `AnalysisResult.subject`, `.players`, `.protocols` from Task 4
- Produces: feed frontmatter keys `subject`, `players`, `protocols`; `normalizeTrack(value: string): Track` exported from `site/src/lib/taxonomy.ts`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_feed_writer.py`. The `source` and `analysis` fixtures already exist in this file (`:14` and `:27`); these tests reuse them and parse frontmatter with `yaml.safe_load`, matching the house style at `:62`. Add `Subject` to the taxonomy import at the top of the file:

```python
from pipeline.taxonomy import SourceRole, SourceTier, Subject, Track
```

```python
def _written(tmp_path, source, analysis):
    observed = datetime(2026, 10, 10, 8, tzinfo=UTC)
    path = write_feed_item(
        feed_dir=tmp_path,
        source=source,
        analysis=analysis,
        status=PublicationStatus.VERIFIED,
        event_date=observed,
        published_at=observed,
        detected_at=observed,
        evidence_ids=["cloudflare--abc123"],
        source_urls=["https://example.test/policy"],
        unified_diff="+signed agents",
    )
    return yaml.safe_load(path.read_text().split("---", 2)[1])


def test_frontmatter_carries_subject_players_and_protocols(tmp_path, source, analysis):
    analysis.subject = Subject.AGENT
    analysis.players = ["cloudflare", "openai"]
    analysis.protocols = ["web-bot-auth"]

    frontmatter = _written(tmp_path, source, analysis)

    assert frontmatter["subject"] == "agent"
    assert frontmatter["players"] == ["cloudflare", "openai"]
    assert frontmatter["protocols"] == ["web-bot-auth"]


def test_frontmatter_omits_empty_entity_lists(tmp_path, source, analysis):
    frontmatter = _written(tmp_path, source, analysis)

    assert frontmatter["subject"] == "unknown"
    assert "players" not in frontmatter
    assert "protocols" not in frontmatter


def test_frontmatter_never_leaks_the_review_queue_fields(tmp_path, source, analysis):
    analysis.unknown_players = ["Totally Unknown Inc"]
    analysis.unknown_protocols = ["Imaginary Protocol"]

    frontmatter = _written(tmp_path, source, analysis)

    assert "unknown_players" not in frontmatter
    assert "unknown_protocols" not in frontmatter
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_feed_writer.py -v`
Expected: FAIL — `assert "subject: agent\n" in text`

- [ ] **Step 3: Emit the new frontmatter keys**

In `pipeline/feed_writer.py` `_compose`, after the `actors` line (currently line 89):

```python
        f"subject: {analysis.subject.value}\n"
```

and after it, only when non-empty, so quiet records stay clean:

```python
    if analysis.players:
        frontmatter += f"players:\n{_yaml_list(analysis.players, quoted=True)}"
    if analysis.protocols:
        frontmatter += f"protocols:\n{_yaml_list(analysis.protocols, quoted=True)}"
```

Place these additions where the existing conditional `development_slug` append happens, so the ordering stays `… actors, subject, [players], [protocols], event_date …`. Keep `subject` inside the f-string block because it is always present.

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_feed_writer.py -v`
Expected: PASS

- [ ] **Step 5: Update the site taxonomy module**

Replace the head of `site/src/lib/taxonomy.ts`:

```ts
export const TRACKS = [
  "policy-regulation",
  "litigation-legal",
  "search-discovery",
  "access-controls",
  "platform-ecosystem",
  "identity-authorization",
  "licensing-monetization",
  "standards-protocols",
  "asset-rights",
  "measurement-economics",
] as const;

export type Track = (typeof TRACKS)[number];

/** Slugs used before 2026-10. Content on disk keeps them; readers resolve. */
export const LEGACY_TRACK_ALIASES: Record<string, Track> = {
  "crawler-controls": "access-controls",
  "agentic-web": "platform-ecosystem",
};

export function normalizeTrack(value: string): Track {
  const alias = LEGACY_TRACK_ALIASES[value];
  if (alias) return alias;
  if ((TRACKS as readonly string[]).includes(value)) return value as Track;
  throw new Error(`Unknown track: ${value}`);
}

export const SUBJECTS = ["crawler", "agent", "both", "unknown"] as const;
export type Subject = (typeof SUBJECTS)[number];

export const SUBJECT_LABELS: Record<Subject, string> = {
  crawler: "Crawlers",
  agent: "Agents",
  both: "Crawlers & Agents",
  unknown: "Unspecified",
};
```

Update `FRONT_TRACKS` and `TRACK_LABELS` to the canonical slugs:

```ts
export const FRONT_TRACKS: Record<Front, readonly Track[]> = {
  "access-discovery": ["access-controls", "search-discovery"],
  "agents-identity": ["platform-ecosystem", "standards-protocols", "identity-authorization"],
  "rights-markets": ["licensing-monetization", "asset-rights"],
  "governance-law": ["policy-regulation", "litigation-legal"],
  "measurement-economics": ["measurement-economics"],
};

export const TRACK_LABELS: Record<Track, string> = {
  "policy-regulation": "Policy & Regulation",
  "litigation-legal": "Litigation & Legal",
  "search-discovery": "Search & AI Discovery",
  "access-controls": "Access Controls",
  "platform-ecosystem": "Platform & Ecosystem",
  "identity-authorization": "Identity & Authorization",
  "licensing-monetization": "Licensing & Monetization",
  "standards-protocols": "Standards & Protocols",
  "asset-rights": "Asset Rights",
  "measurement-economics": "Measurement & Economics",
};
```

The existing runtime assertion below these (`flattened.length !== TRACKS.length`) still holds: ten tracks, each in exactly one front.

- [ ] **Step 6: Normalize tracks at the schema boundary**

Eight site files consume raw track values, and after the rename each one breaks differently: `frontForTrack()` **throws** on a legacy slug (`fronts/index.astro:9`, `index.astro:32-33`, `developments/index.astro:34`), `TRACK_LABELS[track]` yields `undefined` and renders a blank tag (`components/TrackTag.astro:5`), and `tracks.some((t) => tracks.includes(t))` **silently drops** all 62 legacy records from the access-discovery and agents-identity front pages (`fronts/[front].astro:20,22`).

Rather than wrapping `normalizeTrack` at eight call sites, normalize once where content enters: a zod `.transform()` on the shared `track` type. Every consumer then receives canonical slugs and needs no change.

In `site/src/content.config.ts`, add the import and replace the `track` constant:

```ts
import { normalizeTrack } from "./lib/taxonomy";

// Accepts canonical and pre-2026-10 slugs; always yields a canonical Track,
// so no page sees a legacy value and no content file needs rewriting.
const track = z
  .enum([
    "policy-regulation",
    "litigation-legal",
    "search-discovery",
    "access-controls",
    "platform-ecosystem",
    "identity-authorization",
    "licensing-monetization",
    "standards-protocols",
    "asset-rights",
    "measurement-economics",
    "crawler-controls",
    "agentic-web",
  ])
  .transform(normalizeTrack);

const subject = z.enum(["crawler", "agent", "both", "unknown"]);
```

Add to the `feed` collection schema, beside `actors`:

```ts
    subject: subject.default("unknown"),
    players: z.array(z.string()).default([]),
    protocols: z.array(z.string()).default([]),
```

Leave the `legacyEvents` collection alone — it has its own schema and is excluded from current intelligence.

- [ ] **Step 7: Fix the one hardcoded track filter**

`site/src/lib/sources.ts:59` reads `sources.yaml`, which Task 1 already rewrote to canonical slugs, so the literal is now stale. Replace:

```ts
  return loadSources().filter((s) => s.default_tracks.includes("crawler-controls"));
```

with:

```ts
  return loadSources().filter((s) => s.default_tracks.includes("access-controls"));
```

- [ ] **Step 8: Verify the site builds and legacy content still appears**

```bash
cd site && npm ci && npm run check && npm run build
```

Expected: `astro check` reports no errors and the build completes.

Then confirm the silent-drop bug is actually absent, since a passing build would not reveal it:

```bash
grep -c "development-card\|feed-card" dist/fronts/access-discovery/index.html
grep -c "development-card\|feed-card" dist/fronts/agents-identity/index.html
```

Expected: both counts are greater than zero. A zero means the transform is not applied and the legacy records were dropped. Adjust the class names in the grep to whatever `DevelopmentCard.astro` and `FeedCard.astro` actually render as their root element.

- [ ] **Step 9: Commit**

```bash
cd ~/Documents/Claude/Skills/ai-ecosystem-tracker
git add pipeline/feed_writer.py tests/test_feed_writer.py site/src/lib/taxonomy.ts \
        site/src/content.config.ts site/src/lib/sources.ts
git commit -m "feat: publish subject and entity links to the site

Feed frontmatter now carries subject plus controlled player and protocol
slugs, omitting the entity lists when empty so quiet records stay clean.
The site accepts canonical and pre-2026-10 track slugs and normalizes on
read, so no existing content file is rewritten."
```

---

## Verification

After Task 5, the whole sub-project is green when all of these pass from the repository root:

```bash
uv run pytest -q
uv run ruff check pipeline tests
cd site && npm run check && npm run build
```

And a dry run still works against a real source without writing publication files:

```bash
GEMINI_API_KEY=... uv run python -m pipeline.check --dry-run --only gptbot
```

## Notes for the implementer

- **No track URLs exist**, so spec §3.4's "old track URLs redirect" is satisfied vacuously. The site routes by front (`/fronts/{front}`), not by track; `site/src/pages/pillars/` is a legacy archive route that reads schema-v1 frontmatter and is unaffected by removing the Python `Pillar` enum.
- **Nothing in this sub-project writes `entities/*.yaml`.** If an implementation step seems to need the pipeline to add a registry entry, that is a design error — the candidate queue plus a human edit is the only path.
- `data/entity-candidates.json` is created on first write, not committed empty.

## What this sub-project deliberately does not do

- No `data/positions.json`, no proposal stage, no pull request workflow — sub-project ②.
- No matrix page, protocol page, player page, or Editorial token set — sub-project ③.
- **No source expansion entries.** Spec §9.3 has source expansion landing incrementally alongside this sub-project; planning deferred it to its own follow-on plan instead, because each of the ~20 new sources needs its feed URL, fetch mode, tier, role, track, and subject verified individually, and that verification work is unrelated to the vocabulary changes here. The registries name the players; the sources that monitor them follow.
