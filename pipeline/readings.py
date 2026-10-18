"""The qualitative reading layer.

Coloured cells state facts and answer nothing; a reading attaches an editorial
judgement to one axis of the map. The three angles are fixed on purpose —
free-form commentary is hard to generate consistently and harder to keep honest.

Cadence is weekly, aligned with Weekly Intelligence. Like positions, readings
reach `data/readings/` only through a merged pull request: a wrong cell is a
visible factual error, a wrong reading is a judgement error that costs
credibility.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from pipeline.model_provider import StructuredModel

SubjectKind = Literal["protocol", "front"]

_SYSTEM = (
    "You write one short editorial reading of a protocol or front in an "
    "intelligence publication about AI crawlers and agents. Answer exactly three "
    "angles and one stance sentence. `stance`: one sentence naming what this "
    "subject's situation now is — the single judgement a reader should take away, "
    "not a summary of the developments. `adoption_shape`: what the pattern of "
    "positions means — who moved, who did not, and why that grouping matters. "
    "`new_entrants`: who arrived recently and what they are trying to control. "
    "`watch_for`: the one thing whose presence or absence in the next months "
    "would change the read. Ground every sentence in the developments supplied; "
    "never speculate beyond them."
)


class DevelopmentNote(BaseModel):
    """One development's evidentiary text, as the reading's input."""

    slug: str
    title: str
    summary: str = ""


class ReadingResponse(BaseModel):
    stance: str
    adoption_shape: str
    new_entrants: str
    watch_for: str


class Reading(BaseModel):
    subject_kind: SubjectKind
    subject_slug: str
    stance: str
    adoption_shape: str
    new_entrants: str
    watch_for: str
    built_from: list[str] = Field(default_factory=list)
    development_count: int = 0
    generated_at: datetime
    # Set by the human merge, never by the pipeline.
    merged_at: datetime | None = None


async def build_reading(
    model: StructuredModel,
    *,
    subject_kind: SubjectKind,
    subject_slug: str,
    developments: list[DevelopmentNote],
    now: datetime,
) -> Reading | None:
    """Generate one reading, or None when there is nothing to read from.

    A subject with no developments in the window is skipped rather than given an
    invented reading.
    """
    if not developments:
        return None
    lines = [f"{subject_kind}: {subject_slug}", "", "developments:"]
    for note in developments:
        lines.append(f"- {note.title}")
        if note.summary:
            lines.append(f"  {note.summary}")
    raw = await model.generate(
        response_model=ReadingResponse,
        system_instruction=_SYSTEM,
        prompt="\n".join(lines),
    )
    return Reading(
        subject_kind=subject_kind,
        subject_slug=subject_slug,
        stance=raw.stance.strip(),
        adoption_shape=raw.adoption_shape.strip(),
        new_entrants=raw.new_entrants.strip(),
        watch_for=raw.watch_for.strip(),
        built_from=[note.slug for note in developments],
        development_count=len(developments),
        generated_at=now,
    )


def save_reading(readings_dir: Path, reading: Reading) -> Path:
    """Write one reading atomically as `<kind>-<slug>.json`."""
    readings_dir.mkdir(parents=True, exist_ok=True)
    path = readings_dir / f"{reading.subject_kind}-{reading.subject_slug}.json"
    payload = json.dumps(reading.model_dump(mode="json"), indent=2, ensure_ascii=False)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload + "\n")
    os.replace(temporary, path)
    return path
