from datetime import datetime, timezone

import pytest
import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.github_repo import fetch_github_repo
from pipeline.sources import Pillar, Source, SourceType


@pytest.fixture
def gh_source():
    return Source(
        slug="mcp",
        pillar=Pillar.AGENT,
        type=SourceType.GITHUB_REPO,
        repo="modelcontextprotocol/specification",
        display_name="MCP",
    )


@respx.mock
async def test_includes_releases_and_merged_prs_since_cutoff(gh_source):
    releases_url = "https://api.github.com/repos/modelcontextprotocol/specification/releases"
    prs_url = "https://api.github.com/repos/modelcontextprotocol/specification/pulls"

    respx.get(releases_url).mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": 1,
                    "name": "v1.2.0",
                    "tag_name": "v1.2.0",
                    "published_at": "2026-04-17T12:00:00Z",
                    "html_url": "https://github.com/x/y/releases/tag/v1.2.0",
                    "body": "Added new tool-use protocol.",
                }
            ],
        )
    )
    respx.get(prs_url).mock(
        return_value=Response(
            200,
            json=[
                {
                    "number": 42,
                    "title": "Add structured outputs field to tool call",
                    "merged_at": "2026-04-17T09:00:00Z",
                    "html_url": "https://github.com/x/y/pull/42",
                    "body": "Details about the change.",
                    "labels": [{"name": "spec"}],
                },
                {
                    "number": 43,
                    "title": "Fix typo in readme",
                    "merged_at": "2026-04-16T09:00:00Z",
                    "html_url": "https://github.com/x/y/pull/43",
                    "body": "",
                    "labels": [{"name": "docs"}],
                },
            ],
        )
    )

    since = datetime(2026, 4, 16, tzinfo=timezone.utc)
    result = await fetch_github_repo(gh_source, since=since, seen_guids=[])

    assert result.mode == ResultMode.PER_ITEM
    kinds = {item.guid.split(":")[0] for item in result.items}
    assert kinds == {"release", "pr"}
    assert len(result.items) == 3


@respx.mock
async def test_applies_pr_label_filter_when_set(gh_source):
    labeled = gh_source.model_copy(update={"pr_labels": ["spec"]})
    releases_url = "https://api.github.com/repos/modelcontextprotocol/specification/releases"
    prs_url = "https://api.github.com/repos/modelcontextprotocol/specification/pulls"

    respx.get(releases_url).mock(return_value=Response(200, json=[]))
    respx.get(prs_url).mock(
        return_value=Response(
            200,
            json=[
                {
                    "number": 42,
                    "title": "Add structured outputs",
                    "merged_at": "2026-04-17T09:00:00Z",
                    "html_url": "https://x",
                    "body": "",
                    "labels": [{"name": "spec"}],
                },
                {
                    "number": 43,
                    "title": "Typo fix",
                    "merged_at": "2026-04-17T09:00:00Z",
                    "html_url": "https://x",
                    "body": "",
                    "labels": [{"name": "docs"}],
                },
            ],
        )
    )

    result = await fetch_github_repo(labeled, since=None, seen_guids=[])

    guids = {item.guid for item in result.items}
    assert "pr:42" in guids
    assert "pr:43" not in guids
