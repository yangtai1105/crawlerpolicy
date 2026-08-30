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
    event_date: datetime,
    published_at: datetime,
    detected_at: datetime,
    evidence_ids: list[str],
    unified_diff: str,
    source_url: str | None = None,
) -> Path:
    events_dir.mkdir(parents=True, exist_ok=True)
    slug = _slugify(analysis.title)
    filename = f"{event_date.date().isoformat()}-{source.slug}-{slug}.md"
    path = events_dir / filename

    url = source_url or source.url or ""
    body = _compose(
        source=source,
        analysis=analysis,
        event_date=event_date,
        published_at=published_at,
        detected_at=detected_at,
        evidence_ids=evidence_ids,
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


def _compose(
    *,
    source,
    analysis,
    event_date,
    published_at,
    detected_at,
    evidence_ids,
    source_url,
    unified_diff,
    event_slug,
) -> str:
    frontmatter = (
        "---\n"
        "schema_version: 2\n"
        f"slug: {event_slug}\n"
        f'title: "{_yaml_escape(analysis.title)}"\n'
        f"source: {source.slug}\n"
        f"source_tier: {source.tier.value}\n"
        f"primary_track: {analysis.primary_track.value}\n"
        f"tracks:\n{_yaml_list(track.value for track in analysis.tracks)}"
        f"actors:\n{_yaml_list(analysis.actors, quoted=True)}"
        f"event_date: {event_date.isoformat()}\n"
        f"published_at: {published_at.isoformat()}\n"
        f"detected_at: {detected_at.isoformat()}\n"
        f'source_url: "{_yaml_escape(source_url or "")}"\n'
        f"change_kind: {analysis.change_kind}\n"
        f"importance: {analysis.importance:.2f}\n"
        f"confidence: {analysis.confidence}\n"
        f"evidence_ids:\n{_yaml_list(evidence_ids, quoted=True)}"
        "---\n\n"
    )

    body = f"## Development\n\n{analysis.what_changed}\n\n"
    implication = analysis.implication or "No material implication recorded."
    body += f"## Why it matters\n\n{implication}\n\n"
    body += "## Trend impact\n\n"
    if analysis.trend_signals:
        body += "\n".join(f"- {signal}" for signal in analysis.trend_signals) + "\n\n"
    else:
        body += "No durable trend signal identified.\n\n"
    body += "## Evidence\n\n"
    if source_url:
        body += f"- [Primary source]({source_url})\n"
    body += "\n".join(f"- Evidence ID: `{item}`" for item in evidence_ids)
    body += "\n\n"
    if unified_diff.strip():
        body += "<details><summary>View raw diff</summary>\n\n"
        body += f"```diff\n{unified_diff}\n```\n\n</details>\n"
    return frontmatter + body


def _yaml_escape(s: str) -> str:
    return s.replace('"', '\\"')


def _yaml_list(values, *, quoted: bool = False) -> str:
    items = list(values)
    if not items:
        return "  []\n"
    if quoted:
        return "".join(f'  - "{_yaml_escape(value)}"\n' for value in items)
    return "".join(f"  - {value}\n" for value in items)
