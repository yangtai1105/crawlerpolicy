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


def test_apply_takes_previous_status_from_the_running_registry_not_from_main(tmp_path):
    """Day 1 proposes none->stated while `main` still says `none`. Day 2,
    before day 1 merges, `main` still says `none` too, so day 2's proposal
    also carries `from_status=none` even though it proposes none->shipped.
    Applying both in filename order must not erase the `stated` step: the
    final record's `previous_status` must come from what day 1 just wrote
    (`stated`), not from day 2's stale `from_status` (`none`).
    """
    path = tmp_path / "positions.json"
    day1 = _proposal(
        from_status=PositionStatus.NONE,
        to_status=PositionStatus.STATED,
        since="2026-10-17",
        proposed_by="run-2026-10-17",
    )
    day2 = _proposal(
        from_status=PositionStatus.NONE,
        to_status=PositionStatus.SHIPPED,
        since="2026-10-18",
        proposed_by="run-2026-10-18",
    )

    applied = apply([day1, day2], path, proposals_dir=None)

    assert applied == 2
    position = load_positions(path).get("akamai", "aipref-vocab")
    assert position.status is PositionStatus.SHIPPED
    assert position.previous_status is PositionStatus.STATED


def test_apply_skips_a_re_proposal_whose_target_already_holds(tmp_path):
    """While a pull request sits open, `collect_proposals` re-proposes the
    same cell every day because it only diffs against merged state. Applying
    the same transition a second time must be a no-op, not a second
    transition, so a batch of proposals that duplicates an already-applied
    change doesn't advance `applied` or disturb the record it already wrote.
    """
    path = tmp_path / "positions.json"
    apply([_proposal()], path, proposals_dir=None)  # none -> stated

    applied = apply([_proposal()], path, proposals_dir=None)  # re-proposed, unchanged

    assert applied == 0
    position = load_positions(path).get("akamai", "aipref-vocab")
    assert position.status is PositionStatus.STATED
    assert position.previous_status is PositionStatus.NONE


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
