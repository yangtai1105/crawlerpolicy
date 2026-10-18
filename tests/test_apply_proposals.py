from pipeline.apply_proposals import apply, load_pending, render_body
from pipeline.map_proposals import Proposal
from pipeline.positions import EvidenceLevel, PositionStatus, load_positions


def _proposal(**overrides) -> Proposal:
    base = dict(
        player_slug="akamai",
        protocol_slug="aipref-vocab",
        from_status=PositionStatus.NONE,
        to_status=PositionStatus.STATED,
        evidence_level=EvidenceLevel.PRIMARY,
        since="2026-10-08",
        source_urls=["https://techdocs.akamai.com/aipref"],
        supporting_development_slug="akamai-aipref",
        feed_slug="akamai-aipref",
        proposed_by="run-1",
    )
    base.update(overrides)
    return Proposal(**base)


def test_apply_creates_a_position_and_records_the_previous_status(tmp_path):
    path = tmp_path / "positions.json"

    # proposals_dir=None: never let a test delete the repository's real queue.
    assert apply([_proposal()], path, proposals_dir=None) == 1

    position = load_positions(path).get("akamai", "aipref-vocab")
    assert position.status is PositionStatus.STATED
    assert position.previous_status is PositionStatus.NONE
    assert position.supporting_development_slugs == ["akamai-aipref"]
    assert position.merged_at is None


def test_apply_replaces_rather_than_duplicating_an_existing_cell(tmp_path):
    path = tmp_path / "positions.json"
    apply([_proposal()], path, proposals_dir=None)

    apply(
        [_proposal(from_status=PositionStatus.STATED, to_status=PositionStatus.SHIPPED)],
        path,
        proposals_dir=None,
    )

    registry = load_positions(path)
    assert len(registry.positions) == 1
    assert registry.get("akamai", "aipref-vocab").status is PositionStatus.SHIPPED


def test_apply_drains_the_queue_so_nothing_is_proposed_twice(tmp_path):
    queue = tmp_path / "proposals"
    queue.mkdir()
    (queue / "2026-10-17-1.json").write_text(_proposal().model_dump_json())

    apply(load_pending(queue), tmp_path / "positions.json", proposals_dir=queue)

    assert list(queue.glob("*.json")) == []


def test_load_pending_reads_every_proposal_file(tmp_path):
    (tmp_path / "2026-10-17-1.json").write_text(_proposal().model_dump_json())
    (tmp_path / "2026-10-17-2.json").write_text(
        _proposal(protocol_slug="rsl").model_dump_json()
    )

    assert len(load_pending(tmp_path)) == 2


def test_render_body_names_the_cell_the_transition_and_the_evidence():
    body = render_body([_proposal()])

    assert "akamai×aipref-vocab" in body
    assert "`none` → `stated`" in body
    assert "https://techdocs.akamai.com/aipref" in body
    assert "effective 2026-10-08" in body
