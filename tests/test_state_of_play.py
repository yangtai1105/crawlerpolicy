import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.sources import Source, SourceType
from pipeline.state_of_play import (
    CrawlerFacts,
    UserAgentFact,
    build_opt_out_matrix,
    select_crawler_control_sources,
)
from pipeline.taxonomy import SourceRole, SourceTier, Track


@pytest.fixture
def crawler_sources():
    return [
        Source(
            slug="gptbot",
            type=SourceType.HTML_PAGE,
            url="https://x",
            display_name="OpenAI GPTBot",
            default_tracks=[Track.CRAWLER_CONTROLS],
            tier=SourceTier.PRIMARY,
            role=SourceRole.PLATFORM_DOCS,
        ),
        Source(
            slug="claudebot",
            type=SourceType.HTML_PAGE,
            url="https://y",
            display_name="Anthropic ClaudeBot",
            default_tracks=[Track.CRAWLER_CONTROLS, Track.SEARCH_DISCOVERY],
            tier=SourceTier.PRIMARY,
            role=SourceRole.PLATFORM_DOCS,
        ),
    ]


@pytest.fixture
def fake_client():
    model = MagicMock()
    model.generate = AsyncMock()
    return model


async def test_build_opt_out_matrix_writes_json(tmp_path: Path, crawler_sources, fake_client):
    fake_client.generate.side_effect = [
        CrawlerFacts(
            supports_robots_txt=True,
            supports_user_agent_opt_out=True,
            policy_url="https://x/docs",
            user_agents=[
                UserAgentFact(name="GPTBot", purpose="Training crawl")
            ],
        ),
        CrawlerFacts(
            supports_robots_txt=True,
            supports_user_agent_opt_out=True,
            policy_url="https://y/docs",
            user_agents=[
                UserAgentFact(name="ClaudeBot", purpose="Training crawl")
            ],
        ),
    ]

    def load_latest_snapshot(slug: str) -> tuple[str, datetime] | None:
        return ("dummy content", datetime(2026, 4, 18, tzinfo=UTC))

    out_path = tmp_path / "opt-out-matrix.json"
    await build_opt_out_matrix(
        model=fake_client,
        crawler_sources=crawler_sources,
        load_latest_snapshot=load_latest_snapshot,
        out_path=out_path,
        now=datetime(2026, 4, 20, tzinfo=UTC),
    )

    data = json.loads(out_path.read_text())
    assert {row["slug"] for row in data["entries"]} == {"gptbot", "claudebot"}
    first = data["entries"][0]
    assert first["supports_robots_txt"] is True
    assert first["days_since_last_change"] == 2
    assert first["user_agents"][0]["name"] == "GPTBot"


def test_select_crawler_control_sources_uses_tracks_not_source_type(crawler_sources):
    non_crawler_html = Source(
        slug="regulator",
        type=SourceType.HTML_PAGE,
        url="https://regulator.example",
        display_name="Regulator",
        default_tracks=[Track.POLICY_REGULATION],
        tier=SourceTier.PRIMARY,
        role=SourceRole.REGULATOR,
    )

    selected = select_crawler_control_sources([*crawler_sources, non_crawler_html])

    assert [source.slug for source in selected] == ["gptbot", "claudebot"]
