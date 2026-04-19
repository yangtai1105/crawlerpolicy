from datetime import datetime, timezone

import pytest
import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.rss_feed import fetch_rss_feed
from pipeline.sources import Pillar, Source, SourceType

RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Example Blog</title>
<item>
<title>AI crawler update: new opt-out</title>
<link>https://example.com/posts/ai-crawler-opt-out</link>
<guid>https://example.com/posts/ai-crawler-opt-out</guid>
<pubDate>Wed, 18 Apr 2026 12:00:00 GMT</pubDate>
<description>We added a new AI bot opt-out flow.</description>
</item>
<item>
<title>Old post from last month</title>
<link>https://example.com/posts/old</link>
<guid>https://example.com/posts/old</guid>
<pubDate>Sat, 15 Mar 2026 00:00:00 GMT</pubDate>
<description>Something unrelated.</description>
</item>
</channel>
</rss>
"""


@pytest.fixture
def rss_source():
    return Source(
        slug="example",
        pillar=Pillar.ECOSYSTEM,
        type=SourceType.RSS_FEED,
        url="https://example.com/rss",
        display_name="Example",
        keyword_filter=["AI bot", "crawler"],
    )


@respx.mock
async def test_fetches_all_items_when_no_state(rss_source):
    respx.get(rss_source.url).mock(return_value=Response(200, text=RSS))

    result = await fetch_rss_feed(rss_source, since=None, seen_guids=[])

    assert result.mode == ResultMode.PER_ITEM
    assert len(result.items) == 2
    titles = {item.title for item in result.items}
    assert "AI crawler update: new opt-out" in titles


@respx.mock
async def test_excludes_items_older_than_since(rss_source):
    since = datetime(2026, 4, 1, tzinfo=timezone.utc)
    respx.get(rss_source.url).mock(return_value=Response(200, text=RSS))

    result = await fetch_rss_feed(rss_source, since=since, seen_guids=[])

    assert len(result.items) == 1
    assert result.items[0].title == "AI crawler update: new opt-out"


@respx.mock
async def test_excludes_seen_guids(rss_source):
    respx.get(rss_source.url).mock(return_value=Response(200, text=RSS))

    result = await fetch_rss_feed(
        rss_source,
        since=None,
        seen_guids=["https://example.com/posts/ai-crawler-opt-out"],
    )

    titles = {item.title for item in result.items}
    assert "AI crawler update: new opt-out" not in titles
