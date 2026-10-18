"""Deterministic publication rules for the public ecosystem feed."""
from __future__ import annotations

from enum import StrEnum

from pipeline.analyzer import AnalysisResult
from pipeline.sources import Source
from pipeline.taxonomy import SourceTier


class PublicationStatus(StrEnum):
    VERIFIED = "verified"
    REPORTED = "reported"
    SIGNAL = "signal"


# Tiers treated as first-party factual evidence everywhere in the pipeline.
# `verified` publication status and primary-evidence proposals both rest on
# this exact set, so it is defined once here and shared rather than restated.
_PRIMARY_TIERS = {SourceTier.PRIMARY, SourceTier.MEASUREMENT}


def is_primary_tier(tier: SourceTier | str) -> bool:
    """True when `tier` is one of the tiers treated as first-party evidence.

    Accepts either a `SourceTier` member (as on a configured `Source`) or a
    raw string tier name (as read back from feed frontmatter), case- and
    whitespace-insensitively.
    """
    return str(tier).strip().lower() in _PRIMARY_TIERS


def publication_status(source: Source) -> PublicationStatus:
    if is_primary_tier(source.tier):
        return PublicationStatus.VERIFIED
    if source.tier is SourceTier.SPECIALIST:
        return PublicationStatus.REPORTED
    return PublicationStatus.SIGNAL


def should_promote(status: PublicationStatus, analysis: AnalysisResult) -> bool:
    return status is PublicationStatus.VERIFIED and analysis.change_kind == "material"
