import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest

from pipeline.analyzer import AnalysisResult
from pipeline.check import run_check
from pipeline.evidence import pending_analysis
from pipeline.fetchers.base import FetchResult, ResultMode
from pipeline.taxonomy import Track
from pipeline.weekly_intelligence import generate_weekly_intelligence

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "intelligence_repo"


@pytest.fixture
def fixture_repo(tmp_path):
    repo = tmp_path / "intelligence-repo"
    shutil.copytree(FIXTURE_ROOT, repo)
    return repo


async def _fetch(source, _state):
    if source.slug == "optional-reporting":
        raise RuntimeError("optional reporting source unavailable")
    content = {
        "primary-control": "primary-new signed request control",
        "measurement-signal": "measurement-new agent traffic series",
        "supporting-standard": "supporting baseline",
    }[source.slug]
    return FetchResult(
        mode=ResultMode.DIFFABLE,
        normalized_content=content,
        raw_ext="html",
    )


async def _first_analysis(**kwargs):
    source = kwargs["source"]
    if source.slug == "measurement-signal":
        raise RuntimeError("measurement analysis provider unavailable")
    return AnalysisResult(
        change_kind="material",
        importance=0.9,
        title="Primary source advances signed control",
        what_changed="The primary source documented an implementable signed request.",
        implication="Machine access can now bind identity to a declared policy.",
        primary_track=Track.CRAWLER_CONTROLS,
        tracks=[Track.CRAWLER_CONTROLS, Track.STANDARDS_PROTOCOLS],
        actors=["Primary Control"],
        trend_signals=["signed-machine-access"],
        confidence="high",
    )


async def _replay_analysis(**kwargs):
    source = kwargs["source"]
    assert source.slug == "measurement-signal"
    return AnalysisResult(
        change_kind="cosmetic",
        importance=0.2,
        title="Measurement series formatting changed",
        what_changed="Formatting changed without a new material signal.",
        implication="No change to the current intelligence read.",
        primary_track=Track.MEASUREMENT_ECONOMICS,
        tracks=[Track.MEASUREMENT_ECONOMICS],
        actors=[],
        trend_signals=[],
        confidence="high",
    )


async def test_pipeline_replay_and_weekly_delta_work_end_to_end(fixture_repo):
    first_health = await run_check(
        repo_root=fixture_repo,
        now=datetime(2026, 8, 27, 8, tzinfo=UTC),
        fetch_dispatch=_fetch,
        analyze_change=_first_analysis,
        dry_run=False,
    )

    assert first_health["status"] == "critical"
    assert len(list((fixture_repo / "content" / "events").glob("*.md"))) == 1
    assert len(pending_analysis(fixture_repo / "content" / "evidence")) == 1

    second_health = await run_check(
        repo_root=fixture_repo,
        now=datetime(2026, 8, 30, 8, tzinfo=UTC),
        fetch_dispatch=_fetch,
        analyze_change=_replay_analysis,
        dry_run=False,
    )

    assert second_health["status"] == "degraded"
    assert second_health["coverage"]["completed"] == 3
    assert pending_analysis(fixture_repo / "content" / "evidence") == []
    assert len(list((fixture_repo / "content" / "events").glob("*.md"))) == 1

    issue = await generate_weekly_intelligence(
        repo_root=fixture_repo,
        now=datetime(2026, 8, 31, 13, tzinfo=UTC),
        client=None,
    )

    assert issue.health_status == "degraded"
    assert issue.trend_deltas[0].previous_status == "emerging"
    assert issue.trend_deltas[0].current_status == "accelerating"
    assert (fixture_repo / "data" / "intelligence" / "2026-W35.json").exists()
