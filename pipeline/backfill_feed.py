"""Bounded, resumable publication of historical direct-source evidence."""
from __future__ import annotations

import argparse
import asyncio
import os
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from pipeline.analyzer import AnalysisResult, analyze_change
from pipeline.backfill import (
    BackfillEntry,
    BackfillManifest,
    BackfillOutcome,
    batch_id,
    load_manifest,
    manifest_path,
    save_manifest,
    select_candidates,
)
from pipeline.event_writer import event_slug, write_event
from pipeline.feed import publication_status, should_promote
from pipeline.feed_writer import write_feed_item
from pipeline.model_provider import (
    GeminiStructuredModel,
    ProviderCircuit,
    ProviderFailure,
    StructuredModel,
)
from pipeline.relevance import RelevanceVerdict, keyword_match, model_relevance
from pipeline.sources import Source, load_sources

Analyze = Callable[..., Awaitable[AnalysisResult]]
Relevance = Callable[[StructuredModel, str, str], Awaitable[RelevanceVerdict]]


class BackfillSummary(BaseModel):
    batch_id: str
    eligible: int
    attempted: int
    remaining: int
    published: int
    irrelevant: int
    duplicate: int
    excluded: int
    failed: int
    provider_status: str


async def run_backfill(
    *,
    repo_root: Path,
    since: datetime,
    until: datetime,
    limit: int,
    model: StructuredModel | None,
    now: datetime,
    dry_run: bool = False,
    analyze: Analyze = analyze_change,
    relevance: Relevance = model_relevance,
) -> BackfillSummary:
    if since.tzinfo is None or until.tzinfo is None or now.tzinfo is None:
        raise ValueError("backfill timestamps must include a timezone")
    if since > until:
        raise ValueError("since must be on or before until")
    if limit <= 0:
        raise ValueError("limit must be positive")
    if model is None and not dry_run:
        raise ValueError("a structured model is required outside dry-run")

    sources = load_sources(repo_root / "sources.yaml")
    selection = select_candidates(
        evidence_dir=repo_root / "content/evidence",
        feed_dir=repo_root / "content/feed",
        sources=sources,
        since=since,
        until=until,
    )
    current_batch_id = batch_id(since, until)

    if dry_run:
        return BackfillSummary(
            batch_id=current_batch_id,
            eligible=selection.counts.eligible,
            attempted=0,
            remaining=selection.counts.eligible,
            published=0,
            irrelevant=0,
            duplicate=selection.counts.duplicate,
            excluded=selection.counts.excluded_search + selection.counts.unknown_source,
            failed=0,
            provider_status="dry-run",
        )

    progress_path = manifest_path(repo_root / "data", since, until)
    manifest = load_manifest(progress_path, since=since, until=until)
    _record_selection_exclusions(manifest, selection, now)
    save_manifest(progress_path, manifest)

    unfinished = [
        candidate
        for candidate in selection.candidates
        if not _is_terminal(manifest.entries.get(candidate.record.evidence_id))
    ]
    attempted = 0
    published = 0
    irrelevant = 0
    failed = 0
    circuit = ProviderCircuit()

    for candidate in unfinished[:limit]:
        if circuit.is_open:
            break
        attempted += 1
        record = candidate.record
        try:
            if record.title is not None:
                searchable = f"{record.title}\n{record.content}"
                if not keyword_match(searchable, candidate.source.keyword_filter or []):
                    irrelevant += 1
                    _record_outcome(
                        manifest,
                        evidence_id=record.evidence_id,
                        outcome=BackfillOutcome.IRRELEVANT,
                        updated_at=now,
                        reason="keyword filter",
                    )
                    save_manifest(progress_path, manifest)
                    continue
                verdict = await relevance(model, record.title, record.content)  # type: ignore[arg-type]
                if not verdict.is_relevant:
                    irrelevant += 1
                    _record_outcome(
                        manifest,
                        evidence_id=record.evidence_id,
                        outcome=BackfillOutcome.IRRELEVANT,
                        updated_at=now,
                        reason=verdict.reason,
                    )
                    save_manifest(progress_path, manifest)
                    continue

            analysis = await analyze(
                model=model,
                source=candidate.source,
                prev_content=record.previous_content,
                curr_content=record.content,
                unified_diff=record.unified_diff,
                item_url=record.source_url,
                published_at=record.published_at,
            )
            if analysis.change_kind != "material":
                irrelevant += 1
                _record_outcome(
                    manifest,
                    evidence_id=record.evidence_id,
                    outcome=BackfillOutcome.IRRELEVANT,
                    updated_at=now,
                    reason=analysis.change_kind,
                )
                save_manifest(progress_path, manifest)
                continue

            feed_path, development_path = _publish_candidate(
                repo_root=repo_root,
                source=candidate.source,
                analysis=analysis,
                item_date=candidate.item_date,
                detected_at=record.detected_at,
                evidence_id=record.evidence_id,
                source_url=record.source_url,
                unified_diff=record.unified_diff,
                processed_at=now,
                current_batch_id=current_batch_id,
            )
            published += 1
            _record_outcome(
                manifest,
                evidence_id=record.evidence_id,
                outcome=BackfillOutcome.PUBLISHED,
                updated_at=now,
                feed_path=str(feed_path.relative_to(repo_root)),
                development_path=(
                    str(development_path.relative_to(repo_root))
                    if development_path is not None
                    else None
                ),
            )
        except ProviderFailure as error:
            failed += 1
            circuit.open(error)
            _record_outcome(
                manifest,
                evidence_id=record.evidence_id,
                outcome=BackfillOutcome.FAILED,
                updated_at=now,
                reason=str(error),
            )
        except Exception as error:
            failed += 1
            _record_outcome(
                manifest,
                evidence_id=record.evidence_id,
                outcome=BackfillOutcome.FAILED,
                updated_at=now,
                reason=str(error),
            )
        save_manifest(progress_path, manifest)

    remaining = sum(
        1
        for candidate in selection.candidates
        if not _is_terminal(manifest.entries.get(candidate.record.evidence_id))
    )
    summary = BackfillSummary(
        batch_id=current_batch_id,
        eligible=selection.counts.eligible,
        attempted=attempted,
        remaining=remaining,
        published=published,
        irrelevant=irrelevant,
        duplicate=selection.counts.duplicate,
        excluded=selection.counts.excluded_search + selection.counts.unknown_source,
        failed=failed,
        provider_status="blocked" if circuit.is_open else "ok",
    )
    manifest.summary = summary.model_dump(mode="json")
    save_manifest(progress_path, manifest)
    return summary


def _is_terminal(entry: BackfillEntry | None) -> bool:
    return entry is not None and entry.outcome.is_terminal


def _record_selection_exclusions(manifest, selection, now: datetime) -> None:
    groups = (
        (selection.excluded_search_ids, BackfillOutcome.EXCLUDED_SOURCE, "Gemini Search evidence"),
        (selection.unknown_source_ids, BackfillOutcome.EXCLUDED_SOURCE, "unknown source"),
        (selection.outside_window_ids, BackfillOutcome.OUTSIDE_WINDOW, "outside requested window"),
        (selection.duplicate_ids, BackfillOutcome.DUPLICATE, "already published"),
    )
    for evidence_ids, outcome, reason in groups:
        for evidence_id in evidence_ids:
            if not _is_terminal(manifest.entries.get(evidence_id)):
                _record_outcome(
                    manifest,
                    evidence_id=evidence_id,
                    outcome=outcome,
                    updated_at=now,
                    reason=reason,
                )


def _record_outcome(
    manifest: BackfillManifest,
    *,
    evidence_id: str,
    outcome: BackfillOutcome,
    updated_at: datetime,
    feed_path: str | None = None,
    development_path: str | None = None,
    reason: str | None = None,
) -> None:
    manifest.entries[evidence_id] = BackfillEntry(
        evidence_id=evidence_id,
        outcome=outcome,
        updated_at=updated_at,
        feed_path=feed_path,
        development_path=development_path,
        reason=reason,
    )


def _publish_candidate(
    *,
    repo_root: Path,
    source: Source,
    analysis: AnalysisResult,
    item_date: datetime,
    detected_at: datetime,
    evidence_id: str,
    source_url: str,
    unified_diff: str,
    processed_at: datetime,
    current_batch_id: str,
) -> tuple[Path, Path | None]:
    status = publication_status(source)
    development_path = None
    development_slug = None
    if should_promote(status, analysis):
        development_path = write_event(
            events_dir=repo_root / "content/events",
            source=source,
            analysis=analysis,
            event_date=item_date,
            published_at=item_date,
            detected_at=detected_at,
            evidence_ids=[evidence_id],
            unified_diff=unified_diff,
            source_url=source_url,
        )
        development_slug = event_slug(analysis.title)

    feed_path = write_feed_item(
        feed_dir=repo_root / "content/feed",
        source=source,
        analysis=analysis,
        status=status,
        event_date=item_date,
        published_at=item_date,
        detected_at=detected_at,
        evidence_ids=[evidence_id],
        source_urls=[source_url],
        unified_diff=unified_diff,
        development_slug=development_slug,
        backfilled=True,
        processed_at=processed_at,
        backfill_batch=current_batch_id,
    )
    return feed_path, development_path


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("timestamps must include a timezone")
    return parsed


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", type=_parse_timestamp, required=True)
    parser.add_argument("--until", type=_parse_timestamp, required=True)
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--direct-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


async def _main() -> int:
    parser = _parser()
    args = parser.parse_args()
    if args.limit <= 0:
        parser.error("--limit must be positive")
    if not args.direct_only:
        parser.error("--direct-only is required; search-derived backfill is unsupported")

    model = None
    if not args.dry_run:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            parser.error("GEMINI_API_KEY is required outside --dry-run")
        model = GeminiStructuredModel(
            api_key=api_key,
            model=os.environ.get("GEMINI_ANALYSIS_MODEL", "gemini-3.7-flash"),
        )
    summary = await run_backfill(
        repo_root=Path(os.environ.get("REPO_ROOT", Path.cwd())).resolve(),
        since=args.since,
        until=args.until,
        limit=args.limit,
        model=model,
        now=datetime.now(UTC),
        dry_run=args.dry_run,
    )
    print(summary.model_dump_json(indent=2))
    return 1 if summary.provider_status == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
