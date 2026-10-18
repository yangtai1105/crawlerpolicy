from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.analyzer import (
    AnalysisResult,
    AnalyzerResponse,
    PositionClaim,
    _validated_subject,
    analyze_change,
    resolve_entities,
    resolve_position_claims,
)
from pipeline.entities import load_registry
from pipeline.positions import PositionStatus
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Subject, Track

REGISTRY = load_registry()


@pytest.fixture
def fake_model():
    model = MagicMock()
    model.generate = AsyncMock()
    return model


@pytest.fixture
def crawler_source():
    return Source(
        slug="gptbot",
        type=SourceType.HTML_PAGE,
        url="https://x",
        display_name="OpenAI GPTBot",
        default_tracks=[Track.ACCESS_CONTROLS],
        tier=SourceTier.PRIMARY,
        role=SourceRole.PLATFORM_DOCS,
    )


async def test_analyzer_returns_four_layer_editorial_result(fake_model, crawler_source):
    fake_model.generate.return_value = AnalyzerResponse(
        change_kind="material",
        importance=0.8,
        title="OpenAI adds Operator UA string",
        summary="GPTBot documentation now lists another automated client.",
        insight="Search and training clients are becoming distinct.",
        implication="Publishers can apply separate access policies.",
        why_it_matters="One robots.txt decision no longer covers every OpenAI product.",
        key_facts=["  OpenAI listed  a new\nuser agent. ", "", "It applies to Operator."],
        primary_track="search-discovery",
        tracks=["search-discovery", "access-controls"],
        actors=["Cloudflare", "Totally Unknown Inc"],
        subject="agent",
        protocols=["Web Bot Auth", "Imaginary Protocol"],
        trend_signals=["training-search-separation"],
        confidence="high",
    )

    result = await analyze_change(
        model=fake_model,
        source=crawler_source,
        prev_content="old doc",
        curr_content="new doc",
        unified_diff="-x\n+y",
    )

    assert isinstance(result, AnalysisResult)
    assert result.summary.startswith("GPTBot documentation")
    assert result.insight == "Search and training clients are becoming distinct."
    assert result.key_facts == ["OpenAI listed a new user agent.", "It applies to Operator."]
    # End-to-end wiring of the five new AnalysisResult fields through analyze_change.
    # Both actors and protocols carry one known registry name and one name that is
    # definitely absent from the registries, so swapping unknown_players with
    # unknown_protocols (or players with protocols) in the AnalysisResult
    # construction would make one of these four assertions fail.
    assert result.subject is Subject.AGENT
    assert result.players == ["cloudflare"]
    assert result.protocols == ["web-bot-auth"]
    assert result.unknown_players == ["Totally Unknown Inc"]
    assert result.unknown_protocols == ["Imaginary Protocol"]
    assert result.implication == "Publishers can apply separate access policies."
    assert result.why_it_matters.startswith("One robots.txt")
    assert result.primary_track is Track.SEARCH_DISCOVERY
    assert result.tracks == [Track.SEARCH_DISCOVERY, Track.ACCESS_CONTROLS]
    assert result.confidence == "high"


async def test_analyzer_falls_back_to_source_track_for_invalid_classification(
    fake_model, crawler_source
):
    fake_model.generate.return_value = AnalyzerResponse(
        change_kind="material",
        importance=0.7,
        title="Unclassifiable update",
        summary="A change occurred.",
        insight="The classification was malformed.",
        implication="Requires review.",
        why_it_matters="A human should inspect the evidence.",
        primary_track="not-a-track",
        tracks=["not-a-track"],
        actors=[],
        trend_signals=[],
        confidence="high",
    )

    result = await analyze_change(
        model=fake_model,
        source=crawler_source,
        prev_content="old",
        curr_content="new",
        unified_diff="-old\n+new",
    )

    assert result.primary_track is Track.ACCESS_CONTROLS
    assert result.tracks == [Track.ACCESS_CONTROLS]
    assert result.confidence == "low"


def test_analysis_result_accepts_legacy_what_changed_input():
    result = AnalysisResult(
        change_kind="material",
        importance=0.6,
        title="Compatible result",
        what_changed="Legacy summary.",
        implication="Legacy implication.",
        primary_track=Track.ACCESS_CONTROLS,
        tracks=[Track.ACCESS_CONTROLS],
        actors=[],
        trend_signals=[],
        confidence="medium",
    )

    assert result.summary == "Legacy summary."
    assert result.what_changed == "Legacy summary."
    assert result.why_it_matters == "Legacy implication."


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
