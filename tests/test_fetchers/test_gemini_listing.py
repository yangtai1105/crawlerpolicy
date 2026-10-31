from datetime import UTC, datetime
from unittest.mock import AsyncMock

from pipeline import grounded_reader
from pipeline.fetchers import gemini_listing
from pipeline.fetchers.base import ResultMode
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Track

NOW = datetime(2026, 10, 31, 8, tzinfo=UTC)
NEW = "https://www.humansecurity.com/learn/blog/human-sightline-detects-claude-duet/"
OLD = "https://www.humansecurity.com/learn/blog/2024-bot-report/"
PENDING = "https://www.humansecurity.com/learn/blog/not-yet-indexed/"
SEEN = "https://www.humansecurity.com/learn/blog/already-seen/"


def _source() -> Source:
    return Source(
        slug="human-blog",
        type=SourceType.GEMINI_LISTING,
        listing_domain="humansecurity.com",
        query="agent posts",
        lookback_days=14,
        display_name="HUMAN Security Blog",
        default_tracks=[Track.IDENTITY_AUTHORIZATION],
        tier=SourceTier.SPECIALIST,
        role=SourceRole.INFRASTRUCTURE,
    )


def _read(url: str, published: datetime | None) -> grounded_reader.GroundedRead:
    return grounded_reader.GroundedRead(
        url=url, title=f"Title {url[-12:]}", published_on=published, text="n" * 500,
        cited_urls=[url], model="m",
    )


async def test_listing_yields_new_dated_articles_and_settles_old_ones(monkeypatch):
    monkeypatch.setattr(
        grounded_reader, "discover_articles", AsyncMock(return_value=[NEW, OLD, PENDING, SEEN])
    )

    async def fake_read(url, *, model=None):
        if url == PENDING:
            raise grounded_reader.NotIndexed("later")
        return _read(url, datetime(2026, 10, 30, tzinfo=UTC) if url == NEW else None)

    monkeypatch.setattr(grounded_reader, "read_article", fake_read)

    result = await gemini_listing.fetch_gemini_listing(
        _source(), seen_guids=[gemini_listing.article_guid(SEEN)], now=NOW
    )

    assert result.mode is ResultMode.PER_ITEM
    assert [item.url for item in result.items] == [NEW]
    assert result.items[0].guid == "humansecurity.com/human-sightline-detects-claude-duet"
    assert result.items[0].published_at == datetime(2026, 10, 30, tzinfo=UTC)
    # Old/undated pages are settled; unindexed ones stay open for the next run.
    assert result.metadata["settled_guids"] == ["humansecurity.com/2024-bot-report"]
