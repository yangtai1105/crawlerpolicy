from datetime import UTC, datetime

import pytest

from pipeline.backfill import (
    BackfillEntry,
    BackfillManifest,
    BackfillOutcome,
    batch_id,
    load_manifest,
    save_manifest,
    select_candidates,
)
from pipeline.evidence import EvidenceRecord, save_evidence
from pipeline.sources import load_sources


def _record(evidence_id, source, published_at):
    return EvidenceRecord(
        evidence_id=evidence_id,
        source=source,
        source_url=f"https://example.test/{evidence_id}",
        published_at=published_at,
        detected_at=published_at,
        content_path=f"content/raw/{source}/2026-08.jsonl",
        external_id=evidence_id,
        title=evidence_id,
        content="Direct evidence about crawler policy.",
    )


def test_selection_uses_only_unpublished_direct_evidence(tmp_path):
    evidence_dir = tmp_path / "content/evidence"
    feed_dir = tmp_path / "content/feed"
    feed_dir.mkdir(parents=True)
    (tmp_path / "sources.yaml").write_text(
        """
- slug: direct
  type: rss_feed
  url: https://example.test/feed.xml
  display_name: Direct Publisher
  default_tracks: [crawler-controls]
  tier: primary
  role: infrastructure
- slug: search
  type: gemini_search
  query: crawler policy news
  display_name: Search Discovery
  default_tracks: [search-discovery]
  tier: commentary
  role: reporting
  enabled: false
""".strip()
    )
    records = [
        _record("direct--older", "direct", datetime(2026, 6, 15, tzinfo=UTC)),
        _record("direct--newest", "direct", datetime(2026, 8, 20, tzinfo=UTC)),
        _record("direct--old", "direct", datetime(2026, 5, 31, tzinfo=UTC)),
        _record("direct--published", "direct", datetime(2026, 7, 1, tzinfo=UTC)),
        _record("search--excluded", "search", datetime(2026, 8, 1, tzinfo=UTC)),
    ]
    for record in records:
        save_evidence(evidence_dir, record)
    (feed_dir / "existing.md").write_text(
        "---\nevidence_ids:\n  - direct--published\n---\n"
    )

    selection = select_candidates(
        evidence_dir=evidence_dir,
        feed_dir=feed_dir,
        sources=load_sources(tmp_path / "sources.yaml"),
        since=datetime(2026, 6, 1, tzinfo=UTC),
        until=datetime(2026, 9, 1, 23, 59, 59, tzinfo=UTC),
    )

    assert [candidate.record.evidence_id for candidate in selection.candidates] == [
        "direct--newest",
        "direct--older",
    ]
    assert selection.excluded_search_ids == ["search--excluded"]
    assert selection.outside_window_ids == ["direct--old"]
    assert selection.duplicate_ids == ["direct--published"]
    assert selection.counts.eligible == 2


def test_manifest_batch_id_and_round_trip(tmp_path):
    since = datetime(2026, 6, 1, tzinfo=UTC)
    until = datetime(2026, 9, 1, 23, 59, 59, tzinfo=UTC)
    manifest = BackfillManifest(
        batch_id=batch_id(since, until),
        since=since,
        until=until,
        entries={
            "source--abc": BackfillEntry(
                evidence_id="source--abc",
                outcome=BackfillOutcome.PUBLISHED,
                updated_at=until,
                feed_path="content/feed/item.md",
            )
        },
        summary={"published": 1, "remaining": 0},
    )
    path = tmp_path / "manifest.json"
    save_manifest(path, manifest)
    assert load_manifest(path, since=since, until=until) == manifest
    assert not list(tmp_path.glob("*.tmp"))


def test_manifest_rejects_a_different_window(tmp_path):
    path = tmp_path / "manifest.json"
    save_manifest(
        path,
        BackfillManifest(
            batch_id="direct-evidence_2026-06-01_2026-09-01",
            since=datetime(2026, 6, 1, tzinfo=UTC),
            until=datetime(2026, 9, 1, 23, 59, 59, tzinfo=UTC),
        ),
    )
    with pytest.raises(ValueError, match="window does not match"):
        load_manifest(
            path,
            since=datetime(2026, 7, 1, tzinfo=UTC),
            until=datetime(2026, 9, 1, 23, 59, 59, tzinfo=UTC),
        )
