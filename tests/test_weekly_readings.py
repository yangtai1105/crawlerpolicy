import sys
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.readings import DevelopmentNote, Reading, ReadingResponse, save_reading
from pipeline.taxonomy import Front, Track
from pipeline.weekly_readings import (
    WindowRecord,
    front_for_track,
    generate,
    group_by_front,
    group_by_protocol,
    load_window_records,
    main,
    render_body,
)

NOW = datetime(2026, 10, 17, 8, 0, tzinfo=UTC)


def _record(**overrides) -> WindowRecord:
    base = dict(
        slug="cloudflare-signs-bots",
        status="verified",
        event_date="2026-10-13",
        title="Cloudflare signs bots",
        summary="",
        protocols=["web-bot-auth"],
        tracks=["identity-authorization"],
    )
    base.update(overrides)
    return WindowRecord(**base)


def _feed_file(
    feed_dir,
    name: str,
    *,
    slug: str = "cloudflare-signs-bots",
    status: str = "verified",
    event_date: str = "2026-10-08T09:00:00+00:00",
    title: str = "Cloudflare signs bots",
    protocols: list[str] | None = None,
    tracks: list[str] | None = None,
    summary_body: str | None = "Bots now sign every request.",
) -> None:
    protocols = protocols if protocols is not None else ["web-bot-auth"]
    tracks = tracks if tracks is not None else ["identity-authorization"]
    protocol_lines = "\n".join(f'  - "{p}"' for p in protocols)
    track_lines = "\n".join(f"  - {t}" for t in tracks)
    summary_section = f"## Summary\n\n{summary_body}\n\n" if summary_body else ""
    text = (
        "---\n"
        f"slug: {slug}\n"
        f'title: "{title}"\n'
        f"status: {status}\n"
        f"event_date: {event_date}\n"
        f"tracks:\n{track_lines}\n"
        f"protocols:\n{protocol_lines}\n"
        "---\n\n"
        f"{summary_section}"
        "## Insight\n\nAn editorial judgement that must never reach the prompt.\n"
    )
    (feed_dir / name).write_text(text)


def test_front_for_track_inverts_the_rollup_table():
    assert front_for_track(Track.IDENTITY_AUTHORIZATION) is Front.AGENTS_IDENTITY
    assert front_for_track(Track.LITIGATION_LEGAL) is Front.GOVERNANCE_LAW
    assert front_for_track(Track.MEASUREMENT_ECONOMICS) is Front.MEASUREMENT_ECONOMICS


def test_group_by_protocol_collects_development_slugs():
    records = [
        _record(),
        _record(slug="akamai-aipref", protocols=["web-bot-auth", "aipref-vocab"]),
    ]

    grouped = group_by_protocol(records)

    assert [n.slug for n in grouped["web-bot-auth"]] == [
        "cloudflare-signs-bots",
        "akamai-aipref",
    ]
    assert [n.slug for n in grouped["aipref-vocab"]] == ["akamai-aipref"]


def test_grouping_ignores_records_that_are_not_verified():
    records = [_record(status="reported"), _record(slug="sig", status="signal")]

    assert group_by_protocol(records) == {}
    assert group_by_front(records) == {}


def test_group_by_front_uses_the_track_rollup_and_resolves_legacy_slugs():
    records = [_record(tracks=["agentic-web"])]

    grouped = group_by_front(records)

    assert [n.slug for n in grouped["agents-identity"]] == ["cloudflare-signs-bots"]


def test_a_record_with_no_protocols_still_counts_toward_its_front():
    records = [_record(protocols=[])]

    assert group_by_protocol(records) == {}
    assert [n.slug for n in group_by_front(records)["agents-identity"]] == [
        "cloudflare-signs-bots"
    ]


def test_grouping_carries_the_development_title_and_summary():
    records = [_record(title="Cloudflare signs bots", summary="Bots get signed.")]

    note = group_by_protocol(records)["web-bot-auth"][0]

    assert isinstance(note, DevelopmentNote)
    assert note.title == "Cloudflare signs bots"
    assert note.summary == "Bots get signed."


def test_render_body_names_each_subject_and_its_development_count():
    body = render_body(
        [
            Reading(
                subject_kind="protocol",
                subject_slug="web-bot-auth",
                stance="Verification is consolidating among defenders.",
                adoption_shape="a",
                new_entrants="n",
                watch_for="w",
                built_from=["cloudflare-signs-bots"],
                development_count=1,
                generated_at=datetime(2026, 10, 17, tzinfo=UTC),
            )
        ]
    )

    assert "protocol · web-bot-auth" in body
    assert "Verification is consolidating among defenders." in body
    assert "1 development" in body


def test_load_window_records_reads_the_summary_from_the_summary_section(tmp_path):
    feed_dir = tmp_path / "feed"
    feed_dir.mkdir()
    _feed_file(feed_dir, "a.md", summary_body="Bots now sign every request.")

    [record] = load_window_records(feed_dir, "2026-10-08", "2026-10-08")

    assert record.title == "Cloudflare signs bots"
    assert record.summary == "Bots now sign every request."
    # The Insight section is an editorial judgement, not evidence — it must
    # never leak into the summary a reading is grounded in.
    assert "editorial judgement" not in record.summary


def test_load_window_records_tolerates_a_record_with_no_summary_section(tmp_path):
    feed_dir = tmp_path / "feed"
    feed_dir.mkdir()
    _feed_file(feed_dir, "a.md", summary_body=None)

    [record] = load_window_records(feed_dir, "2026-10-08", "2026-10-08")

    assert record.summary == ""


def test_load_window_records_reads_the_summary_from_a_realistically_shaped_file(tmp_path):
    (tmp_path / "2026-10-13-example.md").write_text(
        "---\n"
        "slug: cloudflare-signs-bots\n"
        "status: verified\n"
        "event_date: 2026-10-13T00:00:00+00:00\n"
        'title: "Cloudflare signs its bot traffic"\n'
        "protocols:\n"
        '  - "web-bot-auth"\n'
        "tracks:\n"
        "  - identity-authorization\n"
        "---\n\n"
        "## Summary\n\n"
        "Cloudflare began signing outbound bot requests with Web Bot Auth keys.\n\n"
        "## Insight\n\n"
        "Verification is consolidating among defenders.\n"
    )

    records = load_window_records(tmp_path, "2026-10-12", "2026-10-18")

    assert len(records) == 1
    assert records[0].title == "Cloudflare signs its bot traffic"
    assert records[0].summary.startswith("Cloudflare began signing outbound bot requests")
    assert "Verification is consolidating" not in records[0].summary


def test_load_window_records_excludes_records_outside_the_window(tmp_path):
    feed_dir = tmp_path / "feed"
    feed_dir.mkdir()
    _feed_file(feed_dir, "in.md", slug="in-window", event_date="2026-10-13T09:00:00+00:00")
    _feed_file(feed_dir, "out.md", slug="out-of-window", event_date="2026-09-01T09:00:00+00:00")

    records = load_window_records(feed_dir, "2026-10-07", "2026-10-13")

    assert [r.slug for r in records] == ["in-window"]


async def test_generate_builds_and_writes_readings_for_the_window(tmp_path):
    feed_dir = tmp_path / "feed"
    feed_dir.mkdir()
    readings_dir = tmp_path / "readings"
    _feed_file(feed_dir, "a.md")

    model = MagicMock()
    model.generate = AsyncMock(
        return_value=ReadingResponse(
            stance="Verification is consolidating.",
            adoption_shape="a",
            new_entrants="n",
            watch_for="w",
        )
    )

    readings = await generate(
        model, feed_dir=feed_dir, readings_dir=readings_dir, now=NOW
    )

    subject_pairs = {(r.subject_kind, r.subject_slug) for r in readings}
    assert ("protocol", "web-bot-auth") in subject_pairs
    assert ("front", "agents-identity") in subject_pairs
    assert (readings_dir / "protocol-web-bot-auth.json").exists()
    assert (readings_dir / "front-agents-identity.json").exists()


async def test_generate_with_write_false_does_not_touch_disk(tmp_path):
    feed_dir = tmp_path / "feed"
    feed_dir.mkdir()
    readings_dir = tmp_path / "readings"
    _feed_file(feed_dir, "a.md")

    model = MagicMock()
    model.generate = AsyncMock(
        return_value=ReadingResponse(
            stance="s", adoption_shape="a", new_entrants="n", watch_for="w"
        )
    )

    readings = await generate(
        model, feed_dir=feed_dir, readings_dir=readings_dir, now=NOW, write=False
    )

    assert readings
    assert not readings_dir.exists()


async def test_generate_with_no_developments_in_window_writes_nothing(tmp_path):
    feed_dir = tmp_path / "feed"
    feed_dir.mkdir()
    readings_dir = tmp_path / "readings"

    model = MagicMock()
    model.generate = AsyncMock()

    readings = await generate(model, feed_dir=feed_dir, readings_dir=readings_dir, now=NOW)

    assert readings == []
    model.generate.assert_not_called()


def test_main_body_flag_renders_the_readings_already_on_disk(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    readings_dir = tmp_path / "data" / "readings"
    reading = Reading(
        subject_kind="protocol",
        subject_slug="web-bot-auth",
        stance="Verification is consolidating among defenders.",
        adoption_shape="a",
        new_entrants="n",
        watch_for="w",
        built_from=["cloudflare-signs-bots"],
        development_count=1,
        generated_at=NOW,
    )
    save_reading(readings_dir, reading)
    monkeypatch.setattr(sys, "argv", ["weekly_readings", "--body"])

    exit_code = main()

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "protocol · web-bot-auth" in captured.out


def test_main_without_gemini_api_key_refuses_to_generate(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(sys, "argv", ["weekly_readings"])

    exit_code = main()

    assert exit_code == 1
    assert not (tmp_path / "data" / "readings").exists()


@pytest.fixture(autouse=True)
def _no_real_env(monkeypatch):
    # Tests must not reach a real network or real repo content.
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
