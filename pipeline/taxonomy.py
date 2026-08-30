"""Canonical editorial taxonomy for Web intelligence."""
from __future__ import annotations

from enum import StrEnum


class Track(StrEnum):
    POLICY_REGULATION = "policy-regulation"
    LITIGATION_LEGAL = "litigation-legal"
    SEARCH_DISCOVERY = "search-discovery"
    CRAWLER_CONTROLS = "crawler-controls"
    AGENTIC_WEB = "agentic-web"
    LICENSING_MONETIZATION = "licensing-monetization"
    STANDARDS_PROTOCOLS = "standards-protocols"
    ASSET_RIGHTS = "asset-rights"
    MEASUREMENT_ECONOMICS = "measurement-economics"


class Front(StrEnum):
    ACCESS_DISCOVERY = "access-discovery"
    AGENTS_IDENTITY = "agents-identity"
    RIGHTS_MARKETS = "rights-markets"
    GOVERNANCE_LAW = "governance-law"
    MEASUREMENT_ECONOMICS = "measurement-economics"


class SourceTier(StrEnum):
    PRIMARY = "primary"
    MEASUREMENT = "measurement"
    SPECIALIST = "specialist"
    COMMENTARY = "commentary"


class SourceRole(StrEnum):
    PLATFORM_DOCS = "platform-docs"
    STANDARDS = "standards"
    REGULATOR = "regulator"
    LEGAL_PRIMARY = "legal-primary"
    PUBLISHER = "publisher"
    INFRASTRUCTURE = "infrastructure"
    MEASUREMENT = "measurement"
    REPORTING = "reporting"


FRONT_TRACKS: dict[Front, tuple[Track, ...]] = {
    Front.ACCESS_DISCOVERY: (
        Track.CRAWLER_CONTROLS,
        Track.SEARCH_DISCOVERY,
    ),
    Front.AGENTS_IDENTITY: (
        Track.AGENTIC_WEB,
        Track.STANDARDS_PROTOCOLS,
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


def validate_tracks(primary_track: Track, tracks: list[Track]) -> None:
    """Validate an event's primary and secondary track assignments."""
    if not tracks:
        raise ValueError("tracks must not be empty")
    if len(tracks) != len(set(tracks)):
        raise ValueError("tracks must not contain duplicates")
    if primary_track not in tracks:
        raise ValueError("primary_track must appear in tracks")
