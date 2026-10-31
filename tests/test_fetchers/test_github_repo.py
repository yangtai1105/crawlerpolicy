from datetime import UTC, datetime

import pytest
import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.github_repo import fetch_github_repo
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Track


@pytest.fixture
def gh_source():
    return Source(
        slug="mcp",
        type=SourceType.GITHUB_REPO,
        repo="modelcontextprotocol/specification",
        display_name="MCP",
        default_tracks=[Track.STANDARDS_PROTOCOLS, Track.PLATFORM_ECOSYSTEM],
        tier=SourceTier.PRIMARY,
        role=SourceRole.STANDARDS,
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

    since = datetime(2026, 4, 16, tzinfo=UTC)
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


@respx.mock
async def test_path_globs_keep_only_prs_that_touch_the_spec(gh_source):
    scoped = gh_source.model_copy(
        update={"repo": "x402-foundation/x402", "pr_path_globs": ["specs/*"]}
    )
    base = "https://api.github.com/repos/x402-foundation/x402"
    respx.get(f"{base}/releases").mock(return_value=Response(200, json=[]))
    respx.get(f"{base}/pulls").mock(
        return_value=Response(
            200,
            json=[
                {
                    "number": 7,
                    "title": "spec: add upto scheme",
                    "merged_at": "2026-10-20T09:00:00Z",
                    "html_url": "https://x/7",
                    "body": "",
                    "labels": [],
                },
                {
                    "number": 8,
                    "title": "go sdk: bump deps",
                    "merged_at": "2026-10-20T10:00:00Z",
                    "html_url": "https://x/8",
                    "body": "",
                    "labels": [{"name": "go"}],
                },
            ],
        )
    )
    respx.get(f"{base}/pulls/7/files").mock(
        return_value=Response(200, json=[{"filename": "specs/schemes/upto/scheme_upto.md"}])
    )
    respx.get(f"{base}/pulls/8/files").mock(
        return_value=Response(200, json=[{"filename": "go/go.mod"}])
    )

    result = await fetch_github_repo(scoped, since=None, seen_guids=[])

    assert [item.guid for item in result.items] == ["pr:7"]
