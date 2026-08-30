from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.analyzer import AnalysisResult, analyze_change
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Track


@pytest.fixture
def fake_client():
    client = MagicMock()
    client.messages.create = AsyncMock()
    return client


def _tool_response(arguments: dict):
    block = MagicMock()
    block.type = "tool_use"
    block.name = "emit_analysis"
    block.input = arguments
    msg = MagicMock()
    msg.content = [block]
    msg.stop_reason = "tool_use"
    return msg


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


async def test_analyzer_returns_structured_result_for_crawler_change(fake_client, crawler_source):
    fake_client.messages.create.return_value = _tool_response(
        {
            "change_kind": "material",
            "importance": 0.80,
            "title": "OpenAI adds Operator UA string",
            "what_changed": "GPTBot docs now list a second UA for Operator.",
            "implication": "Search and training controls are separating.",
            "primary_track": "search-discovery",
            "tracks": ["search-discovery", "crawler-controls"],
            "actors": ["OpenAI", "publishers"],
            "trend_signals": ["training-search-separation"],
            "confidence": "high",
        }
    )

    result = await analyze_change(
        client=fake_client,
        source=crawler_source,
        prev_content="old doc",
        curr_content="new doc",
        unified_diff="-x\n+y",
    )

    assert isinstance(result, AnalysisResult)
    assert result.change_kind == "material"
    assert result.importance == 0.80
    assert result.title.startswith("OpenAI adds")
    assert result.primary_track is Track.SEARCH_DISCOVERY
    assert result.tracks == [Track.SEARCH_DISCOVERY, Track.CRAWLER_CONTROLS]
    assert result.actors == ["OpenAI", "publishers"]
    assert result.trend_signals == ["training-search-separation"]
    assert result.confidence == "high"


async def test_analyzer_cosmetic_change(fake_client, crawler_source):
    fake_client.messages.create.return_value = _tool_response(
        {
            "change_kind": "cosmetic",
            "importance": 0.1,
            "title": "Typo fix",
            "what_changed": "Fixed a typo.",
            "implication": "",
            "primary_track": "crawler-controls",
            "tracks": ["crawler-controls"],
            "actors": ["OpenAI"],
            "trend_signals": [],
            "confidence": "medium",
        }
    )

    result = await analyze_change(
        client=fake_client,
        source=crawler_source,
        prev_content="old",
        curr_content="new",
        unified_diff="-typo\n+typo-fixed",
    )

    assert result.change_kind == "cosmetic"


async def test_analyzer_falls_back_to_source_track_for_invalid_tool_output(
    fake_client, crawler_source
):
    fake_client.messages.create.return_value = _tool_response(
        {
            "change_kind": "material",
            "importance": 0.7,
            "title": "Unclassifiable update",
            "what_changed": "A change occurred.",
            "implication": "Requires review.",
            "primary_track": "not-a-track",
            "tracks": ["not-a-track"],
            "actors": [],
            "trend_signals": [],
            "confidence": "high",
        }
    )

    result = await analyze_change(
        client=fake_client,
        source=crawler_source,
        prev_content="old",
        curr_content="new",
        unified_diff="-old\n+new",
    )

    assert result.primary_track is Track.CRAWLER_CONTROLS
    assert result.tracks == [Track.CRAWLER_CONTROLS]
    assert result.confidence == "low"
