from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.relevance import haiku_relevance, keyword_match


def test_keyword_match_case_insensitive():
    assert keyword_match("AI Bots are evolving", ["AI bot"]) is True
    assert keyword_match("we launched a new firewall", ["AI bot", "crawler"]) is False


def test_keyword_match_substring():
    assert keyword_match("trainingdata policies", ["training data"]) is False
    assert keyword_match("training data policies", ["training data"]) is True


def test_keyword_match_empty_list_returns_true():
    assert keyword_match("anything", []) is True


class _FakeMessage:
    def __init__(self, text: str):
        self.content = [MagicMock(text=text)]


@pytest.fixture
def fake_client():
    client = MagicMock()
    client.messages.create = AsyncMock()
    return client


async def test_haiku_returns_relevant(fake_client):
    fake_client.messages.create.return_value = _FakeMessage(
        '{"is_relevant": true, "reason": "Discusses GPTBot opt-out"}'
    )
    v = await haiku_relevance(fake_client, "Cloudflare launches AI bot audit", "...")
    assert v.is_relevant is True
    assert "GPTBot" in v.reason


async def test_haiku_returns_not_relevant(fake_client):
    fake_client.messages.create.return_value = _FakeMessage(
        '{"is_relevant": false, "reason": "Unrelated product"}'
    )
    v = await haiku_relevance(fake_client, "We launched new dashboard widgets", "...")
    assert v.is_relevant is False
