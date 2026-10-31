from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from pipeline import grounded_reader
from pipeline.model_provider import ProviderFailure

_REDIRECT = "https://vertexaisearch.cloud.google.com/grounding-api-redirect/"


@pytest.fixture(autouse=True)
def _clear_cache():
    grounded_reader._cache.clear()
    yield
    grounded_reader._cache.clear()


def _client(text: str, cited: list[str]):
    chunks = [
        SimpleNamespace(web=SimpleNamespace(uri=f"{_REDIRECT}{index}"))
        for index in range(len(cited))
    ]
    response = SimpleNamespace(
        text=text,
        candidates=[SimpleNamespace(grounding_metadata=SimpleNamespace(grounding_chunks=chunks))],
    )
    generate = AsyncMock(return_value=response)
    client = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate)))
    locations = {f"{_REDIRECT}{i}": url for i, url in enumerate(cited)}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": locations[str(request.url)]})

    return client, httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_same_article_ignores_date_segments_but_not_hosts():
    feed = "https://www.akamai.com/blog/ai/2026/oct/silent-agents-are-already-on-your-site"
    index = "https://www.akamai.com/blog/ai/silent-agents-are-already-on-your-site/"
    assert grounded_reader.same_article(feed, index)
    assert not grounded_reader.same_article(feed, "https://akamai.example/silent-agents-are-already-on-your-site")
    assert not grounded_reader.same_article("https://www.akamai.com/", "https://www.akamai.com/")


def test_listing_pages_are_not_articles():
    assert grounded_reader.is_article_url(
        "https://www.humansecurity.com/learn/blog/human-sightline-detects-claude-duet/",
        "humansecurity.com",
    )
    assert not grounded_reader.is_article_url(
        "https://www.humansecurity.com/learn/resources/", "humansecurity.com"
    )
    assert not grounded_reader.is_article_url(
        "https://reddit.com/r/x/some-thread-title", "humansecurity.com"
    )


async def test_read_article_uses_the_cited_url_and_header():
    notes = "The post says 63.2% of agentic requests carried no mouse events. " * 10
    client, http = _client(
        f"TITLE: Silent Agents Are Already on Your Site\nDATE: 2026-10-26\n\n{notes}",
        [
            "https://www.akamai.com/blog/ai/silent-agents-are-already-on-your-site",
            "https://example.substack.com/p/roundup",
        ],
    )

    read = await grounded_reader.read_article(
        "https://www.akamai.com/blog/ai/2026/oct/silent-agents-are-already-on-your-site",
        title="Silent Agents",
        model="gemini-test",
        client=client,
        http=http,
    )

    assert read.url == "https://www.akamai.com/blog/ai/silent-agents-are-already-on-your-site"
    assert read.title == "Silent Agents Are Already on Your Site"
    assert read.published_on == datetime(2026, 10, 26, tzinfo=UTC)
    assert read.text.startswith("The post says 63.2%")
    assert read.as_metadata()["cited_urls"][1] == "https://example.substack.com/p/roundup"


@pytest.mark.parametrize(
    ("text", "cited"),
    [
        ("NOT_FOUND", ["https://www.akamai.com/blog/ai/silent-agents"]),
        ("TITLE: Other\n" + "notes " * 200, ["https://www.akamai.com/blog/ai/other-post"]),
        ("TITLE: Silent\n" + "notes " * 200, ["https://news.example/silent-agents"]),
        ("TITLE: Silent\nshort", ["https://www.akamai.com/blog/ai/silent-agents"]),
    ],
)
async def test_read_article_refuses_reads_that_do_not_cite_the_article(text, cited):
    client, http = _client(text, cited)
    with pytest.raises(grounded_reader.NotIndexed):
        await grounded_reader.read_article(
            "https://www.akamai.com/blog/ai/2026/oct/silent-agents",
            model="gemini-test",
            client=client,
            http=http,
        )


async def test_provider_errors_are_classified():
    generate = AsyncMock(side_effect=RuntimeError("429 resource exhausted"))
    client = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate)))
    with pytest.raises(ProviderFailure) as raised:
        await grounded_reader.grounded_search("q", model="m", client=client)
    assert raised.value.kind == "quota"


async def test_discover_articles_keeps_one_url_per_article_on_the_domain():
    client, http = _client(
        "1. Some invented URL https://www.humansecurity.com/blog/made-up-path",
        [
            "https://www.humansecurity.com/learn/blog/human-sightline-detects-claude-duet/",
            "https://humansecurity.com/learn/blog/human-sightline-detects-claude-duet",
            "https://www.humansecurity.com/learn/resources/",
            "https://www.youtube.com/watch-some-video",
        ],
    )

    urls = await grounded_reader.discover_articles(
        "humansecurity.com", "agent posts", lookback_days=14, model="m", client=client, http=http
    )

    assert urls == ["https://www.humansecurity.com/learn/blog/human-sightline-detects-claude-duet/"]
