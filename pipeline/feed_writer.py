"""Write reader-facing daily feed items as Markdown with YAML frontmatter."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from pipeline.analyzer import AnalysisResult
from pipeline.feed import PublicationStatus
from pipeline.sources import Source

_SLUG_RX = re.compile(r"[^a-z0-9]+")


def write_feed_item(
    *,
    feed_dir: Path,
    source: Source,
    analysis: AnalysisResult,
    status: PublicationStatus,
    event_date: datetime,
    published_at: datetime,
    detected_at: datetime,
    evidence_ids: list[str],
    source_urls: list[str],
    unified_diff: str,
    development_slug: str | None = None,
    backfilled: bool = False,
    processed_at: datetime | None = None,
    backfill_batch: str | None = None,
) -> Path:
    if backfilled and (processed_at is None or not backfill_batch):
        raise ValueError("backfilled feed items require processed_at and backfill_batch")
    feed_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{source.slug}-{_slugify(analysis.title)}"
    path = feed_dir / f"{event_date.date().isoformat()}-{slug}.md"
    path.write_text(
        _compose(
            slug=slug,
            source=source,
            analysis=analysis,
            status=status,
            event_date=event_date,
            published_at=published_at,
            detected_at=detected_at,
            evidence_ids=evidence_ids,
            source_urls=source_urls,
            unified_diff=unified_diff,
            development_slug=development_slug,
            backfilled=backfilled,
            processed_at=processed_at,
            backfill_batch=backfill_batch,
        )
    )
    return path


def _slugify(value: str) -> str:
    return _SLUG_RX.sub("-", value.lower()).strip("-")[:80] or "untitled"


def _compose(
    *,
    slug: str,
    source: Source,
    analysis: AnalysisResult,
    status: PublicationStatus,
    event_date: datetime,
    published_at: datetime,
    detected_at: datetime,
    evidence_ids: list[str],
    source_urls: list[str],
    unified_diff: str,
    development_slug: str | None,
    backfilled: bool,
    processed_at: datetime | None,
    backfill_batch: str | None,
) -> str:
    frontmatter = (
        "---\n"
        "schema_version: 1\n"
        f"slug: {slug}\n"
        f'title: "{_yaml_escape(analysis.title)}"\n'
        f"source: {source.slug}\n"
        f"source_tier: {source.tier.value}\n"
        f"status: {status.value}\n"
        f"primary_track: {analysis.primary_track.value}\n"
        f"tracks:\n{_yaml_list(track.value for track in analysis.tracks)}"
        f"actors:\n{_yaml_list(analysis.actors, quoted=True)}"
        f"event_date: {event_date.isoformat()}\n"
        f"published_at: {published_at.isoformat()}\n"
        f"detected_at: {detected_at.isoformat()}\n"
        f"source_urls:\n{_yaml_list(source_urls, quoted=True)}"
        f"change_kind: {analysis.change_kind}\n"
        f"importance: {analysis.importance:.2f}\n"
        f"confidence: {analysis.confidence}\n"
        f"evidence_ids:\n{_yaml_list(evidence_ids, quoted=True)}"
    )
    if development_slug:
        frontmatter += f"development_slug: {development_slug}\n"
    frontmatter += f"backfilled: {str(backfilled).lower()}\n"
    if backfilled:
        frontmatter += f"processed_at: {processed_at.isoformat()}\n"
        frontmatter += f"backfill_batch: {backfill_batch}\n"
    frontmatter += "---\n\n"

    body = (
        f"## Summary\n\n{analysis.summary}\n\n"
        f"## Insight\n\n{analysis.insight}\n\n"
        f"## Implication\n\n{analysis.implication}\n\n"
        f"## Why it matters\n\n{analysis.why_it_matters}\n\n"
        "## Evidence\n\n"
    )
    for index, url in enumerate(source_urls, start=1):
        label = "Primary source" if index == 1 else f"Supporting source {index}"
        body += f"- [{label}]({url})\n"
    body += "".join(f"- Evidence ID: `{item}`\n" for item in evidence_ids)
    if unified_diff.strip():
        body += (
            "\n<details><summary>View observed change</summary>\n\n"
            f"```diff\n{unified_diff}\n```\n\n</details>\n"
        )
    return frontmatter + body


def _yaml_escape(value: str) -> str:
    return value.replace('"', '\\"')


def _yaml_list(values, *, quoted: bool = False) -> str:
    items = list(dict.fromkeys(value for value in values if value))
    if not items:
        return "  []\n"
    if quoted:
        return "".join(f'  - "{_yaml_escape(value)}"\n' for value in items)
    return "".join(f"  - {value}\n" for value in items)
