"""Controlled registries for the protocols and players the map tracks."""
from __future__ import annotations

from datetime import date
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from pipeline.taxonomy import Front

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOLS_PATH = _REPO_ROOT / "entities" / "protocols.yaml"
DEFAULT_PLAYERS_PATH = _REPO_ROOT / "entities" / "players.yaml"


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
        names = [slug, entry.display_name, *entry.aliases, *getattr(entry, "bots", [])]
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
