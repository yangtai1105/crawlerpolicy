from unittest.mock import AsyncMock

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
