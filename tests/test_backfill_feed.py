from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import yaml

from pipeline.analyzer import AnalysisResult
from pipeline.backfill_feed import run_backfill
from pipeline.evidence import EvidenceRecord, save_evidence
from pipeline.model_provider import ProviderFailure
from pipeline.relevance import RelevanceVerdict
from pipeline.taxonomy import Track

SINCE = datetime(2026, 6, 1, tzinfo=UTC)
UNTIL = datetime(2026, 9, 1, 23, 59, 59, tzinfo=UTC)
NOW = datetime(2026, 9, 2, 1, tzinfo=UTC)


def material_analysis(title="Direct evidence changes crawler access"):
    return AnalysisResult(
        change_kind="material",
        importance=0.84,
        title=title,
        summary="The publisher changed its crawler access policy.",
        insight="Machine access is becoming an explicit policy surface.",
        implication="Publishers may adopt more granular controls.",
        why_it_matters="The change affects how automated clients access the web.",
        primary_track=Track.CRAWLER_CONTROLS,
        tracks=[Track.CRAWLER_CONTROLS],
        actors=["Direct Publisher"],
        trend_signals=["granular-access"],
        confidence="high",
    )


def make_repo(tmp_path, *, tier="primary", records=1, keyword_filter=None):
    repo = tmp_path
    keyword_line = (
        f"  keyword_filter: [{', '.join(keyword_filter)}]\n" if keyword_filter else ""
    )
    (repo / "sources.yaml").write_text(
        
            "- slug: direct\n"
            "  type: rss_feed\n"
            "  url: https://example.test/feed.xml\n"
            "  display_name: Direct Publisher\n"
            "  default_tracks: [crawler-controls]\n"
            f"  tier: {tier}\n"
            "  role: infrastructure\n"
            f"{keyword_line}"
            "- slug: search\n"
            "  type: gemini_search\n"
            "  query: crawler policy news\n"
            "  display_name: Search Discovery\n"
            "  default_tracks: [search-discovery]\n"
            "  tier: commentary\n"
            "  role: reporting\n"
            "  enabled: false\n"
        
    )
    published = datetime(2026, 7, 28, 16, 47, 49, tzinfo=UTC)
    for index in range(records):
        date = published - timedelta(days=index)
        save_evidence(
            repo / "content/evidence",
            EvidenceRecord(
                evidence_id=f"direct--{index}",
                source="direct",
                source_url=f"https://example.test/item-{index}",
                published_at=date,
                detected_at=date + timedelta(hours=2),
                content_path="content/raw/direct/2026-07.jsonl",
                external_id=f"item-{index}",
                title="Crawler policy release",
                content="The publisher changed crawler access terms.",
                previous_content="Old crawler access terms.",
                unified_diff="-old\n+new",
            ),
        )
    save_evidence(
        repo / "content/evidence",
        EvidenceRecord(
            evidence_id="search--excluded",
            source="search",
            source_url="https://example.test/search-result",
            published_at=published,
            detected_at=published,
            content_path="content/raw/search/2026-07.jsonl",
            external_id="search-result",
            title="Search result",
            content="An indirect discovery result.",
        ),
    )
    return repo


def runner_args(repo, **overrides):
    args = {
        "repo_root": repo,
        "since": SINCE,
        "until": UNTIL,
        "limit": 15,
        "model": AsyncMock(),
        "now": NOW,
        "relevance": AsyncMock(
            return_value=RelevanceVerdict(is_relevant=True, reason="in scope")
        ),
        "analyze": AsyncMock(return_value=material_analysis()),
    }
    args.update(overrides)
    return args


async def test_backfill_publishes_material_direct_evidence_with_original_date(tmp_path):
    repo = make_repo(tmp_path)
    summary = await run_backfill(**runner_args(repo))

    assert summary.published == 1
    feed = next((repo / "content/feed").glob("*.md")).read_text()
    assert "published_at: 2026-07-28T16:47:49+00:00" in feed
    assert "backfilled: true" in feed
    assert "backfill_batch: direct-evidence_2026-06-01_2026-09-01" in feed


async def test_backfill_excludes_search_and_is_idempotent(tmp_path):
    repo = make_repo(tmp_path)
    first = await run_backfill(**runner_args(repo))
    second = await run_backfill(**runner_args(repo))

    assert first.published == 1
    assert first.excluded == 1
    assert second.published == 0
    assert len(list((repo / "content/feed").glob("*.md"))) == 1


async def test_reported_backfill_does_not_create_development(tmp_path):
    repo = make_repo(tmp_path, tier="specialist")
    summary = await run_backfill(**runner_args(repo))

    assert summary.published == 1
    assert list((repo / "content/events").glob("*.md")) == []


async def test_blocking_provider_failure_stops_remaining_calls(tmp_path):
    repo = make_repo(tmp_path, records=2)
    analyze = AsyncMock(side_effect=ProviderFailure("quota", "resource exhausted"))
    summary = await run_backfill(**runner_args(repo, analyze=analyze))

    assert analyze.await_count == 1
    assert summary.provider_status == "blocked"
    assert summary.remaining == 2


async def test_limit_bounds_unfinished_candidates(tmp_path):
    repo = make_repo(tmp_path, records=2)
    analyze = AsyncMock(return_value=material_analysis())
    summary = await run_backfill(**runner_args(repo, limit=1, analyze=analyze))

    assert summary.attempted == 1
    assert summary.remaining == 1
    assert analyze.await_count == 1


async def test_irrelevant_verdict_skips_analysis_and_is_terminal(tmp_path):
    repo = make_repo(tmp_path)
    relevance = AsyncMock(
        return_value=RelevanceVerdict(is_relevant=False, reason="not in scope")
    )
    analyze = AsyncMock()
    summary = await run_backfill(
        **runner_args(repo, relevance=relevance, analyze=analyze)
    )

    assert summary.irrelevant == 1
    assert summary.remaining == 0
    analyze.assert_not_awaited()
    manifest = next((repo / "data/backfills").glob("*.json"))
    assert yaml.safe_load(manifest.read_text())["entries"]["direct--0"]["outcome"] == "irrelevant"


async def test_dry_run_needs_no_model_and_writes_nothing(tmp_path):
    repo = make_repo(tmp_path)
    summary = await run_backfill(
        repo_root=repo,
        since=SINCE,
        until=UNTIL,
        limit=15,
        model=None,
        now=NOW,
        dry_run=True,
    )

    assert summary.eligible == 1
    assert summary.remaining == 1
    assert summary.provider_status == "dry-run"
    assert not (repo / "content/feed").exists()
    assert not (repo / "content/events").exists()
    assert not (repo / "data/backfills").exists()
