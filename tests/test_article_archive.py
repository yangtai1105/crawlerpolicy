from datetime import UTC, datetime

import httpx

from pipeline import article_archive
from pipeline.article_reader import Article
from pipeline.evidence import EvidenceRecord, EvidenceStage

NOW = datetime(2026, 10, 18, 12, tzinfo=UTC)
URL = "https://www.theverge.com/tech/1013409/meta"


def _record() -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id="x-discovery--abc",
        source="x-discovery",
        source_url="https://x.com/verge/status/1",
        supporting_urls=[URL],
        published_at=datetime(2026, 10, 17, 15, tzinfo=UTC),
        detected_at=NOW,
        content_path="content/evidence/x-discovery/x-discovery--abc.json",
        content_hash="sha256:x",
        external_id="1",
        stage=EvidenceStage.FETCHED,
        title="Meta removes language",
        content="synopsis",
        discovery_metadata={"linked_articles": [{"url": URL, "method": "json-ld"}]},
    )


def _article() -> Article:
    return Article(
        url=URL, final_url=URL, method="json-ld", title="Meta removes language",
        text="First paragraph.\n\nSecond paragraph.",
    )


def test_private_copies_are_disabled_without_configuration(monkeypatch, tmp_path):
    monkeypatch.delenv("PRIVATE_ARCHIVE_DIR", raising=False)
    assert article_archive.save_private_copies([_article()], record=_record(), read_at=NOW) == {}
    assert not any(tmp_path.iterdir())


def test_private_copy_is_written_with_source_metadata(monkeypatch, tmp_path):
    monkeypatch.setenv("PRIVATE_ARCHIVE_DIR", str(tmp_path))
    monkeypatch.setenv("PRIVATE_ARCHIVE_REPO", "owner/archive")

    links = article_archive.save_private_copies([_article()], record=_record(), read_at=NOW)

    relative = "articles/2026-10-17/x-discovery--abc-1.md"
    assert links == {URL: f"https://github.com/owner/archive/blob/main/{relative}"}
    text = (tmp_path / relative).read_text()
    assert f'url: "{URL}"' in text
    assert 'x_post: "https://x.com/verge/status/1"' in text
    assert "First paragraph.\n\nSecond paragraph." in text


async def test_wayback_returns_timestamped_snapshots_and_skips_failures():
    snapshot = f"https://web.archive.org/web/20261018205027/{URL}"

    def handler(request: httpx.Request) -> httpx.Response:
        if URL in str(request.url):
            return httpx.Response(302, headers={"location": snapshot})
        return httpx.Response(523)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    result = await article_archive.save_wayback_snapshots(
        [URL, "https://down.example/a"], client=client
    )
    assert result == {URL: snapshot}


async def test_wayback_is_off_unless_enabled(monkeypatch):
    monkeypatch.delenv("WAYBACK_SAVE", raising=False)
    assert await article_archive.save_wayback_snapshots([URL]) == {}


async def test_preserve_annotates_the_read_log(monkeypatch, tmp_path):
    monkeypatch.setenv("PRIVATE_ARCHIVE_DIR", str(tmp_path))
    monkeypatch.setenv("PRIVATE_ARCHIVE_REPO", "owner/archive")

    async def fake_wayback(urls, *, client=None):
        return {URL: f"https://web.archive.org/web/20261018205027/{URL}"}

    monkeypatch.setattr(article_archive, "save_wayback_snapshots", fake_wayback)
    record = _record()

    await article_archive.preserve([_article()], record=record, read_at=NOW)

    entry = record.discovery_metadata["linked_articles"][0]
    assert entry["saved_copy"].startswith("https://github.com/owner/archive/blob/main/")
    assert entry["archived_copy"].startswith("https://web.archive.org/web/")
