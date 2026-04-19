"""Daily orchestrator: fetch → diff/relevance → analyze → write → commit."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path

from anthropic import AsyncAnthropic

from pipeline import raw_log
from pipeline.analyzer import AnalysisResult
from pipeline.analyzer import analyze_change as _default_analyze_change
from pipeline.config import Config
from pipeline.differ import compute_diff
from pipeline.event_writer import write_event
from pipeline.fetchers.base import FetchResult, ResultMode
from pipeline.fetchers.github_repo import fetch_github_repo
from pipeline.fetchers.html_page import fetch_html_page
from pipeline.fetchers.ietf_draft import fetch_ietf_draft
from pipeline.fetchers.rss_feed import fetch_rss_feed
from pipeline.relevance import haiku_relevance, keyword_match
from pipeline.snapshots import hash_content, load_latest, save_snapshot
from pipeline.sources import Pillar, Source, SourceType, load_sources
from pipeline.state import SourceState, load_state, save_state
from pipeline.state_of_play import build_opt_out_matrix

log = logging.getLogger("check")

# On first-seen RSS/GitHub sources, process items from the last N days as
# events (instead of silently recording state). Avoids a wall of historical
# posts while still giving the site something to show at launch.
BACKFILL_DAYS = 30


FetchDispatch = Callable[[Source, SourceState], Awaitable[FetchResult]]


async def _default_fetch(source: Source, state: SourceState) -> FetchResult:
    if source.type == SourceType.HTML_PAGE:
        return await fetch_html_page(source)
    if source.type == SourceType.RSS_FEED:
        return await fetch_rss_feed(
            source, since=state.last_checked_at, seen_guids=state.last_seen_guids
        )
    if source.type == SourceType.GITHUB_REPO:
        return await fetch_github_repo(
            source, since=state.last_checked_at, seen_guids=state.last_seen_guids
        )
    if source.type == SourceType.IETF_DRAFT:
        return await fetch_ietf_draft(source)
    raise ValueError(f"unknown source type {source.type}")


async def run_check(
    *,
    repo_root: Path,
    now: datetime,
    fetch_dispatch: FetchDispatch | None = None,
    analyze_change: Callable = _default_analyze_change,
    extract_sop: Callable | None = None,
    anthropic_client: AsyncAnthropic | None = None,
    only: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Run the daily pipeline. Returns a health summary dict."""
    cfg = Config(repo_root=repo_root, anthropic_api_key="", alert_emails=[])
    sources = load_sources(cfg.sources_yaml)
    if only:
        sources = [s for s in sources if s.slug == only]
        if not sources:
            raise ValueError(f"--only {only!r} did not match any source")

    fetch_dispatch = fetch_dispatch or _default_fetch
    client = anthropic_client

    per_source_status: dict[str, str] = {}
    events_written: list[Path] = []

    for source in sources:
        state = load_state(cfg.state_dir, source.slug)
        try:
            result = await fetch_dispatch(source, state)
            new_events, updated_state = await _process_result(
                source=source,
                state=state,
                result=result,
                now=now,
                cfg=cfg,
                client=client,
                analyze_change=analyze_change,
                dry_run=dry_run,
            )
            events_written.extend(new_events)
            state = updated_state
            state.last_checked_at = now
            state.consecutive_failures = 0
            if not dry_run:
                save_state(cfg.state_dir, source.slug, state)
            per_source_status[source.slug] = "ok"
        except Exception as e:
            log.exception("fetch failed for %s", source.slug)
            state.consecutive_failures += 1
            if not dry_run:
                save_state(cfg.state_dir, source.slug, state)
            per_source_status[source.slug] = f"error: {e}"

    if extract_sop is not None and not dry_run:
        try:
            await extract_sop(sources=sources, repo_root=repo_root, now=now)
        except Exception as e:
            log.exception("state_of_play failed")
            per_source_status["_sop"] = f"error: {e}"

    health = {
        "last_run_at": now.isoformat(),
        "per_source_status": per_source_status,
        "events_written": [str(p.relative_to(repo_root)) for p in events_written],
    }
    if not dry_run:
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        (cfg.data_dir / "health.json").write_text(json.dumps(health, indent=2))
    return health


async def _process_result(
    *,
    source: Source,
    state: SourceState,
    result: FetchResult,
    now: datetime,
    cfg: Config,
    client: AsyncAnthropic | None,
    analyze_change,
    dry_run: bool,
) -> tuple[list[Path], SourceState]:
    new_events: list[Path] = []

    if result.mode == ResultMode.DIFFABLE:
        new_hash = hash_content(result.normalized_content)
        if state.last_hash == new_hash:
            return new_events, state
        # Load previous BEFORE saving the new snapshot, so `prev` is the
        # actual pre-change content, not the file we're about to write.
        prev = load_latest(cfg.snapshots_dir, source.slug)
        if not dry_run:
            save_snapshot(
                cfg.snapshots_dir,
                source.slug,
                now,
                content=result.normalized_content,
                ext=result.raw_ext,
            )
        # Catch-up: first-ever snapshot → no event
        if state.first_seen or prev is None or prev[0] == result.normalized_content:
            state.first_seen = False
            state.last_hash = new_hash
            return new_events, state
        diff = compute_diff(prev[0], result.normalized_content)
        if not diff.has_changes:
            state.last_hash = new_hash
            return new_events, state
        analysis: AnalysisResult = await analyze_change(
            client=client,
            source=source,
            prev_content=prev[0],
            curr_content=result.normalized_content,
            unified_diff=diff.unified_diff,
        )
        if analysis.change_kind == "material" and not dry_run:
            path = write_event(
                events_dir=cfg.events_dir,
                source=source,
                analysis=analysis,
                detected_at=now,
                unified_diff=diff.unified_diff,
            )
            new_events.append(path)
        state.last_hash = new_hash
        return new_events, state

    # PER_ITEM
    # Catch-up on first run: filter items to the last BACKFILL_DAYS (default
    # 30) rather than skipping everything. A brand-new source should
    # contribute some immediately visible history, but not a flood.
    items_to_process = result.items
    if state.first_seen:
        cutoff = now - timedelta(days=BACKFILL_DAYS)
        items_to_process = [
            i for i in result.items if i.published_at and i.published_at >= cutoff
        ]
        # Record guids of items OLDER than the backfill window as "seen" so
        # they don't get reprocessed if the state file is ever rebuilt.
        for i in result.items:
            if i not in items_to_process:
                state.last_seen_guids.append(i.guid)

    for item in items_to_process:
        blob = f"{item.title}\n{item.summary}"
        keyword_pass = keyword_match(blob, source.keyword_filter or [])
        relevance_pass: bool | None = None
        analysis: AnalysisResult | None = None

        if keyword_pass:
            verdict = await haiku_relevance(client, item.title, item.summary)
            relevance_pass = verdict.is_relevant
            if verdict.is_relevant:
                analysis = await analyze_change(
                    client=client,
                    source=source,
                    prev_content="",
                    curr_content=item.body or item.summary,
                    unified_diff="",
                )
                if analysis.change_kind == "material" and not dry_run:
                    path = write_event(
                        events_dir=cfg.events_dir,
                        source=source,
                        analysis=analysis,
                        detected_at=item.published_at or now,
                        unified_diff="",
                        source_url=item.url,
                    )
                    new_events.append(path)

        # Raw log: every item that passed the keyword filter (or made it into
        # the relevance pass) is recorded so long-term analysis has the full
        # corpus. Items that failed the keyword filter are skipped here —
        # they're noise that'd drown a trend query.
        if keyword_pass and not dry_run:
            raw_log.append(
                cfg.raw_dir,
                source.slug,
                guid=item.guid,
                title=item.title,
                summary=item.summary,
                url=item.url,
                published_at=item.published_at,
                keyword_pass=keyword_pass,
                relevance_pass=relevance_pass,
                change_kind=analysis.change_kind if analysis else None,
                importance=analysis.importance if analysis else None,
                recorded_at=now,
            )

        state.last_seen_guids.append(item.guid)

    # Mark first_seen done AFTER processing so the flag still applies above.
    if state.first_seen:
        state.first_seen = False
    state.last_seen_guids = state.last_seen_guids[-500:]
    return new_events, state


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
    client = (
        AsyncAnthropic(api_key=cfg.anthropic_api_key) if cfg.anthropic_api_key else None
    )

    async def _sop(sources, repo_root, now):
        from pipeline import snapshots as snap_mod

        crawler_sources = [s for s in sources if s.pillar == Pillar.CRAWLER]

        def _load(slug: str):
            return snap_mod.load_latest(cfg.snapshots_dir, slug)

        await build_opt_out_matrix(
            client=client,
            crawler_sources=crawler_sources,
            load_latest_snapshot=_load,
            out_path=cfg.data_dir / "opt-out-matrix.json",
            now=now,
        )

    asyncio.run(
        run_check(
            repo_root=cfg.repo_root,
            now=datetime.now(tz=timezone.utc),
            anthropic_client=client,
            extract_sop=_sop if client else None,
            only=args.only,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    _cli()
