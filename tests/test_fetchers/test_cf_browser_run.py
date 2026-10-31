from unittest.mock import AsyncMock

import pytest
import respx
from httpx import Response

from pipeline.fetchers import cf_browser_run
from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.cf_browser_run import fetch_cf_browser_run
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Track


@respx.mock
async def test_fetches_rendered_markdown_for_browser_backed_source(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_EMAIL", "crawler@example.test")
    monkeypatch.setenv("CLOUDFLARE_CRAWLER_API_KEY", "test-key")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "account-id")
    monkeypatch.setattr(cf_browser_run.asyncio, "sleep", AsyncMock())
    base = (
        "https://api.cloudflare.com/client/v4/accounts/account-id/"
        "browser-rendering/crawl"
    )
    respx.post(base).mock(return_value=Response(200, json={"success": True, "result": "job-1"}))
    respx.get(f"{base}/job-1?limit=1").mock(
        return_value=Response(
            200,
            json={
                "result": {
                    "status": "completed",
                    "records": [{"markdown": "# AI Insights\nVerified traffic data."}],
                }
            },
        )
    )
    source = Source(
        slug="cloudflare-radar-ai-insights",
        type=SourceType.CF_BROWSER_RUN,
        url="https://radar.cloudflare.com/ai-insights",
        display_name="Cloudflare Radar AI Insights",
        default_tracks=[Track.MEASUREMENT_ECONOMICS],
        tier=SourceTier.MEASUREMENT,
        role=SourceRole.MEASUREMENT,
    )

    result = await fetch_cf_browser_run(source)

    assert result.mode is ResultMode.DIFFABLE
    assert "Verified traffic data" in result.normalized_content
    assert result.raw_ext == "md"


@respx.mock
async def test_bot_protection_block_page_is_a_fetch_failure(monkeypatch):
    monkeypatch.setenv("CLOUDFLARE_EMAIL", "crawler@example.test")
    monkeypatch.setenv("CLOUDFLARE_CRAWLER_API_KEY", "test-key")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "account-id")
    monkeypatch.setattr(cf_browser_run.asyncio, "sleep", AsyncMock())
    base = (
        "https://api.cloudflare.com/client/v4/accounts/account-id/"
        "browser-rendering/crawl"
    )
    respx.post(base).mock(return_value=Response(200, json={"success": True, "result": "job-1"}))
    respx.get(f"{base}/job-1?limit=1").mock(
        return_value=Response(
            200,
            json={
                "result": {
                    "status": "completed",
                    "records": [
                        {
                            "markdown": (
                                "# Access Denied\n\nYou don't have permission to access "
                                "this server.\n\nhttps://errors.edgesuite.net/18.d6d31102"
                            )
                        }
                    ],
                }
            },
        )
    )
    source = Source(
        slug="akamai-page",
        type=SourceType.CF_BROWSER_RUN,
        url="https://www.akamai.com/blog",
        display_name="Akamai page",
        default_tracks=[Track.ACCESS_CONTROLS],
        tier=SourceTier.SPECIALIST,
        role=SourceRole.INFRASTRUCTURE,
    )

    with pytest.raises(RuntimeError, match="blocked by target site"):
        await fetch_cf_browser_run(source)


def test_block_reason_reads_http_status_and_vendor_markers():
    assert cf_browser_run._block_reason("ok", "", {"status": 403}) == "HTTP 403"
    assert cf_browser_run._block_reason("", '<meta content="px-captcha">', {}) == "px-captcha"
    assert cf_browser_run._block_reason("# Radar\nVerified traffic.", "", {"status": 200}) is None
