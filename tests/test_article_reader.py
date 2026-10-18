import json

import httpx
import pytest

import pipeline.article_reader as reader_module
from pipeline.article_reader import extract_article

BODY = "Meta removed language from its terms of service. " * 20


def _paywalled_page() -> str:
    ld = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": "Meta removes scraping language",
        "isAccessibleForFree": False,
        "articleBody": BODY,
    }
    return (
        "<html><head><title>Meta | The Verge</title>"
        f'<script type="application/ld+json">{json.dumps(ld)}</script></head>'
        "<body><article><p>Subscribe to keep reading.</p></article></body></html>"
    )


def _plain_page() -> str:
    paragraphs = "".join(f"<p>{'Google expanded its News AI pilot. ' * 8}</p>" for _ in range(6))
    return (
        "<html><head><title>Nieman Lab</title></head>"
        f"<body><article>{paragraphs}</article></body></html>"
    )


def test_json_ld_body_wins_over_paywalled_dom():
    method, title, text = extract_article(_paywalled_page())
    assert method == "json-ld"
    assert title == "Meta removes scraping language"
    assert text.startswith("Meta removed language")


def test_readability_is_used_without_json_ld():
    method, _title, text = extract_article(_plain_page())
    assert method == "readability"
    assert "News AI pilot" in text


@pytest.fixture
def real_reader(monkeypatch):
    monkeypatch.undo()
    return reader_module.read_linked_articles


def _client(routes):
    def handler(request: httpx.Request) -> httpx.Response:
        key = str(request.url)
        if key not in routes:
            return httpx.Response(404)
        return httpx.Response(200, text=routes[key], headers={"content-type": "text/html"})

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_reads_articles_skips_x_and_records_metadata_only(real_reader):
    client = _client(
        {
            "https://www.theverge.com/robots.txt": "User-agent: *\nAllow: /\n",
            "https://www.theverge.com/a": _paywalled_page(),
        }
    )
    articles, log = await real_reader(
        ["https://x.com/verge/status/1", "https://www.theverge.com/a"], client=client
    )
    assert [article.method for article in articles] == ["json-ld"]
    assert log[0]["method"] == "json-ld"
    assert log[0]["chars"] == len(articles[0].text)
    assert "text" not in log[0]


async def test_robots_disallow_and_thin_pages_are_logged_not_raised(real_reader):
    client = _client(
        {
            "https://blocked.example/robots.txt": "User-agent: *\nDisallow: /\n",
            "https://thin.example/robots.txt": "",
            "https://thin.example/a": "<html><body><p>Sign in</p></body></html>",
        }
    )
    articles, log = await real_reader(
        ["https://blocked.example/a", "https://thin.example/a"], client=client
    )
    assert articles == []
    assert "robots.txt" in log[0]["error"]
    assert "no article body" in log[1]["error"]
