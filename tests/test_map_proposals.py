import json
from datetime import UTC, datetime

from pipeline.map_proposals import (
    FeedRecord,
    collect_proposals,
    evidence_level_for,
    save_proposals,
)
from pipeline.positions import (
    EvidenceLevel,
    Position,
    PositionRegistry,
    PositionStatus,
)

NOW = datetime(2026, 10, 17, 8, 0, tzinfo=UTC)


def _record(**overrides) -> FeedRecord:
    base = dict(
        slug="cloudflare-signs-bots",
        status="verified",
        source_tier="primary",
        source_urls=["https://blog.cloudflare.com/web-bot-auth"],
        event_date="2026-07-11",
        development_slug="cloudflare-signs-bots",
        position_claims=[
            {"player": "cloudflare", "protocol": "web-bot-auth", "status": "shipped"}
        ],
    )
    base.update(overrides)
    return FeedRecord(**base)


def test_a_verified_primary_record_proposes_a_change_from_none():
    proposals = collect_proposals([_record()], PositionRegistry(), run_id="run-1")

    assert len(proposals) == 1
    p = proposals[0]
    assert (p.player_slug, p.protocol_slug) == ("cloudflare", "web-bot-auth")
    assert p.from_status is PositionStatus.NONE
    assert p.to_status is PositionStatus.SHIPPED
    assert p.evidence_level is EvidenceLevel.PRIMARY
    assert p.since == "2026-07-11"
    assert p.supporting_development_slug == "cloudflare-signs-bots"
    assert p.proposed_by == "run-1"


def test_reported_and_signal_records_never_propose():
    for status in ("reported", "signal"):
        proposals = collect_proposals([_record(status=status)], PositionRegistry(), run_id="r")
        assert proposals == [], status


def test_a_non_primary_tier_never_proposes():
    for tier in ("specialist", "commentary"):
        proposals = collect_proposals(
            [_record(source_tier=tier)], PositionRegistry(), run_id="r"
        )
        assert proposals == [], tier


def test_a_claim_matching_merged_state_proposes_nothing():
    merged = PositionRegistry(
        positions=[
            Position(
                player_slug="cloudflare",
                protocol_slug="web-bot-auth",
                status=PositionStatus.SHIPPED,
                since="2026-07-11",
                last_changed_at=NOW,
                evidence_level=EvidenceLevel.PRIMARY,
            )
        ]
    )

    assert collect_proposals([_record()], merged, run_id="r") == []


def test_a_claim_that_moves_an_existing_position_carries_the_previous_status():
    merged = PositionRegistry(
        positions=[
            Position(
                player_slug="cloudflare",
                protocol_slug="web-bot-auth",
                status=PositionStatus.PREVIEW,
                since="2026-05-01",
                last_changed_at=NOW,
                evidence_level=EvidenceLevel.PRIMARY,
            )
        ]
    )

    proposals = collect_proposals([_record()], merged, run_id="r")

    assert proposals[0].from_status is PositionStatus.PREVIEW
    assert proposals[0].to_status is PositionStatus.SHIPPED


def test_evidence_level_mapping():
    assert evidence_level_for("primary") is EvidenceLevel.PRIMARY
    assert evidence_level_for("measurement") is EvidenceLevel.PRIMARY
    assert evidence_level_for("specialist") is EvidenceLevel.SECONDARY
    assert evidence_level_for("commentary") is EvidenceLevel.SECONDARY


def test_save_proposals_writes_one_file_per_proposal_and_nothing_else(tmp_path):
    proposals = collect_proposals([_record()], PositionRegistry(), run_id="run-1")

    written = save_proposals(tmp_path, proposals, date_str="2026-10-17")

    assert [p.name for p in written] == ["2026-10-17-1.json"]
    payload = json.loads(written[0].read_text())
    assert payload["player_slug"] == "cloudflare"
    assert payload["to_status"] == "shipped"
    assert not (tmp_path / "positions.json").exists()


def test_save_proposals_writes_nothing_when_there_is_nothing_to_propose(tmp_path):
    assert save_proposals(tmp_path, [], date_str="2026-10-17") == []
    assert list(tmp_path.glob("*")) == []
