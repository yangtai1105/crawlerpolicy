"""Tests for the Weekly Dispatch URL-grounding logic.

Gemini's grounded-search response ships *two* things: the JSON body (which
can hallucinate publisher URLs) and `grounding_metadata.grounding_chunks`
(which contain the real grounded URIs). These tests cover the pure logic
that extracts grounding citations and maps each Gemini item back to its
real grounded URL by source_domain.
"""
from __future__ import annotations

from pipeline.critical_reading import (
    _collect_grounding_citations,
    _map_items_to_grounded_urls,
)


class _FakeWeb:
    def __init__(self, uri: str, title: str):
        self.uri = uri
        self.title = title


class _FakeChunk:
    def __init__(self, uri: str, title: str = ""):
        self.web = _FakeWeb(uri, title)


class _FakeMeta:
    def __init__(self, chunks: list[_FakeChunk]):
        self.grounding_chunks = chunks


class _FakeCandidate:
    def __init__(self, chunks: list[_FakeChunk]):
        self.grounding_metadata = _FakeMeta(chunks)


class _FakeResp:
    def __init__(self, chunks: list[_FakeChunk]):
        self.candidates = [_FakeCandidate(chunks)]


def test_collect_grounding_citations_dedupes_and_skips_empty_uris():
    resp = _FakeResp(
        [
            _FakeChunk("https://vertexaisearch.cloud.google.com/grounding-api-redirect/abc", "Cloudflare canonical"),
            _FakeChunk("https://vertexaisearch.cloud.google.com/grounding-api-redirect/abc", "dup of above"),
            _FakeChunk("", "no uri, should skip"),
            _FakeChunk("https://vertexaisearch.cloud.google.com/grounding-api-redirect/xyz", "Digiday report"),
        ]
    )
    out = _collect_grounding_citations(resp)
    assert [u for _, u in out] == [
        "https://vertexaisearch.cloud.google.com/grounding-api-redirect/abc",
        "https://vertexaisearch.cloud.google.com/grounding-api-redirect/xyz",
    ]
    assert out[0][0] == "Cloudflare canonical"


def test_collect_grounding_citations_handles_missing_metadata():
    class _NoMeta:
        grounding_metadata = None

    class _Resp:
        candidates = [_NoMeta()]

    assert _collect_grounding_citations(_Resp()) == []
    assert _collect_grounding_citations(object()) == []


def test_map_items_overwrites_hallucinated_url_with_grounded_url():
    items = [
        {
            "source_domain": "cloudflare.com",
            "title": "Cloudflare blog: canonicalization",
            "url": "https://hallucinated.example/fake",
            "topic": "Crawling & Publisher Controls",
        }
    ]
    grounded = [
        ("Redirects for AI Training - Cloudflare", "https://blog.cloudflare.com/redirects-for-ai-training"),
    ]
    out = _map_items_to_grounded_urls(items, grounded)
    assert len(out) == 1
    assert out[0]["url"] == "https://blog.cloudflare.com/redirects-for-ai-training"
    assert out[0]["topic"] == "Crawling & Publisher Controls"


def test_map_items_drops_items_with_no_matching_grounded_domain():
    items = [
        {"source_domain": "apnews.com", "title": "Unrelated", "url": "https://apnews.com/fake-000"},
        {"source_domain": "cloudflare.com", "title": "Cloudflare", "url": "https://cf.example/fake"},
    ]
    grounded = [("CF canonical post", "https://blog.cloudflare.com/real")]
    out = _map_items_to_grounded_urls(items, grounded)
    assert [it["source_domain"] for it in out] == ["cloudflare.com"]
    assert out[0]["url"] == "https://blog.cloudflare.com/real"


def test_map_items_breaks_ties_by_title_overlap():
    items = [
        {
            "source_domain": "digiday.com",
            "title": "New data shows publishers face growing AI bot scraper activity",
            "url": "https://fake",
        }
    ]
    grounded = [
        ("Totally unrelated Digiday headline about advertising", "https://digiday.com/ads/unrelated"),
        (
            "In Graphic Detail: data shows publishers face growing AI bot scraper activity",
            "https://digiday.com/media/real",
        ),
    ]
    out = _map_items_to_grounded_urls(items, grounded)
    assert out[0]["url"] == "https://digiday.com/media/real"


def test_map_items_strips_www_and_is_case_insensitive():
    items = [{"source_domain": "Reuters.com", "title": "x", "url": "fake"}]
    grounded = [("Reuters story", "https://www.reuters.com/article/123")]
    out = _map_items_to_grounded_urls(items, grounded)
    assert len(out) == 1
    assert out[0]["url"] == "https://www.reuters.com/article/123"


def test_map_items_drops_item_with_missing_source_domain():
    items = [{"source_domain": "", "title": "x", "url": "fake"}]
    grounded = [("any", "https://example.com/a")]
    assert _map_items_to_grounded_urls(items, grounded) == []


def test_map_items_returns_empty_when_no_grounded_citations():
    items = [{"source_domain": "cloudflare.com", "title": "x", "url": "https://cf.example/fake"}]
    assert _map_items_to_grounded_urls(items, []) == []
