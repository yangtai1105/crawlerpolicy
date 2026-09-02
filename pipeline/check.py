"""Daily evidence-first orchestrator: fetch → evidence → analyze → publish."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from pipeline import raw_log
from pipeline.analyzer import AnalysisResult
from pipeline.analyzer import analyze_change as _default_analyze_change
from pipeline.config import Config
from pipeline.differ import compute_diff
from pipeline.event_writer import event_slug, write_event
from pipeline.evidence import (
    EvidenceRecord,
    EvidenceStage,
    make_evidence_id,
    pending_analysis,
    save_evidence,
)
from pipeline.feed import publication_status, should_promote
from pipeline.feed_writer import write_feed_item
from pipeline.fetchers.base import CandidateItem, FetchResult, ResultMode
from pipeline.fetchers.cf_browser_run import fetch_cf_browser_run
from pipeline.fetchers.gemini_search import fetch_gemini_search
from pipeline.fetchers.github_repo import fetch_github_repo
from pipeline.fetchers.html_page import fetch_html_page
from pipeline.fetchers.ietf_draft import fetch_ietf_draft
from pipeline.fetchers.rss_feed import fetch_rss_feed
from pipeline.health import (
    HealthStatus,
    SourceRunStatus,
    StageStatus,
    build_run_health,
    exit_code_for_health,
)
from pipeline.model_provider import (
    GeminiStructuredModel,
    ProviderCircuit,
    ProviderFailure,
    StructuredModel,
)
from pipeline.relevance import keyword_match, model_relevance
from pipeline.snapshots import hash_content, load_latest, save_snapshot
from pipeline.sources import Source, SourceType, load_sources
from pipeline.state import SourceState, load_state, save_state
from pipeline.state_of_play import build_opt_out_matrix, select_crawler_control_sources
from pipeline.taxonomy import Track
from pipeline.trend_context import format_trend_context, load_recent_events_for_source

log = logging.getLogger("check")

FetchDispatch = Callable[[Source, SourceState], Awaitable[FetchResult]]


@dataclass(frozen=True)
class DependencyBlocker:
    stage: str
    message: str


def _maybe_trend_context(cfg: Config, source: Source) -> str:
    if Track.CRAWLER_CONTROLS in source.default_tracks:
        return ""
    recent = load_recent_events_for_source(cfg.events_dir, source.slug, limit=10)
    return format_trend_context(recent)


async def _default_fetch(source: Source, state: SourceState) -> FetchResult:
    if source.type is SourceType.HTML_PAGE:
        return await fetch_html_page(source)
    if source.type is SourceType.RSS_FEED:
        return await fetch_rss_feed(
            source,
            since=state.last_checked_at,
            seen_guids=state.last_seen_guids,
        )
    if source.type is SourceType.GITHUB_REPO:
        return await fetch_github_repo(
            source,
            since=state.last_checked_at,
            seen_guids=state.last_seen_guids,
        )
    if source.type is SourceType.IETF_DRAFT:
        return await fetch_ietf_draft(source)
    if source.type is SourceType.GEMINI_SEARCH:
        return await fetch_gemini_search(
            source,
            since=state.last_checked_at,
            seen_guids=state.last_seen_guids,
        )
    if source.type is SourceType.CF_BROWSER_RUN:
        return await fetch_cf_browser_run(source)
    raise ValueError(f"unknown source type {source.type}")


def preflight_dependency_errors(
    sources: list[Source], environ: Mapping[str, str]
) -> dict[str, DependencyBlocker]:
    """Map missing credentials to the source stage they disable."""
    def present(name: str) -> bool:
        return bool(environ.get(name, "").strip())

    blockers: dict[str, DependencyBlocker] = {}
    for source in sources:
        if not source.enabled:
            continue
        if source.type is SourceType.GEMINI_SEARCH and not present("GEMINI_API_KEY"):
            blockers[source.slug] = DependencyBlocker(
                stage="fetch",
                message="GEMINI_API_KEY is missing",
            )
            continue
        if source.type is SourceType.CF_BROWSER_RUN:
            required = (
                "CLOUDFLARE_ACCOUNT_ID",
                "CLOUDFLARE_EMAIL",
                "CLOUDFLARE_CRAWLER_API_KEY",
            )
            missing = [name for name in required if not present(name)]
            if missing:
                blockers[source.slug] = DependencyBlocker(
                    stage="fetch",
                    message=f"missing Cloudflare credentials: {', '.join(missing)}",
                )
                continue
        if not present("GEMINI_API_KEY"):
            blockers[source.slug] = DependencyBlocker(
                stage="analysis",
                message="GEMINI_API_KEY is missing",
            )
    return blockers


async def run_check(
    *,
    repo_root: Path,
    now: datetime,
    fetch_dispatch: FetchDispatch | None = None,
    analyze_change: Callable = _default_analyze_change,
    extract_sop: Callable | None = None,
    model: StructuredModel | None = None,
    publication_cutoff: datetime | None = None,
    only: str | None = None,
    dry_run: bool = False,
    dependency_blockers: dict[str, DependencyBlocker] | None = None,
) -> dict:
    """Run the pipeline and return a JSON-serializable health payload."""
    cfg = Config(
        repo_root=repo_root,
        gemini_api_key="",
        gemini_analysis_model="gemini-3.7-flash",
        publication_cutoff=publication_cutoff
        or datetime(2026, 8, 30, tzinfo=UTC),
        alert_emails=[],
    )
    sources = [source for source in load_sources(cfg.sources_yaml) if source.enabled]
    if only:
        sources = [source for source in sources if source.slug == only]
        if not sources:
            raise ValueError(f"--only {only!r} did not match any source")

    fetch_dispatch = fetch_dispatch or _default_fetch
    blockers = dependency_blockers or {}
    statuses = {source.slug: SourceRunStatus() for source in sources}
    source_by_slug = {source.slug: source for source in sources}
    events_written: list[Path] = []
    circuit = ProviderCircuit()

    await _replay_pending(
        cfg=cfg,
        sources=source_by_slug,
        statuses=statuses,
        blockers=blockers,
        model=model,
        circuit=circuit,
        analyze_change=analyze_change,
        events_written=events_written,
        dry_run=dry_run,
    )

    for source in sources:
        state = load_state(cfg.state_dir, source.slug)
        status = statuses[source.slug]
        blocker = blockers.get(source.slug)
        if blocker and blocker.stage == "fetch":
            status.fetch = StageStatus.FAILED
            status.error = blocker.message
            state.consecutive_failures += 1
            if not dry_run:
                save_state(cfg.state_dir, source.slug, state)
            continue

        try:
            result = await _fetch_source(fetch_dispatch, source, state)
            status.fetch = StageStatus.OK
            state.last_checked_at = now
            state.last_fetch_succeeded_at = now
            state.consecutive_failures = 0
            new_events, state = await _process_result(
                source=source,
                state=state,
                result=result,
                now=now,
                cfg=cfg,
                model=model,
                circuit=circuit,
                analyze_change=analyze_change,
                status=status,
                analysis_blocker=(
                    blocker.message
                    if blocker is not None and blocker.stage == "analysis"
                    else None
                ),
                dry_run=dry_run,
            )
            events_written.extend(new_events)
            if not dry_run:
                save_state(cfg.state_dir, source.slug, state)
        except Exception as error:
            log.exception("fetch/evidence failed for %s", source.slug)
            if status.fetch is StageStatus.PENDING:
                status.fetch = StageStatus.FAILED
            if status.evidence is StageStatus.PENDING:
                status.evidence = StageStatus.FAILED
            status.error = str(error)
            state.consecutive_failures += 1
            if not dry_run:
                save_state(cfg.state_dir, source.slug, state)

    derived_errors: list[str] = []
    if extract_sop is not None and not dry_run:
        try:
            await extract_sop(sources=sources, repo_root=repo_root, now=now)
        except Exception as error:
            log.exception("state_of_play failed")
            derived_errors.append(f"state_of_play: {error}")

    previous_success = _load_last_full_success(cfg.data_dir / "health.json")
    health = build_run_health(
        sources=sources,
        per_source=statuses,
        now=now,
        last_full_success=previous_success,
    )
    payload = health.model_dump(mode="json")
    payload["events_written"] = [
        str(path.relative_to(repo_root)) for path in events_written
    ]
    payload["feed_items_written"] = [
        path
        for source_status in statuses.values()
        for path in source_status.feed_items_written
    ]
    provider_error = str(circuit.failure) if circuit.failure else None
    provider_unavailable = any(
        blocker.stage == "analysis" for blocker in blockers.values()
    )
    payload["provider"] = {
        "name": "gemini",
        "status": (
            "blocked"
            if circuit.is_open
            else "unavailable"
            if provider_unavailable
            else "ok"
        ),
        "error": provider_error,
    }
    payload["derived_errors"] = derived_errors
    if not dry_run:
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        (cfg.data_dir / "health.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        )
    return payload


async def _fetch_source(
    fetch_dispatch: FetchDispatch,
    source: Source,
    state: SourceState,
) -> FetchResult:
    return await fetch_dispatch(source, state)


async def _process_result(
    *,
    source: Source,
    state: SourceState,
    result: FetchResult,
    now: datetime,
    cfg: Config,
    model: StructuredModel | None,
    circuit: ProviderCircuit,
    analyze_change: Callable,
    status: SourceRunStatus,
    analysis_blocker: str | None,
    dry_run: bool,
) -> tuple[list[Path], SourceState]:
    if result.mode is ResultMode.DIFFABLE:
        return await _process_diffable(
            source=source,
            state=state,
            result=result,
            now=now,
            cfg=cfg,
            model=model,
            circuit=circuit,
            analyze_change=analyze_change,
            status=status,
            analysis_blocker=analysis_blocker,
            dry_run=dry_run,
        )
    return await _process_items(
        source=source,
        state=state,
        result=result,
        now=now,
        cfg=cfg,
        model=model,
        circuit=circuit,
        analyze_change=analyze_change,
        status=status,
        analysis_blocker=analysis_blocker,
        dry_run=dry_run,
    )


async def _process_diffable(
    *,
    source: Source,
    state: SourceState,
    result: FetchResult,
    now: datetime,
    cfg: Config,
    model: StructuredModel | None,
    circuit: ProviderCircuit,
    analyze_change: Callable,
    status: SourceRunStatus,
    analysis_blocker: str | None,
    dry_run: bool,
) -> tuple[list[Path], SourceState]:
    current = result.normalized_content or ""
    new_hash = hash_content(current)
    if state.last_hash == new_hash:
        _mark_downstream_ok(status)
        if analysis_blocker:
            _mark_analysis_failed(status, analysis_blocker)
        return [], state

    previous = load_latest(cfg.snapshots_dir, source.slug)
    snapshot_path = cfg.snapshots_dir / source.slug / f"{now.date()}.{result.raw_ext}"
    if not dry_run:
        snapshot_path = save_snapshot(
            cfg.snapshots_dir,
            source.slug,
            now,
            content=current,
            ext=result.raw_ext,
        )
    is_catchup = (
        state.first_seen or previous is None
    ) and source.type is not SourceType.GEMINI_SEARCH
    if is_catchup or (previous is not None and previous[0] == current):
        state.first_seen = False
        state.last_hash = new_hash
        _mark_downstream_ok(status)
        if analysis_blocker:
            _mark_analysis_failed(status, analysis_blocker)
        return [], state

    previous_content = previous[0] if previous is not None else ""
    diff = compute_diff(previous_content, current)
    if not diff.has_changes:
        state.last_hash = new_hash
        _mark_downstream_ok(status)
        return [], state

    record = EvidenceRecord(
        evidence_id=make_evidence_id(source.slug, new_hash),
        source=source.slug,
        source_url=source.url or "",
        published_at=now,
        detected_at=now,
        content_path=_relative_path(snapshot_path, cfg.repo_root),
        content_hash=f"sha256:{new_hash}",
        external_id=new_hash,
        stage=EvidenceStage.FETCHED,
        content=current,
        previous_content=previous_content,
        unified_diff=diff.unified_diff,
    )
    _record_evidence(cfg, record, status, dry_run)
    state.last_hash = new_hash
    state.last_evidence_at = now
    if analysis_blocker:
        _fail_evidence_analysis(cfg, record, analysis_blocker, status, dry_run)
        return [], state

    event = await _analyze_and_publish(
        cfg=cfg,
        source=source,
        record=record,
        model=model,
        circuit=circuit,
        analyze_change=analyze_change,
        status=status,
        dry_run=dry_run,
    )
    return ([event] if event is not None else []), state


async def _process_items(
    *,
    source: Source,
    state: SourceState,
    result: FetchResult,
    now: datetime,
    cfg: Config,
    model: StructuredModel | None,
    circuit: ProviderCircuit,
    analyze_change: Callable,
    status: SourceRunStatus,
    analysis_blocker: str | None,
    dry_run: bool,
) -> tuple[list[Path], SourceState]:
    events: list[Path] = []
    items = result.items

    if not items:
        _mark_downstream_ok(status)
        if analysis_blocker:
            _mark_analysis_failed(status, analysis_blocker)

    for item in items:
        if item.guid in state.last_seen_guids:
            continue
        record = _evidence_for_item(source, item, now)
        _record_evidence(cfg, record, status, dry_run)
        state.last_seen_guids.append(item.guid)
        state.last_evidence_at = now
        if not _is_after_publication_cutoff(record, cfg.publication_cutoff):
            record.stage = EvidenceStage.SKIPPED_CUTOFF
            record.last_error = "item predates publication cutoff"
            if not dry_run:
                save_evidence(cfg.evidence_dir, record)
            _mark_downstream_ok(status)
            continue
        if analysis_blocker:
            _fail_evidence_analysis(cfg, record, analysis_blocker, status, dry_run)
            continue
        event = await _analyze_and_publish(
            cfg=cfg,
            source=source,
            record=record,
            model=model,
            circuit=circuit,
            analyze_change=analyze_change,
            status=status,
            dry_run=dry_run,
        )
        if event is not None:
            events.append(event)

    state.first_seen = False
    state.last_seen_guids = state.last_seen_guids[-500:]
    return events, state


def _evidence_for_item(
    source: Source,
    item: CandidateItem,
    now: datetime,
) -> EvidenceRecord:
    evidence_id = make_evidence_id(source.slug, item.guid)
    relative_path = Path("content") / "evidence" / source.slug / f"{evidence_id}.json"
    content = item.body or item.summary
    return EvidenceRecord(
        evidence_id=evidence_id,
        source=source.slug,
        source_url=item.url or source.url or "",
        published_at=item.published_at,
        detected_at=now,
        content_path=relative_path.as_posix(),
        content_hash=f"sha256:{hash_content(content)}",
        external_id=item.guid,
        stage=EvidenceStage.FETCHED,
        title=item.title,
        content=content,
    )


def _record_evidence(
    cfg: Config,
    record: EvidenceRecord,
    status: SourceRunStatus,
    dry_run: bool,
) -> None:
    if not dry_run:
        save_evidence(cfg.evidence_dir, record)
    if status.evidence is not StageStatus.FAILED:
        status.evidence = StageStatus.OK
    if record.evidence_id not in status.evidence_ids:
        status.evidence_ids.append(record.evidence_id)


async def _analyze_and_publish(
    *,
    cfg: Config,
    source: Source,
    record: EvidenceRecord,
    model: StructuredModel | None,
    circuit: ProviderCircuit,
    analyze_change: Callable,
    status: SourceRunStatus,
    dry_run: bool,
) -> Path | None:
    if circuit.is_open:
        message = str(circuit.failure)
        record.last_error = message
        if not dry_run:
            save_evidence(cfg.evidence_dir, record)
        _mark_analysis_failed(status, message)
        return None
    try:
        analysis = await _analyze_evidence(
            cfg=cfg,
            source=source,
            record=record,
            model=model,
            analyze_change=analyze_change,
            dry_run=dry_run,
        )
        if status.analysis is not StageStatus.FAILED:
            status.analysis = StageStatus.OK
        if analysis is None or analysis.change_kind != "material":
            if status.publish is not StageStatus.FAILED:
                status.publish = StageStatus.OK
            return None
        event, feed_item = _publish_analysis(
            cfg=cfg,
            source=source,
            record=record,
            analysis=analysis,
            dry_run=dry_run,
        )
        if status.publish is not StageStatus.FAILED:
            status.publish = StageStatus.OK
        if event is not None:
            status.events_written.append(_relative_path(event, cfg.repo_root))
        if feed_item is not None:
            status.feed_items_written.append(_relative_path(feed_item, cfg.repo_root))
        return event
    except Exception as error:
        log.exception(
            "analysis/publish failed for %s evidence %s",
            source.slug,
            record.evidence_id,
        )
        if isinstance(error, ProviderFailure):
            circuit.open(error)
        _fail_evidence_analysis(cfg, record, str(error), status, dry_run)
        return None


async def _analyze_evidence(
    *,
    cfg: Config,
    source: Source,
    record: EvidenceRecord,
    model: StructuredModel | None,
    analyze_change: Callable,
    dry_run: bool,
) -> AnalysisResult | None:
    if record.title is not None:
        blob = f"{record.title}\n{record.content}"
        if not keyword_match(blob, source.keyword_filter or []):
            record.stage = EvidenceStage.ANALYZED
            record.last_error = None
            if not dry_run:
                save_evidence(cfg.evidence_dir, record)
            return None
        verdict = (
            await model_relevance(model, record.title, record.content)
            if model is not None
            else None
        )
        if verdict is not None and not verdict.is_relevant:
            record.stage = EvidenceStage.ANALYZED
            record.last_error = None
            if not dry_run:
                save_evidence(cfg.evidence_dir, record)
                _append_raw_record(
                    cfg,
                    source,
                    record,
                    keyword_pass=True,
                    relevance_pass=False,
                )
            return None

    analysis = await analyze_change(
        model=model,
        source=source,
        prev_content=record.previous_content,
        curr_content=record.content,
        unified_diff=record.unified_diff,
        trend_context=_maybe_trend_context(cfg, source),
        item_url=record.source_url or None,
        published_at=record.published_at,
    )
    record.analysis_attempts += 1
    record.stage = EvidenceStage.ANALYZED
    record.last_error = None
    if not dry_run:
        save_evidence(cfg.evidence_dir, record)
        if record.title is not None:
            _append_raw_record(
                cfg,
                source,
                record,
                keyword_pass=True,
                relevance_pass=True,
                analysis=analysis,
            )
    return analysis


def _publish_analysis(
    *,
    cfg: Config,
    source: Source,
    record: EvidenceRecord,
    analysis: AnalysisResult,
    dry_run: bool,
) -> tuple[Path | None, Path | None]:
    if dry_run:
        return None, None
    event_date = record.published_at or record.detected_at
    status = publication_status(source)
    development_path = (
        write_event(
            events_dir=cfg.events_dir,
            source=source,
            analysis=analysis,
            event_date=event_date,
            published_at=record.published_at or event_date,
            detected_at=record.detected_at,
            evidence_ids=[record.evidence_id],
            unified_diff=record.unified_diff,
            source_url=record.source_url,
        )
        if should_promote(status, analysis)
        else None
    )
    feed_path = write_feed_item(
        feed_dir=cfg.feed_dir,
        source=source,
        analysis=analysis,
        status=status,
        event_date=event_date,
        published_at=record.published_at or event_date,
        detected_at=record.detected_at,
        evidence_ids=[record.evidence_id],
        source_urls=[record.source_url] if record.source_url else [],
        unified_diff=record.unified_diff,
        development_slug=(
            event_slug(analysis.title) if development_path is not None else None
        ),
    )
    record.stage = EvidenceStage.PUBLISHED
    record.last_error = None
    save_evidence(cfg.evidence_dir, record)
    return development_path, feed_path


async def _replay_pending(
    *,
    cfg: Config,
    sources: dict[str, Source],
    statuses: dict[str, SourceRunStatus],
    blockers: dict[str, DependencyBlocker],
    model: StructuredModel | None,
    circuit: ProviderCircuit,
    analyze_change: Callable,
    events_written: list[Path],
    dry_run: bool,
) -> None:
    for _path, record in pending_analysis(cfg.evidence_dir):
        source = sources.get(record.source)
        if source is None:
            continue
        status = statuses[source.slug]
        status.evidence = StageStatus.OK
        if record.evidence_id not in status.evidence_ids:
            status.evidence_ids.append(record.evidence_id)
        if not _is_after_publication_cutoff(record, cfg.publication_cutoff):
            record.stage = EvidenceStage.SKIPPED_CUTOFF
            record.last_error = "item predates publication cutoff"
            if not dry_run:
                save_evidence(cfg.evidence_dir, record)
            _mark_downstream_ok(status)
            continue
        blocker = blockers.get(source.slug)
        if blocker and blocker.stage == "analysis":
            _fail_evidence_analysis(cfg, record, blocker.message, status, dry_run)
            continue
        event = await _analyze_and_publish(
            cfg=cfg,
            source=source,
            record=record,
            model=model,
            circuit=circuit,
            analyze_change=analyze_change,
            status=status,
            dry_run=dry_run,
        )
        if event is not None:
            events_written.append(event)


def _fail_evidence_analysis(
    cfg: Config,
    record: EvidenceRecord,
    message: str,
    status: SourceRunStatus,
    dry_run: bool,
) -> None:
    record.stage = EvidenceStage.FAILED_ANALYSIS
    record.analysis_attempts += 1
    record.last_error = message
    if not dry_run:
        save_evidence(cfg.evidence_dir, record)
    _mark_analysis_failed(status, message)


def _mark_analysis_failed(status: SourceRunStatus, message: str) -> None:
    status.analysis = StageStatus.FAILED
    status.publish = StageStatus.FAILED
    status.error = message


def _mark_downstream_ok(status: SourceRunStatus) -> None:
    for name in ("evidence", "analysis", "publish"):
        if getattr(status, name) is not StageStatus.FAILED:
            setattr(status, name, StageStatus.OK)


def _append_raw_record(
    cfg: Config,
    source: Source,
    record: EvidenceRecord,
    *,
    keyword_pass: bool,
    relevance_pass: bool,
    analysis: AnalysisResult | None = None,
) -> None:
    raw_log.append(
        cfg.raw_dir,
        source.slug,
        guid=record.external_id,
        title=record.title or "",
        summary=record.content,
        url=record.source_url,
        published_at=record.published_at,
        keyword_pass=keyword_pass,
        relevance_pass=relevance_pass,
        change_kind=analysis.change_kind if analysis else None,
        importance=analysis.importance if analysis else None,
        recorded_at=record.detected_at,
    )


def _relative_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _is_after_publication_cutoff(
    record: EvidenceRecord,
    cutoff: datetime,
) -> bool:
    item_date = record.published_at or record.detected_at
    return item_date >= cutoff


def _load_last_full_success(path: Path) -> datetime | None:
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text())
        value = raw.get("last_fully_successful_at")
        return datetime.fromisoformat(value) if value else None
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def _write_workflow_summary(payload: dict) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with Path(summary_path).open("a") as handle:
        handle.write("## Daily intelligence health\n\n")
        handle.write(f"Status: **{payload['status']}**\n\n")
        handle.write("```json\n")
        handle.write(json.dumps(payload["coverage"], indent=2))
        handle.write("\n```\n")


def _cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", type=str, default=None)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    cfg = Config.from_env()
    model = (
        GeminiStructuredModel(
            api_key=cfg.gemini_api_key,
            model=cfg.gemini_analysis_model,
        )
        if cfg.gemini_api_key
        else None
    )
    configured_sources = [
        source for source in load_sources(cfg.sources_yaml) if source.enabled
    ]
    if args.only:
        configured_sources = [
            source for source in configured_sources if source.slug == args.only
        ]
    blockers = preflight_dependency_errors(configured_sources, os.environ)

    async def _sop(sources, repo_root, now):
        from pipeline import snapshots as snap_mod

        crawler_sources = select_crawler_control_sources(sources)

        def _load(slug: str):
            return snap_mod.load_latest(cfg.snapshots_dir, slug)

        await build_opt_out_matrix(
            model=model,
            crawler_sources=crawler_sources,
            load_latest_snapshot=_load,
            out_path=cfg.data_dir / "opt-out-matrix.json",
            now=now,
        )

    payload = asyncio.run(
        run_check(
            repo_root=cfg.repo_root,
            now=datetime.now(tz=UTC),
            model=model,
            publication_cutoff=cfg.publication_cutoff,
            extract_sop=_sop if model else None,
            only=args.only,
            dry_run=args.dry_run,
            dependency_blockers=blockers,
        )
    )
    print(json.dumps(payload, indent=2))
    _write_workflow_summary(payload)
    raise SystemExit(exit_code_for_health(HealthStatus(payload["status"])))


if __name__ == "__main__":
    _cli()
