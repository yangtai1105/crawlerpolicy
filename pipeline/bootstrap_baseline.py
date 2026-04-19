"""Seed historical snapshots from the Wayback Machine.

For every html_page source in sources.yaml, attempt to fetch an archived
snapshot from ~6 months ago (window: 150–400 days). If found, save it as
content/snapshots/{slug}/{YYYY-MM-DD}.html using the archived date. Also
reset the source's state.last_hash so the next check.py run sees today's
content as a change and emits a proper "6 months ago → today" event.

Idempotent: skip sources that already have a snapshot older than 30 days
(they already have history).

Run:
    uv run python -m pipeline.bootstrap_baseline
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from pipeline.config import Config
from pipeline.snapshots import save_snapshot
from pipeline.sources import SourceType, load_sources
from pipeline.state import load_state, save_state
from pipeline.wayback import fetch_wayback_snapshot

log = logging.getLogger("bootstrap")


async def bootstrap(cfg: Config) -> None:
    sources = load_sources(cfg.sources_yaml)
    html_sources = [s for s in sources if s.type == SourceType.HTML_PAGE]
    log.info("bootstrapping %d html_page sources", len(html_sources))

    for source in html_sources:
        existing = list((cfg.snapshots_dir / source.slug).glob("*.html")) \
            if (cfg.snapshots_dir / source.slug).exists() else []
        has_historic = any(
            (datetime.now(tz=timezone.utc) - _date_from_filename(p.name)).days >= 30
            for p in existing
        )
        if has_historic:
            log.info("%s: already has a snapshot ≥30 days old, skipping", source.slug)
            continue

        try:
            snap = await fetch_wayback_snapshot(
                source.url,
                target_days_ago=180,
                window_start_days=150,
                window_end_days=400,
                content_selector=source.content_selector,
            )
        except Exception as e:
            log.warning("%s: wayback lookup failed: %s", source.slug, e)
            continue
        if snap is None:
            log.info("%s: no wayback snapshot in the 150–400 day window", source.slug)
            continue

        save_snapshot(
            cfg.snapshots_dir,
            source.slug,
            snap.archived_at,
            content=snap.content,
            ext="html",
        )
        # Reset last_hash so the next check.py run detects the current content
        # as a change (vs the now-existing baseline) and emits an event.
        state = load_state(cfg.state_dir, source.slug)
        state.last_hash = None
        state.first_seen = False  # baseline now exists, not "first ever"
        save_state(cfg.state_dir, source.slug, state)

        log.info(
            "%s: seeded baseline from %s (%d days ago) — %s",
            source.slug,
            snap.archived_at.date().isoformat(),
            (datetime.now(tz=timezone.utc) - snap.archived_at).days,
            snap.wayback_url,
        )


def _date_from_filename(name: str) -> datetime:
    return datetime.strptime(name[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)


def _cli() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    cfg = Config.from_env()
    asyncio.run(bootstrap(cfg))


if __name__ == "__main__":
    _cli()
