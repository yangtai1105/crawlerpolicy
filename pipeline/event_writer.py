"""Write a detected event as markdown with YAML frontmatter."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from pipeline.analyzer import AnalysisResult
from pipeline.sources import Source


def write_event(
    *,
    events_dir: Path,
    source: Source,
    analysis: AnalysisResult,
    detected_at: datetime,
    unified_diff: str,
    source_url: str | None = None,
) -> Path:
    events_dir.mkdir(parents=True, exist_ok=True)
    slug = _slugify(analysis.title)
    filename = f"{detected_at.date().isoformat()}-{source.slug}-{slug}.md"
    path = events_dir / filename

    url = source_url or source.url or ""
    body = _compose(
        source=source,
        analysis=analysis,
        detected_at=detected_at,
        source_url=url,
        unified_diff=unified_diff,
        event_slug=slug,
    )
    path.write_text(body)
    return path


_SLUG_RX = re.compile(r"[^a-z0-9]+")


def _slugify(title: str) -> str:
    s = _SLUG_RX.sub("-", title.lower()).strip("-")
    return s[:80] or "untitled"


def _compose(*, source, analysis, detected_at, source_url, unified_diff, event_slug) -> str:
    frontmatter = (
        "---\n"
        f"slug: {event_slug}\n"
        f'title: "{_yaml_escape(analysis.title)}"\n'
        f"source: {source.slug}\n"
        f"pillar: {source.pillar.value}\n"
        f"detected_at: {detected_at.isoformat()}\n"
        f'source_url: "{_yaml_escape(source_url or "")}"\n'
        f"change_kind: {analysis.change_kind}\n"
        f"importance: {analysis.importance:.2f}\n"
        "---\n\n"
    )
    # For the crawler pillar the raw diff is part of the signal (readers want to
    # see exactly which UA string or directive moved). For ecosystem + agent
    # news, the diff is either irrelevant (RSS — no prior) or noisy (Gemini
    # digest text diff) — lead with implication instead.
    pillar_is_crawler = source.pillar.value == "crawler"

    body = ""
    if analysis.implication.strip() and not pillar_is_crawler:
        body += f"## Implication\n\n{analysis.implication}\n\n"
    body += f"## What changed\n\n{analysis.what_changed}\n\n"
    if analysis.implication.strip() and pillar_is_crawler:
        body += f"## Implication\n\n{analysis.implication}\n\n"
    if unified_diff.strip() and pillar_is_crawler:
        body += "## Raw diff\n\n<details><summary>View diff</summary>\n\n"
        body += f"```diff\n{unified_diff}\n```\n\n</details>\n"
    return frontmatter + body


def _yaml_escape(s: str) -> str:
    return s.replace('"', '\\"')
