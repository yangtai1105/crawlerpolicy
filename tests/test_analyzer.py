from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.analyzer import AnalysisResult, analyze_change
from pipeline.sources import Pillar, Source, SourceType


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
        pillar=Pillar.CRAWLER,
        type=SourceType.HTML_PAGE,
        url="https://x",
        display_name="OpenAI GPTBot",
    )


async def test_analyzer_returns_structured_result_for_crawler_change(fake_client, crawler_source):
    fake_client.messages.create.return_value = _tool_response(
        {
            "change_kind": "material",
            "importance": 0.80,
            "title": "OpenAI adds Operator UA string",
            "what_changed": "GPTBot docs now list a second UA for Operator.",
            "implication": "",
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


async def test_analyzer_cosmetic_change(fake_client, crawler_source):
    fake_client.messages.create.return_value = _tool_response(
        {
            "change_kind": "cosmetic",
            "importance": 0.1,
            "title": "Typo fix",
            "what_changed": "Fixed a typo.",
            "implication": "",
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
