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


def test_bot_name_resolves_to_its_operator_in_the_shipped_registry():
    registry = load_registry(PROTOCOLS, PLAYERS)

    assert registry.resolve_player("ClaudeBot") == "anthropic"
    assert registry.resolve_player("GPTBot") == "openai"


def test_bot_name_resolves_case_insensitively(tmp_path):
    p, q = _write(tmp_path, MINIMAL_PROTOCOLS, MINIMAL_PLAYERS)
    registry = load_registry(p, q)

    assert registry.resolve_player("cloudflarebot") == "cloudflare"


def test_bot_name_colliding_with_another_entry_is_rejected(tmp_path):
    colliding = MINIMAL_PLAYERS + """
  - slug: akamai
    display_name: Akamai
    category: defense-infra
    short_descriptor: CDN and bot management
    home_url: https://www.akamai.com
    bots: ["CloudflareBot"]
"""
    p, q = _write(tmp_path, MINIMAL_PROTOCOLS, colliding)

    with pytest.raises(ValueError, match="ambiguous player name: cloudflarebot"):
        load_registry(p, q)
