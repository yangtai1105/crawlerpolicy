from datetime import datetime, timezone

from pipeline.state import SourceState, load_state, save_state


def test_new_source_returns_empty_state(tmp_path):
    state = load_state(tmp_path, "newsource")
    assert state.last_checked_at is None
    assert state.last_hash is None
    assert state.last_seen_guids == []
    assert state.consecutive_failures == 0


def test_round_trip_state(tmp_path):
    t = datetime(2026, 4, 18, 12, 0, 0, tzinfo=timezone.utc)
    state = SourceState(
        last_checked_at=t,
        last_hash="abc123",
        last_seen_guids=["g1", "g2"],
        consecutive_failures=0,
    )
    save_state(tmp_path, "gptbot", state)
    loaded = load_state(tmp_path, "gptbot")
    assert loaded.last_checked_at == t
    assert loaded.last_hash == "abc123"
    assert loaded.last_seen_guids == ["g1", "g2"]


def test_state_file_written_atomically(tmp_path):
    state = SourceState(last_hash="v1")
    save_state(tmp_path, "gptbot", state)
    leftovers = list(tmp_path.glob("*.tmp"))
    assert leftovers == []
