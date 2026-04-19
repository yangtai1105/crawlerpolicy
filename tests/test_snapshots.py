from datetime import datetime, timezone
from pathlib import Path

from pipeline.snapshots import hash_content, load_latest, save_snapshot


def test_hash_stable():
    assert hash_content("hello") == hash_content("hello")
    assert hash_content("hello") != hash_content("world")


def test_save_and_load_latest(tmp_path: Path):
    save_snapshot(
        tmp_path,
        "gptbot",
        datetime(2026, 3, 1, tzinfo=timezone.utc),
        content="v1",
        ext="html",
    )
    save_snapshot(
        tmp_path,
        "gptbot",
        datetime(2026, 4, 18, tzinfo=timezone.utc),
        content="v2",
        ext="html",
    )

    latest = load_latest(tmp_path, "gptbot")
    assert latest is not None
    content, date = latest
    assert content == "v2"
    assert date.date().isoformat() == "2026-04-18"


def test_load_latest_none_when_no_snapshots(tmp_path: Path):
    assert load_latest(tmp_path, "newthing") is None
