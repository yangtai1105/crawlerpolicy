"""Smoke-level orchestration test: one html_page source, one change → one event."""
import hashlib
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
import yaml

from pipeline.analyzer import AnalysisResult
from pipeline.check import run_check
from pipeline.fetchers.base import FetchResult, ResultMode


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
                    "pillar": "crawler",
                    "type": "html_page",
                    "url": "https://platform.openai.com/docs/gptbot",
                    "display_name": "OpenAI GPTBot",
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
    now = datetime(2026, 4, 18, 8, tzinfo=timezone.utc)

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
        )
    )
    now = datetime(2026, 4, 18, 8, tzinfo=timezone.utc)

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
