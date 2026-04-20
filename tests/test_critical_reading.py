"""Tests for the Weekly Dispatch URL-grounding logic.

Gemini's grounded-search response ships *two* things: the JSON body (title/
frame/quote/tag/kind — editorial fields only) and
``grounding_metadata.grounding_chunks`` (the real grounded URIs).

The matcher here pairs each Gemini item to its grounded citation by
title-token overlap, then fills in ``url`` and ``source_domain`` from the
matched citation. If no grounded citation shares enough tokens with an
item's title, the item is dropped rather than shipped with a hallucinated
or wrong URL.
"""
from __future__ import annotations

from pipeline.critical_reading import (
    _collect_grounding_citations,
    _map_items_to_grounded_citations,
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


def test_map_fills_url_and_source_domain_from_matched_citation():
    items = [
        {
            "tag": "#Canonicalization",
            "title": "Redirects for AI Training enforces canonical content",
            "frame": "Cloudflare announces canonical redirects for AI crawlers.",
            "quote": "...",
            "kind": "field-report",
            "topic": "Crawling & Publisher Controls",
        }
    ]
    grounded = [
        ("Redirects for AI Training enforces canonical content - The Cloudflare Blog",
         "https://blog.cloudflare.com/ai-redirects/"),
    ]
    out = _map_items_to_grounded_citations(items, grounded)
    assert len(out) == 1
    assert out[0]["url"] == "https://blog.cloudflare.com/ai-redirects/"
    assert out[0]["source_domain"] == "blog.cloudflare.com"
    # Editorial fields preserved.
    assert out[0]["tag"] == "#Canonicalization"
    assert out[0]["topic"] == "Crawling & Publisher Controls"


def test_map_picks_best_title_overlap_across_unrelated_citations():
    items = [
        {
            "tag": "#AgentSecurity",
            "title": "Enterprise AI Agent Security Survey shows widespread incidents",
            "frame": "...",
        }
    ]
    grounded = [
        ("Unrelated story about weather radar forecasts",
         "https://weather.example/forecast"),
        ("Enterprise AI Agent Security Survey Report",
         "https://cloudsecurityalliance.org/survey"),
        ("Crypto market update",
         "https://crypto.example/market"),
    ]
    out = _map_items_to_grounded_citations(items, grounded)
    assert out[0]["url"] == "https://cloudsecurityalliance.org/survey"
    assert out[0]["source_domain"] == "cloudsecurityalliance.org"


def test_map_matches_even_when_domain_differs_from_what_gemini_would_guess():
    # The gemini-prior fix was domain-strict; this case failed there.
    # Here we verify title-overlap matching succeeds even if Gemini never
    # claimed the grounded citation's domain as its own.
    items = [
        {
            "tag": "#AgentFailure",
            "title": "Why agentic AI deployments are failing before they scale",
            "frame": "...",
        }
    ]
    grounded = [
        ("Why Agentic A.I. Deployments Are Failing Before They Scale - Observer",
         "https://observer.com/2026/04/agentic-ai-scale-failures/"),
    ]
    out = _map_items_to_grounded_citations(items, grounded)
    assert out[0]["url"] == "https://observer.com/2026/04/agentic-ai-scale-failures/"
    assert out[0]["source_domain"] == "observer.com"


def test_map_drops_item_when_no_citation_overlaps_enough():
    items = [
        {"title": "Some completely unrelated headline about gardening tips", "frame": "."}
    ]
    grounded = [
        ("AI crawler enforcement becomes stricter in Q2", "https://example.com/ai"),
    ]
    assert _map_items_to_grounded_citations(items, grounded) == []


def test_map_respects_min_overlap_threshold():
    # Only 1 shared meaningful token: "crawlers". Default threshold is 2,
    # so this should drop.
    items = [{"title": "New research on AI crawlers", "frame": "."}]
    grounded = [("Something about crawlers today", "https://example.com/x")]
    assert _map_items_to_grounded_citations(items, grounded) == []
    # With relaxed threshold, accept it.
    out = _map_items_to_grounded_citations(items, grounded, min_overlap=1)
    assert len(out) == 1


def test_map_matches_via_url_slug_when_grounded_title_is_redirect_uri():
    # Real failure mode: grounding_metadata's `web.title` is sometimes
    # just the redirect URI. The resolved URL's slug still carries the
    # headline and is enough for token matching.
    items = [
        {"title": "Why agentic AI deployments are failing before they scale"}
    ]
    grounded = [
        (
            "https://vertexaisearch.cloud.google.com/grounding-api-redirect/xyz",
            "https://observer.com/2026/04/why-agentic-ai-deployments-are-failing-before-they-scale/",
        ),
    ]
    out = _map_items_to_grounded_citations(items, grounded)
    assert out[0]["url"].endswith("failing-before-they-scale/")
    assert out[0]["source_domain"] == "observer.com"


def test_map_drops_items_with_empty_title():
    items = [{"title": "", "frame": "."}]
    grounded = [("x", "https://example.com/x")]
    assert _map_items_to_grounded_citations(items, grounded) == []


def test_map_returns_empty_when_no_grounded_citations():
    items = [{"title": "Real headline with plenty of tokens", "frame": "."}]
    assert _map_items_to_grounded_citations(items, []) == []


def test_map_strips_www_in_derived_source_domain():
    items = [{"title": "Reuters reports new AI crawler guidance this week"}]
    grounded = [("Reuters reports new AI crawler guidance this week",
                 "https://www.reuters.com/tech/article/123")]
    out = _map_items_to_grounded_citations(items, grounded)
    assert out[0]["source_domain"] == "reuters.com"
