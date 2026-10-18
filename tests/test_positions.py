from datetime import UTC, datetime, timedelta

from pipeline.positions import (
    EvidenceLevel,
    Position,
    PositionRegistry,
    PositionStatus,
    changes_within,
    load_positions,
    may_change,
    position_key,
    save_positions,
)

NOW = datetime(2026, 10, 17, 8, 0, tzinfo=UTC)


def _position(**overrides) -> Position:
    base = dict(
        player_slug="cloudflare",
        protocol_slug="web-bot-auth",
        status=PositionStatus.SHIPPED,
        since="2026-07-11",
        previous_status=PositionStatus.NONE,
        last_changed_at=NOW,
        evidence_level=EvidenceLevel.PRIMARY,
        source_urls=["https://blog.cloudflare.com/web-bot-auth"],
        supporting_development_slugs=["cloudflare-signs-bots"],
        proposed_by="run-2026-10-17",
        merged_at=NOW,
    )
    base.update(overrides)
    return Position(**base)


def test_absent_pair_reads_as_none_and_is_not_stored(tmp_path):
    path = tmp_path / "positions.json"
    save_positions(path, PositionRegistry(positions=[_position()]))

    registry = load_positions(path)

    assert registry.get("cloudflare", "web-bot-auth").status is PositionStatus.SHIPPED
    assert registry.get("akamai", "web-bot-auth") is None
    assert len(registry.positions) == 1


def test_loading_a_missing_file_is_an_empty_registry(tmp_path):
    registry = load_positions(tmp_path / "nope.json")

    assert registry.positions == []
    assert registry.get("cloudflare", "web-bot-auth") is None


def test_save_is_atomic_and_leaves_no_temp_file(tmp_path):
    path = tmp_path / "positions.json"

    save_positions(path, PositionRegistry(positions=[_position()]))

    assert path.exists()
    assert list(tmp_path.glob("*.tmp")) == []
    assert path.read_text().endswith("\n")


def test_only_primary_evidence_may_change_a_position():
    assert may_change(EvidenceLevel.PRIMARY) is True
    assert may_change(EvidenceLevel.SECONDARY) is False


def test_declined_is_a_first_class_status_distinct_from_none():
    declined = _position(status=PositionStatus.DECLINED)

    assert declined.status is not PositionStatus.NONE
    assert declined.status.value == "declined"


def test_changes_within_uses_last_changed_at():
    recent = _position(last_changed_at=NOW - timedelta(days=2))
    old = _position(protocol_slug="rsl", last_changed_at=NOW - timedelta(days=30))
    registry = PositionRegistry(positions=[recent, old])

    changed = changes_within(registry, NOW, days=7)

    assert [p.protocol_slug for p in changed] == ["web-bot-auth"]


def test_position_key_is_stable():
    assert position_key("cloudflare", "web-bot-auth") == "cloudflare×web-bot-auth"


def test_merged_at_is_optional_so_the_pipeline_can_never_set_it():
    unmerged = _position(merged_at=None)

    assert unmerged.merged_at is None
