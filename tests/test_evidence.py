from datetime import UTC, datetime

from pipeline.evidence import (
    EvidenceRecord,
    EvidenceStage,
    load_evidence,
    make_evidence_id,
    pending_analysis,
    save_evidence,
)


def _record(*, evidence_id: str, stage: EvidenceStage, detected_at: datetime):
    return EvidenceRecord(
        evidence_id=evidence_id,
        source="cloudflare-blog",
        source_url="https://example.test/post",
        published_at=datetime(2026, 8, 28, tzinfo=UTC),
        detected_at=detected_at,
        content_path="content/raw/cloudflare-blog/2026-08.jsonl",
        content_hash="sha256:abc123",
        external_id="post-42",
        stage=stage,
        analysis_attempts=1,
        last_error="provider unavailable"
        if stage is EvidenceStage.FAILED_ANALYSIS
        else None,
        title="Cloudflare changes bot controls",
        content="Normalized current content",
        previous_content="Normalized previous content",
        unified_diff="-old\n+new",
    )


def test_evidence_id_is_stable_and_source_scoped():
    first = make_evidence_id("cloudflare-blog", "post-42")

    assert first == make_evidence_id("cloudflare-blog", "post-42")
    assert first != make_evidence_id("another-source", "post-42")
    assert first.startswith("cloudflare-blog--")
    assert len(first.rsplit("--", 1)[1]) == 16


def test_save_and_load_evidence_uses_source_directory(tmp_path):
    record = _record(
        evidence_id="cloudflare-blog--abc123",
        stage=EvidenceStage.FETCHED,
        detected_at=datetime(2026, 8, 29, tzinfo=UTC),
    )

    path = save_evidence(tmp_path, record)

    assert path == tmp_path / "cloudflare-blog" / "cloudflare-blog--abc123.json"
    assert load_evidence(path) == record
    assert load_evidence(path).content == "Normalized current content"
    assert list(path.parent.glob("*.tmp")) == []


def test_failed_analysis_remains_replayable_and_queue_is_chronological(tmp_path):
    failed = _record(
        evidence_id="cloudflare-blog--later",
        stage=EvidenceStage.FAILED_ANALYSIS,
        detected_at=datetime(2026, 8, 29, 10, tzinfo=UTC),
    )
    fetched = _record(
        evidence_id="cloudflare-blog--earlier",
        stage=EvidenceStage.FETCHED,
        detected_at=datetime(2026, 8, 29, 9, tzinfo=UTC),
    )
    published = _record(
        evidence_id="cloudflare-blog--done",
        stage=EvidenceStage.PUBLISHED,
        detected_at=datetime(2026, 8, 29, 8, tzinfo=UTC),
    )
    for record in (failed, fetched, published):
        save_evidence(tmp_path, record)

    queued = pending_analysis(tmp_path)

    assert [item[1].evidence_id for item in queued] == [
        fetched.evidence_id,
        failed.evidence_id,
    ]
