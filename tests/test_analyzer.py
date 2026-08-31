from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.analyzer import AnalysisResult, AnalyzerResponse, analyze_change
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Track


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
        default_tracks=[Track.CRAWLER_CONTROLS],
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
        primary_track="search-discovery",
        tracks=["search-discovery", "crawler-controls"],
        actors=["OpenAI", "publishers"],
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
    assert result.implication == "Publishers can apply separate access policies."
    assert result.why_it_matters.startswith("One robots.txt")
    assert result.primary_track is Track.SEARCH_DISCOVERY
    assert result.tracks == [Track.SEARCH_DISCOVERY, Track.CRAWLER_CONTROLS]
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

    assert result.primary_track is Track.CRAWLER_CONTROLS
    assert result.tracks == [Track.CRAWLER_CONTROLS]
    assert result.confidence == "low"


def test_analysis_result_accepts_legacy_what_changed_input():
    result = AnalysisResult(
        change_kind="material",
        importance=0.6,
        title="Compatible result",
        what_changed="Legacy summary.",
        implication="Legacy implication.",
        primary_track=Track.CRAWLER_CONTROLS,
        tracks=[Track.CRAWLER_CONTROLS],
        actors=[],
        trend_signals=[],
        confidence="medium",
    )

    assert result.summary == "Legacy summary."
    assert result.what_changed == "Legacy summary."
    assert result.why_it_matters == "Legacy implication."
