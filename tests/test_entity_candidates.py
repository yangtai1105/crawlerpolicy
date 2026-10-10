from datetime import UTC, datetime

from pipeline.entity_candidates import load_candidates, record_candidates

NOW = datetime(2026, 10, 10, 8, 0, tzinfo=UTC)
LATER = datetime(2026, 10, 11, 8, 0, tzinfo=UTC)


def test_recording_creates_the_queue_file_with_one_entry_per_name(tmp_path):
    path = tmp_path / "entity-candidates.json"

    record_candidates(
        path,
        "player",
        ["Scalepost", "Human Native"],
        evidence_ids=["ev-1"],
        feed_slug="2026-10-10-example",
        now=NOW,
    )

    candidates = load_candidates(path)
    assert set(candidates) == {"player:scalepost", "player:human native"}
    entry = candidates["player:scalepost"]
    assert entry.observed_name == "Scalepost"
    assert entry.occurrences == 1
    assert entry.first_seen_at == NOW
    assert entry.evidence_ids == ["ev-1"]


def test_recording_the_same_feed_slug_again_is_idempotent(tmp_path):
    path = tmp_path / "entity-candidates.json"
    args = dict(evidence_ids=["ev-1"], feed_slug="2026-10-10-example", now=NOW)

    record_candidates(path, "player", ["Scalepost"], **args)
    record_candidates(path, "player", ["Scalepost"], **args)

    entry = load_candidates(path)["player:scalepost"]
    assert entry.occurrences == 1
    assert entry.feed_slugs == ["2026-10-10-example"]
    assert entry.evidence_ids == ["ev-1"]


def test_a_new_feed_slug_bumps_occurrences_and_last_seen(tmp_path):
    path = tmp_path / "entity-candidates.json"

    record_candidates(
        path, "player", ["Scalepost"],
        evidence_ids=["ev-1"], feed_slug="first", now=NOW,
    )
    record_candidates(
        path, "player", ["scalepost"],
        evidence_ids=["ev-2"], feed_slug="second", now=LATER,
    )

    entry = load_candidates(path)["player:scalepost"]
    assert entry.occurrences == 2
    assert entry.feed_slugs == ["first", "second"]
    assert entry.evidence_ids == ["ev-1", "ev-2"]
    assert entry.first_seen_at == NOW
    assert entry.last_seen_at == LATER
    assert entry.observed_name == "Scalepost"


def test_loading_a_missing_file_returns_an_empty_queue(tmp_path):
    assert load_candidates(tmp_path / "nope.json") == {}


def test_blank_names_are_ignored(tmp_path):
    path = tmp_path / "entity-candidates.json"

    record_candidates(
        path, "protocol", ["  ", ""],
        evidence_ids=["ev-1"], feed_slug="first", now=NOW,
    )

    assert load_candidates(path) == {}


def test_evidence_ids_are_deduplicated_across_distinct_feed_slugs(tmp_path):
    path = tmp_path / "entity-candidates.json"

    record_candidates(
        path, "player", ["Scalepost"],
        evidence_ids=["ev-9", "ev-1"], feed_slug="first", now=NOW,
    )
    record_candidates(
        path, "player", ["Scalepost"],
        evidence_ids=["ev-9", "ev-2"], feed_slug="second", now=LATER,
    )

    entry = load_candidates(path)["player:scalepost"]
    assert entry.evidence_ids == ["ev-9", "ev-1", "ev-2"]
    # Ensure ev-9 appears exactly once, not duplicated
    assert entry.evidence_ids.count("ev-9") == 1
