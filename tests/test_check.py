"""Smoke-level orchestration test: one html_page source, one change → one event."""
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import yaml

from pipeline.analyzer import AnalysisResult
from pipeline.check import preflight_dependency_errors, run_check
from pipeline.evidence import EvidenceStage, pending_analysis
from pipeline.fetchers.base import CandidateItem, FetchResult, ResultMode
from pipeline.model_provider import ProviderFailure
from pipeline.sources import load_sources
from pipeline.taxonomy import Track


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "content" / "snapshots").mkdir(parents=True)
    (tmp_path / "content" / "events").mkdir(parents=True)
    (tmp_path / "data").mkdir(parents=True)
    (tmp_path / "state").mkdir(parents=True)
    (tmp_path / "sources.yaml").write_text(
        yaml.safe_dump(
            [
                {
                    "slug": "gptbot",
                    "type": "html_page",
                    "url": "https://platform.openai.com/docs/gptbot",
                    "display_name": "OpenAI GPTBot",
                    "default_tracks": ["crawler-controls"],
                    "tier": "primary",
                    "role": "platform-docs",
                    "required_for_coverage": True,
                }
            ]
        )
    )
    return tmp_path


async def test_new_source_first_run_is_catchup_no_event(repo):
    fetch = AsyncMock(
        return_value=FetchResult(
            mode=ResultMode.DIFFABLE, normalized_content="v1", raw_ext="html"
        )
    )
    analyze = AsyncMock()
    now = datetime(2026, 8, 30, 8, tzinfo=UTC)

    await run_check(
        repo_root=repo,
        now=now,
        fetch_dispatch=lambda s, state: fetch(s),
        analyze_change=analyze,
        extract_sop=AsyncMock(),
        only=None,
        dry_run=False,
    )

    events = list((repo / "content" / "events").glob("*.md"))
    assert events == []
    snaps = list((repo / "content" / "snapshots" / "gptbot").glob("*.html"))
    assert len(snaps) == 1
    analyze.assert_not_called()


async def test_subsequent_change_emits_event(repo):
    (repo / "content" / "snapshots" / "gptbot").mkdir(parents=True)
    (repo / "content" / "snapshots" / "gptbot" / "2026-08-29.html").write_text("v1")
    (repo / "state" / "gptbot.json").write_text(
        '{"last_checked_at": "2026-08-29T00:00:00+00:00", "last_hash": "'
        + hashlib.sha256(b"v1").hexdigest()
        + '", "last_seen_guids": [], "consecutive_failures": 0, "first_seen": false}'
    )

    fetch = AsyncMock(
        return_value=FetchResult(
            mode=ResultMode.DIFFABLE, normalized_content="v2 updated", raw_ext="html"
        )
    )
    analyze = AsyncMock(
        return_value=AnalysisResult(
            change_kind="material",
            importance=0.85,
                title="GPTBot adds section",
                what_changed="Added.",
                implication="Important.",
                primary_track=Track.CRAWLER_CONTROLS,
                tracks=[Track.CRAWLER_CONTROLS],
                actors=["OpenAI"],
                trend_signals=[],
                confidence="high",
            )
    )
    now = datetime(2026, 8, 30, 8, tzinfo=UTC)

    await run_check(
        repo_root=repo,
        now=now,
        fetch_dispatch=lambda s, state: fetch(s),
        analyze_change=analyze,
        extract_sop=AsyncMock(),
        only=None,
        dry_run=False,
    )

    events = list((repo / "content" / "events").glob("*.md"))
    feed_items = list((repo / "content" / "feed").glob("*.md"))
    assert len(events) == 1
    assert len(feed_items) == 1
    assert "status: verified" in feed_items[0].read_text()
    assert "gptbot-gptbot-adds-section" in events[0].name
    analyze.assert_called_once()


async def test_analysis_failure_saves_evidence_and_replays_without_refetching_history(repo):
    (repo / "content" / "snapshots" / "gptbot").mkdir(parents=True)
    (repo / "content" / "snapshots" / "gptbot" / "2026-08-29.html").write_text("v1")
    (repo / "state" / "gptbot.json").write_text(
        '{"last_checked_at": "2026-08-29T00:00:00+00:00", "last_hash": "'
        + hashlib.sha256(b"v1").hexdigest()
        + '", "last_seen_guids": [], "consecutive_failures": 0, "first_seen": false}'
    )
    fetch = AsyncMock(
        return_value=FetchResult(
            mode=ResultMode.DIFFABLE,
            normalized_content="v2 updated",
            raw_ext="html",
        )
    )
    failed_analyze = AsyncMock(side_effect=RuntimeError("provider down"))
    first_now = datetime(2026, 8, 30, 8, tzinfo=UTC)

    first_health = await run_check(
        repo_root=repo,
        now=first_now,
        fetch_dispatch=lambda source, state: fetch(source),
        analyze_change=failed_analyze,
        only=None,
        dry_run=False,
    )

    queued = pending_analysis(repo / "content" / "evidence")
    assert len(queued) == 1
    assert queued[0][1].stage is EvidenceStage.FAILED_ANALYSIS
    assert queued[0][1].analysis_attempts == 1
    assert first_health["status"] == "critical"
    state = (repo / "state" / "gptbot.json").read_text()
    assert hashlib.sha256(b"v2 updated").hexdigest() in state

    successful_analyze = AsyncMock(
        return_value=AnalysisResult(
            change_kind="material",
            importance=0.85,
            title="GPTBot adds section",
            what_changed="Added.",
            implication="Important.",
            primary_track=Track.CRAWLER_CONTROLS,
            tracks=[Track.CRAWLER_CONTROLS],
            actors=["OpenAI"],
            trend_signals=[],
            confidence="high",
        )
    )
    second_health = await run_check(
        repo_root=repo,
        now=datetime(2026, 8, 31, 8, tzinfo=UTC),
        fetch_dispatch=lambda source, state: fetch(source),
        analyze_change=successful_analyze,
        only=None,
        dry_run=False,
    )

    assert pending_analysis(repo / "content" / "evidence") == []
    replayed = list((repo / "content" / "evidence" / "gptbot").glob("*.json"))
    assert len(replayed) == 1
    assert EvidenceStage.PUBLISHED.value in replayed[0].read_text()
    assert len(list((repo / "content" / "events").glob("*.md"))) == 1
    assert second_health["status"] == "healthy"


def test_preflight_maps_missing_credentials_to_affected_stage():
    sources = load_sources(Path("sources.yaml"))
    blockers = preflight_dependency_errors(
        sources,
        {
            "GEMINI_API_KEY": "",
            "CLOUDFLARE_ACCOUNT_ID": "account",
            "CLOUDFLARE_EMAIL": "email@example.com",
            "CLOUDFLARE_CRAWLER_API_KEY": "key",
        },
    )

    assert "gemini-agent-infra" not in blockers
    assert blockers["gptbot"].stage == "analysis"
    assert "GEMINI_API_KEY" in blockers["gptbot"].message
    assert blockers["meta-externalagent"].stage == "analysis"


def _write_item_source(repo, *, tier="specialist"):
    (repo / "sources.yaml").write_text(
        yaml.safe_dump(
            [
                {
                    "slug": "ecosystem-report",
                    "type": "rss_feed",
                    "url": "https://example.test/feed.xml",
                    "display_name": "Ecosystem Report",
                    "default_tracks": ["agentic-web"],
                    "tier": tier,
                    "role": "reporting",
                }
            ]
        )
    )


def _item(guid: str, published_at: datetime) -> CandidateItem:
    return CandidateItem(
        guid=guid,
        title=f"Item {guid}",
        published_at=published_at,
        url=f"https://example.test/{guid}",
        summary="A material agent ecosystem development.",
        body="A material agent ecosystem development with evidence.",
    )


def _material_analysis() -> AnalysisResult:
    return AnalysisResult(
        change_kind="material",
        importance=0.72,
        title="Agent identity becomes deployable",
        summary="A deployable identity control was announced.",
        insight="Agent identity is moving into infrastructure.",
        implication="Sites can distinguish accountable agents.",
        why_it_matters="Machine access can become specific and auditable.",
        primary_track=Track.AGENTIC_WEB,
        tracks=[Track.AGENTIC_WEB],
        actors=["Example"],
        trend_signals=[],
        confidence="high",
    )


async def test_pre_cutoff_item_is_not_analyzed_or_published(repo):
    _write_item_source(repo)
    analyze = AsyncMock(return_value=_material_analysis())
    old_item = _item("old", datetime(2026, 8, 29, 23, tzinfo=UTC))

    await run_check(
        repo_root=repo,
        now=datetime(2026, 8, 30, 8, tzinfo=UTC),
        fetch_dispatch=AsyncMock(
            return_value=FetchResult(mode=ResultMode.PER_ITEM, items=[old_item])
        ),
        analyze_change=analyze,
    )

    analyze.assert_not_awaited()
    assert list((repo / "content" / "feed").glob("*.md")) == []
    evidence = list((repo / "content" / "evidence").glob("*/*.json"))
    assert len(evidence) == 1
    assert EvidenceStage.SKIPPED_CUTOFF.value in evidence[0].read_text()


async def test_reported_item_writes_feed_without_development(repo):
    _write_item_source(repo, tier="specialist")
    current = _item("current", datetime(2026, 8, 30, 7, tzinfo=UTC))

    health = await run_check(
        repo_root=repo,
        now=datetime(2026, 8, 30, 8, tzinfo=UTC),
        fetch_dispatch=AsyncMock(
            return_value=FetchResult(mode=ResultMode.PER_ITEM, items=[current])
        ),
        analyze_change=AsyncMock(return_value=_material_analysis()),
    )

    feed_items = list((repo / "content" / "feed").glob("*.md"))
    assert len(feed_items) == 1
    assert "status: reported" in feed_items[0].read_text()
    assert list((repo / "content" / "events").glob("*.md")) == []
    assert health["feed_items_written"] == [
        str(feed_items[0].relative_to(repo))
    ]


async def test_fatal_provider_failure_opens_circuit_and_preserves_pending(repo):
    _write_item_source(repo, tier="primary")
    analyze = AsyncMock(side_effect=ProviderFailure("billing", "credit exhausted"))
    items = [
        _item("one", datetime(2026, 8, 30, 6, tzinfo=UTC)),
        _item("two", datetime(2026, 8, 30, 7, tzinfo=UTC)),
    ]

    health = await run_check(
        repo_root=repo,
        now=datetime(2026, 8, 30, 8, tzinfo=UTC),
        fetch_dispatch=AsyncMock(
            return_value=FetchResult(mode=ResultMode.PER_ITEM, items=items)
        ),
        analyze_change=analyze,
    )

    assert analyze.await_count == 1
    assert len(pending_analysis(repo / "content" / "evidence")) == 2
    assert health["provider"] == {
        "name": "gemini",
        "status": "blocked",
        "error": "credit exhausted",
    }


def _add_x_source(repo, *, shadow: bool = True) -> None:
    sources = yaml.safe_load((repo / "sources.yaml").read_text())
    sources.append(
        {
            "slug": "x-access-discovery",
            "type": "xai_search",
            "query": "Find consequential crawler policy changes.",
            "x_handles": ["Cloudflare"],
            "lookback_hours": 36,
            "shadow": shadow,
            "display_name": "X — Access & Discovery",
            "default_tracks": ["crawler-controls"],
            "tier": "commentary",
            "role": "reporting",
        }
    )
    (repo / "sources.yaml").write_text(yaml.safe_dump(sources))


def _x_item() -> CandidateItem:
    post_url = "https://x.com/Cloudflare/status/2031535503443374365"
    return CandidateItem(
        guid="2031535503443374365",
        title="Cloudflare changes crawler controls",
        published_at=datetime(2026, 9, 3, 4, tzinfo=UTC),
        url=post_url,
        summary="Cloudflare announced a concrete crawler-control change.",
        body="A concrete crawler-control change was announced.",
        metadata={
            "author_handle": "Cloudflare",
            "post_url": post_url,
            "linked_urls": ["https://blog.cloudflare.com/example"],
            "provider_citations": [post_url],
        },
    )


def test_preflight_maps_missing_xai_key_only_to_x_sources(repo):
    _add_x_source(repo)
    sources = load_sources(repo / "sources.yaml")

    blockers = preflight_dependency_errors(
        sources,
        {
            "GEMINI_API_KEY": "gemini-test",
            "XAI_API_KEY": "",
            "CLOUDFLARE_ACCOUNT_ID": "account",
            "CLOUDFLARE_EMAIL": "email@example.com",
            "CLOUDFLARE_CRAWLER_API_KEY": "key",
        },
    )

    assert blockers["x-access-discovery"].stage == "fetch"
    assert blockers["x-access-discovery"].message == "XAI_API_KEY is missing"
    assert "gptbot" not in blockers


async def test_shadow_x_candidate_is_saved_without_gemini_or_publication(repo):
    _add_x_source(repo)
    analyze = AsyncMock()

    async def fetch(source, _state):
        if source.slug == "x-access-discovery":
            return FetchResult(
                mode=ResultMode.PER_ITEM,
                items=[_x_item()],
                metadata={
                    "x_search_calls": 1,
                    "estimated_tool_cost_usd": 0.005,
                    "model": "grok-4.6",
                },
            )
        return FetchResult(mode=ResultMode.DIFFABLE, normalized_content="baseline")

    health = await run_check(
        repo_root=repo,
        now=datetime(2026, 9, 3, 8, tzinfo=UTC),
        fetch_dispatch=fetch,
        analyze_change=analyze,
    )

    records = list((repo / "content/evidence/x-access-discovery").glob("*.json"))
    assert len(records) == 1
    assert '"stage": "analyzed"' in records[0].read_text()
    assert '"shadow": true' in records[0].read_text()
    assert '"supporting_urls"' in records[0].read_text()
    assert list((repo / "content/feed").glob("*.md")) == []
    analyze.assert_not_awaited()
    assert health["discovery"] == {
        "status": "shadow",
        "candidate_count": 1,
        "x_search_calls": 1,
        "estimated_tool_cost_usd": 0.005,
        "sources_configured": 1,
        "sources_completed": 1,
        "sources_failed": 0,
        "sources_skipped_by_cap": 0,
    }


async def test_missing_xai_key_degrades_without_making_core_run_critical(repo):
    _add_x_source(repo)
    sources = load_sources(repo / "sources.yaml")
    blockers = preflight_dependency_errors(
        sources,
        {"GEMINI_API_KEY": "gemini-test", "XAI_API_KEY": ""},
    )

    health = await run_check(
        repo_root=repo,
        now=datetime(2026, 9, 3, 8, tzinfo=UTC),
        fetch_dispatch=AsyncMock(
            return_value=FetchResult(
                mode=ResultMode.DIFFABLE,
                normalized_content="baseline",
            )
        ),
        analyze_change=AsyncMock(),
        dependency_blockers=blockers,
    )

    assert health["status"] == "degraded"
    assert health["discovery"]["status"] == "unavailable"
    assert health["coverage"]["required_failed"] == 0


async def test_non_shadow_x_candidate_publishes_signal_with_attribution(repo):
    (repo / "sources.yaml").write_text("[]\n")
    _add_x_source(repo, shadow=False)

    health = await run_check(
        repo_root=repo,
        now=datetime(2026, 9, 3, 8, tzinfo=UTC),
        fetch_dispatch=AsyncMock(
            return_value=FetchResult(
                mode=ResultMode.PER_ITEM,
                items=[_x_item()],
                metadata={"x_search_calls": 1, "estimated_tool_cost_usd": 0.005},
            )
        ),
        analyze_change=AsyncMock(return_value=_material_analysis()),
    )

    feed_items = list((repo / "content/feed").glob("*.md"))
    assert len(feed_items) == 1
    text = feed_items[0].read_text()
    assert "status: signal" in text
    assert "https://x.com/Cloudflare/status/2031535503443374365" in text
    assert "https://blog.cloudflare.com/example" in text
    assert list((repo / "content/events").glob("*.md")) == []
    assert health["discovery"]["status"] == "live"
