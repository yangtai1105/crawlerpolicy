from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.relevance import RelevanceVerdict, keyword_match, model_relevance


def test_keyword_match_case_insensitive():
    assert keyword_match("AI Bots are evolving", ["AI bot"]) is True
    assert keyword_match("we launched a new firewall", ["AI bot", "crawler"]) is False


def test_keyword_match_substring():
    assert keyword_match("trainingdata policies", ["training data"]) is False
    assert keyword_match("training data policies", ["training data"]) is True


def test_keyword_match_empty_list_returns_true():
    assert keyword_match("anything", []) is True


@pytest.fixture
def fake_model():
    model = MagicMock()
    model.generate = AsyncMock()
    return model


async def test_model_relevance_returns_structured_verdict(fake_model):
    fake_model.generate.return_value = RelevanceVerdict(
        is_relevant=True,
        reason="Discusses GPTBot opt-out",
    )

    verdict = await model_relevance(
        fake_model,
        "Cloudflare launches AI bot audit",
        "A new crawler control is available.",
    )

    assert verdict.is_relevant is True
    assert "GPTBot" in verdict.reason


async def test_model_relevance_preserves_negative_verdict(fake_model):
    fake_model.generate.return_value = RelevanceVerdict(
        is_relevant=False,
        reason="Unrelated product",
    )

    verdict = await model_relevance(
        fake_model,
        "Dashboard widgets",
        "A visual dashboard update.",
    )

    assert verdict == RelevanceVerdict(is_relevant=False, reason="Unrelated product")
