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


def publication_status(source: Source) -> PublicationStatus:
    if source.tier in {SourceTier.PRIMARY, SourceTier.MEASUREMENT}:
        return PublicationStatus.VERIFIED
    if source.tier is SourceTier.SPECIALIST:
        return PublicationStatus.REPORTED
    return PublicationStatus.SIGNAL


def should_promote(status: PublicationStatus, analysis: AnalysisResult) -> bool:
    return status is PublicationStatus.VERIFIED and analysis.change_kind == "material"
