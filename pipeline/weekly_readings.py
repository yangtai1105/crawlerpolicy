"""Generate the week's readings and stage them for review.

Runs weekly, after Weekly Intelligence. Writes `data/readings/` only inside the
`map/readings` branch, whose contents reach the default branch exclusively
through a human merge — the same gate positions pass.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from pipeline.config import Config
from pipeline.model_provider import StructuredModel
from pipeline.readings import DevelopmentNote, Reading, build_reading, save_reading
from pipeline.taxonomy import FRONT_TRACKS, Front, Track, resolve_track
from pipeline.weekly_intelligence import _section, completed_iso_window

_FRONT_BY_TRACK: dict[Track, Front] = {
    track: front for front, tracks in FRONT_TRACKS.items() for track in tracks
}


class WindowRecord(BaseModel):
    """A feed record inside the reading window."""

    slug: str
    status: str
    event_date: str
    title: str = ""
    summary: str = ""
    protocols: list[str] = Field(default_factory=list)
    tracks: list[str] = Field(default_factory=list)


def front_for_track(track: Track) -> Front | None:
    """Invert FRONT_TRACKS. Returns None for a track in no front."""
    return _FRONT_BY_TRACK.get(track)


def _verified(records: list[WindowRecord]) -> list[WindowRecord]:
    return [r for r in records if r.status.strip().lower() == "verified"]


def _note(record: WindowRecord) -> DevelopmentNote:
    return DevelopmentNote(slug=record.slug, title=record.title, summary=record.summary)


def group_by_protocol(records: list[WindowRecord]) -> dict[str, list[DevelopmentNote]]:
    """Development notes per protocol, verified records only."""
    grouped: dict[str, list[DevelopmentNote]] = {}
    for record in _verified(records):
        for protocol in record.protocols:
            grouped.setdefault(protocol, []).append(_note(record))
    return grouped


def group_by_front(records: list[WindowRecord]) -> dict[str, list[DevelopmentNote]]:
    """Development notes per front, verified records only.

    A record with no protocol still belongs to a front, so a front reading can
    speak about developments the protocol axis cannot see.
    """
    grouped: dict[str, list[DevelopmentNote]] = {}
    for record in _verified(records):
        fronts: set[str] = set()
        for raw in record.tracks:
            front = front_for_track(resolve_track(raw))
            if front is not None:
                fronts.add(front.value)
        for front_slug in sorted(fronts):
            notes = grouped.setdefault(front_slug, [])
            if record.slug not in [note.slug for note in notes]:
                notes.append(_note(record))
    return grouped


def load_window_records(
    feed_dir: Path, window_start: str, window_end: str
) -> list[WindowRecord]:
    """Read feed records whose event_date falls inside the window.

    Frontmatter carries `title`, a full descriptive sentence, but no summary;
    the summary lives in the body under a `## Development` heading, read with
    the same `_section` helper `weekly_intelligence` uses for the same purpose.
    """
    records: list[WindowRecord] = []
    for path in sorted(feed_dir.glob("*.md")):
        text = path.read_text()
        if not text.startswith("---\n"):
            continue
        try:
            frontmatter_text, body = text[4:].split("\n---\n", 1)
            data = yaml.safe_load(frontmatter_text)
        except (ValueError, yaml.YAMLError):
            continue
        if not isinstance(data, dict):
            continue
        event_date = str(data.get("event_date", ""))[:10]
        if not (window_start <= event_date <= window_end):
            continue
        records.append(
            WindowRecord(
                slug=str(data.get("slug", path.stem)),
                status=str(data.get("status", "")),
                event_date=event_date,
                title=str(data.get("title", "")),
                summary=_section(body, "Development"),
                protocols=[str(p) for p in (data.get("protocols") or [])],
                tracks=[str(t) for t in (data.get("tracks") or [])],
            )
        )
    return records


def render_body(readings: list[Reading]) -> str:
    lines = [
        "Weekly readings generated from this week's verified developments.",
        "",
        "Each reading is one stance sentence plus three fixed angles. A wrong cell",
        "is a visible factual error; a wrong reading is a judgement error, so these",
        "are reviewed before they publish.",
        "",
        "This branch is rebuilt from `main` on every run — edit on `main` after merging.",
        "",
    ]
    for reading in readings:
        plural = "s" if reading.development_count != 1 else ""
        lines.append(f"### {reading.subject_kind} · {reading.subject_slug}")
        lines.append(f"_{reading.development_count} development{plural}_")
        lines.append("")
        lines.append(reading.stance)
        lines.append("")
        lines.append(f"- **Adoption shape:** {reading.adoption_shape}")
        lines.append(f"- **New entrants:** {reading.new_entrants}")
        lines.append(f"- **Watch for:** {reading.watch_for}")
        lines.append("")
    return "\n".join(lines) + "\n"


async def generate(
    model: StructuredModel,
    *,
    feed_dir: Path,
    readings_dir: Path,
    now: datetime | None = None,
    write: bool = True,
) -> list[Reading]:
    """Build every reading the window supports: all protocols, then all fronts."""
    now = now or datetime.now(UTC)
    _, window_start, window_end = completed_iso_window(now)
    records = load_window_records(
        feed_dir, window_start.isoformat(), window_end.isoformat()
    )

    readings: list[Reading] = []
    for subject_kind, grouped in (
        ("protocol", group_by_protocol(records)),
        ("front", group_by_front(records)),
    ):
        for subject_slug, developments in sorted(grouped.items()):
            reading = await build_reading(
                model,
                subject_kind=subject_kind,
                subject_slug=subject_slug,
                developments=developments,
                now=now,
            )
            if reading is None:
                continue
            readings.append(reading)
            if write:
                save_reading(readings_dir, reading)
    return readings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--body",
        action="store_true",
        help="print the PR body for the readings already in data/readings",
    )
    args = parser.parse_args()

    cfg = Config.from_env()

    if args.body:
        readings = [
            Reading.model_validate_json(path.read_text())
            for path in sorted(cfg.readings_dir.glob("*.json"))
        ]
        print(render_body(readings), end="")
        return 0

    if not cfg.gemini_api_key:
        print("GEMINI_API_KEY is missing; no readings generated.")
        return 1

    from pipeline.model_provider import GeminiStructuredModel

    model = GeminiStructuredModel(
        api_key=cfg.gemini_api_key,
        model=cfg.gemini_analysis_model,
    )
    readings = asyncio.run(
        generate(model, feed_dir=cfg.feed_dir, readings_dir=cfg.readings_dir)
    )
    print(f"wrote {len(readings)} reading(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
