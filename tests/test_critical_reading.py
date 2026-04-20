"""Tests for the Weekly Dispatch URL-grounding logic.

Anthropic's Messages API with ``web_search_20260209`` returns a mixed content
list — some blocks are ``text`` (the JSON body: title/frame/quote/tag/kind),
others are ``web_search_tool_result`` (the real publisher URLs Claude
searched). The matcher here pairs each JSON item to its grounded result by
title-token overlap, then fills in ``url`` and ``source_domain`` from the
matched result. If no grounded URL shares enough tokens with an item's title,
the item is dropped rather than shipped with a potentially-wrong link.
"""
from __future__ import annotations

from datetime import datetime, timezone

from pipeline.critical_reading import (
    _collect_grounding_citations,
    _filter_quality,
    _map_items_to_grounded_citations,
)

_NOW = datetime(2026, 4, 20, tzinfo=timezone.utc)


class _FakeSearchResult:
    def __init__(self, url: str, title: str = ""):
        self.type = "web_search_result"
        self.url = url
        self.title = title


class _FakeBlock:
    """Mimics an Anthropic content block (type + optional content list)."""
    def __init__(self, type_: str, content: list | None = None, text: str = ""):
        self.type = type_
        self.content = content or []
        self.text = text


class _FakeResp:
    def __init__(self, content: list[_FakeBlock]):
        self.content = content


def _web_search_block(results: list[_FakeSearchResult]) -> _FakeBlock:
    return _FakeBlock("web_search_tool_result", content=results)


def test_collect_grounding_citations_extracts_web_search_result_urls():
    resp = _FakeResp([
        _FakeBlock("text", text="Some preamble from Claude."),
        _web_search_block([
            _FakeSearchResult("https://blog.cloudflare.com/ai-redirects/", "Cloudflare canonical"),
            _FakeSearchResult("https://digiday.com/media/ai-bots/", "Digiday report"),
        ]),
    ])
    out = _collect_grounding_citations(resp)
    assert out == [
        ("Cloudflare canonical", "https://blog.cloudflare.com/ai-redirects/"),
        ("Digiday report", "https://digiday.com/media/ai-bots/"),
    ]


def test_collect_grounding_citations_dedupes_across_multiple_search_blocks():
    resp = _FakeResp([
        _web_search_block([_FakeSearchResult("https://example.com/a", "A")]),
        _FakeBlock("text", text="..."),
        _web_search_block([
            _FakeSearchResult("https://example.com/a", "dup"),   # duplicate URL
            _FakeSearchResult("https://example.com/b", "B"),
        ]),
    ])
    out = _collect_grounding_citations(resp)
    assert [u for _, u in out] == ["https://example.com/a", "https://example.com/b"]


def test_collect_grounding_citations_handles_missing_content():
    class _Empty:
        content = None
    assert _collect_grounding_citations(_Empty()) == []
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


def test_filter_quality_drops_old_year_in_url_path():
    items = [
        {"url": "https://example.com/2025/07/some-article", "source_domain": "example.com"},
        {"url": "https://example.com/2026/04/fresh-article", "source_domain": "example.com"},
    ]
    out = _filter_quality(items, now=_NOW)
    assert [it["url"] for it in out] == ["https://example.com/2026/04/fresh-article"]


def test_filter_quality_drops_explainer_slugs():
    items = [
        {"url": "https://reuters.com/openai-copyright-lawsuit-explained/", "source_domain": "reuters.com"},
        {"url": "https://example.com/what-is-mcp/", "source_domain": "example.com"},
        {"url": "https://example.com/how-to-block-ai-bots/", "source_domain": "example.com"},
        {"url": "https://example.com/who-owns-ai-training-data/", "source_domain": "example.com"},
        {"url": "https://reuters.com/real-lawsuit-filing", "source_domain": "reuters.com"},
    ]
    out = _filter_quality(items, now=_NOW)
    assert [it["url"] for it in out] == ["https://reuters.com/real-lawsuit-filing"]


def test_filter_quality_drops_blocked_domains():
    items = [
        {"url": "https://www.mondaq.com/unitedstates/copyright/123456/fresh", "source_domain": "mondaq.com"},
        {"url": "https://jdsupra.com/legalnews/something", "source_domain": "jdsupra.com"},
        {"url": "https://lexology.com/library/foo", "source_domain": "lexology.com"},
        {"url": "https://reuters.com/tech/article", "source_domain": "reuters.com"},
    ]
    out = _filter_quality(items, now=_NOW)
    assert [it["source_domain"] for it in out] == ["reuters.com"]


def test_filter_quality_drops_stale_published_date():
    # Default cutoff is 60 days — generous on purpose because Gemini's
    # self-reported dates are flaky.
    items = [
        {"url": "https://reuters.com/a", "source_domain": "reuters.com", "published": "2025-11-01"},  # >60d
        {"url": "https://reuters.com/b", "source_domain": "reuters.com", "published": "2026-04-15"},  # ~5d
        {"url": "https://reuters.com/c", "source_domain": "reuters.com", "published": "2026-03-10"},  # ~40d
    ]
    out = _filter_quality(items, now=_NOW)
    assert [it["url"] for it in out] == ["https://reuters.com/b", "https://reuters.com/c"]


def test_filter_quality_keeps_item_when_published_missing_and_url_clean():
    items = [
        {"url": "https://reuters.com/story-about-ai", "source_domain": "reuters.com"},  # no date
    ]
    out = _filter_quality(items, now=_NOW)
    assert len(out) == 1


def test_filter_quality_keeps_current_year_in_url():
    items = [
        {"url": "https://reuters.com/2026/04/17/story", "source_domain": "reuters.com"},
    ]
    out = _filter_quality(items, now=_NOW)
    assert len(out) == 1
