from pipeline.analyzer import AnalysisResult
from pipeline.feed import PublicationStatus, publication_status, should_promote
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Track


def _source(tier: SourceTier) -> Source:
    return Source(
        slug=f"source-{tier.value}",
        type=SourceType.HTML_PAGE,
        url="https://example.test",
        display_name="Example",
        default_tracks=[Track.CRAWLER_CONTROLS],
        tier=tier,
        role=SourceRole.REPORTING,
    )


def _analysis(change_kind: str = "material") -> AnalysisResult:
    return AnalysisResult(
        change_kind=change_kind,
        importance=0.7,
        title="A crawler policy changed",
        summary="The policy added a new control.",
        insight="Access rules are becoming more specific.",
        implication="Publishers can distinguish automated uses.",
        why_it_matters="The change makes crawler policy more enforceable.",
        primary_track=Track.CRAWLER_CONTROLS,
        tracks=[Track.CRAWLER_CONTROLS],
        actors=["Example"],
        trend_signals=[],
        confidence="high",
    )


def test_source_tier_determines_publication_status():
    assert publication_status(_source(SourceTier.PRIMARY)) is PublicationStatus.VERIFIED
    assert publication_status(_source(SourceTier.MEASUREMENT)) is PublicationStatus.VERIFIED
    assert publication_status(_source(SourceTier.SPECIALIST)) is PublicationStatus.REPORTED
    assert publication_status(_source(SourceTier.COMMENTARY)) is PublicationStatus.SIGNAL


def test_only_verified_material_analysis_promotes_to_development():
    assert should_promote(PublicationStatus.VERIFIED, _analysis()) is True
    assert should_promote(PublicationStatus.REPORTED, _analysis()) is False
    assert should_promote(PublicationStatus.SIGNAL, _analysis()) is False
    assert should_promote(PublicationStatus.VERIFIED, _analysis("cosmetic")) is False
