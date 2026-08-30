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
from pipeline.fetchers.base import FetchResult, ResultMode
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
    now = datetime(2026, 4, 18, 8, tzinfo=UTC)

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
    (repo / "content" / "snapshots" / "gptbot" / "2026-03-01.html").write_text("v1")
    (repo / "state" / "gptbot.json").write_text(
        '{"last_checked_at": "2026-03-01T00:00:00+00:00", "last_hash": "'
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
    now = datetime(2026, 4, 18, 8, tzinfo=UTC)

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
    assert len(events) == 1
    assert "gptbot-gptbot-adds-section" in events[0].name
    analyze.assert_called_once()


async def test_analysis_failure_saves_evidence_and_replays_without_refetching_history(repo):
    (repo / "content" / "snapshots" / "gptbot").mkdir(parents=True)
    (repo / "content" / "snapshots" / "gptbot" / "2026-03-01.html").write_text("v1")
    (repo / "state" / "gptbot.json").write_text(
        '{"last_checked_at": "2026-03-01T00:00:00+00:00", "last_hash": "'
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
    first_now = datetime(2026, 4, 18, 8, tzinfo=UTC)

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
        now=datetime(2026, 4, 19, 8, tzinfo=UTC),
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
            "ANTHROPIC_API_KEY": "   ",
            "GEMINI_API_KEY": "",
            "CLOUDFLARE_ACCOUNT_ID": "account",
            "CLOUDFLARE_EMAIL": "email@example.com",
            "CLOUDFLARE_CRAWLER_API_KEY": "key",
        },
    )

    assert blockers["gemini-agent-infra"].stage == "fetch"
    assert "GEMINI_API_KEY" in blockers["gemini-agent-infra"].message
    assert blockers["gptbot"].stage == "analysis"
    assert "ANTHROPIC_API_KEY" in blockers["gptbot"].message
    assert blockers["meta-externalagent"].stage == "analysis"
