"""GitHub releases + merged PRs fetcher."""
from __future__ import annotations

import os
from datetime import datetime
from fnmatch import fnmatchcase

import httpx

from pipeline.fetchers.base import CandidateItem, FetchResult, ResultMode
from pipeline.sources import Source

_UA = "ai-ecosystem-tracker/0.1"
_TIMEOUT = httpx.Timeout(30.0)


async def fetch_github_repo(
    source: Source,
    since: datetime | None,
    seen_guids: list[str],
) -> FetchResult:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"User-Agent": _UA, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    seen = set(seen_guids)
    items: list[CandidateItem] = []
    async with httpx.AsyncClient(
        headers=headers, timeout=_TIMEOUT, follow_redirects=True
    ) as client:
        # Treat rate-limited endpoints as "no items this run" rather than a
        # hard failure — unauthenticated GitHub API allows 60 req/hour, and
        # the daily cron shouldn't drop the whole source on a transient 403.
        try:
            releases = await _fetch_releases(client, source, since, seen)
            items.extend(releases)
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 403:
                raise
        try:
            prs = await _fetch_merged_prs(client, source, since, seen)
            items.extend(prs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 403:
                raise
    return FetchResult(mode=ResultMode.PER_ITEM, items=items)


async def _fetch_releases(
    client: httpx.AsyncClient, source: Source, since: datetime | None, seen: set[str]
) -> list[CandidateItem]:
    resp = await client.get(
        f"https://api.github.com/repos/{source.repo}/releases",
        params={"per_page": 20},
    )
    resp.raise_for_status()
    items: list[CandidateItem] = []
    for r in resp.json():
        guid = f"release:{r['id']}"
        if guid in seen:
            continue
        published = datetime.fromisoformat(r["published_at"].replace("Z", "+00:00"))
        if since and published < since:
            continue
        items.append(
            CandidateItem(
                guid=guid,
                title=f"Release {r.get('name') or r['tag_name']}",
                published_at=published,
                url=r.get("html_url"),
                summary=r.get("body") or "",
                body=r.get("body") or "",
            )
        )
    return items


async def _fetch_merged_prs(
    client: httpx.AsyncClient, source: Source, since: datetime | None, seen: set[str]
) -> list[CandidateItem]:
    resp = await client.get(
        f"https://api.github.com/repos/{source.repo}/pulls",
        params={
            "state": "closed",
            "sort": "updated",
            "direction": "desc",
            "per_page": 30,
        },
    )
    resp.raise_for_status()
    items: list[CandidateItem] = []
    for pr in resp.json():
        if not pr.get("merged_at"):
            continue
        guid = f"pr:{pr['number']}"
        if guid in seen:
            continue
        merged = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
        if since and merged < since:
            continue
        labels = {label["name"] for label in pr.get("labels", [])}
        if not await _pr_passes_filters(client, source, pr["number"], labels):
            continue
        items.append(
            CandidateItem(
                guid=guid,
                title=f"PR #{pr['number']}: {pr['title']}",
                published_at=merged,
                url=pr.get("html_url"),
                summary=pr.get("title") or "",
                body=pr.get("body") or "",
            )
        )
    return items


async def _pr_passes_filters(
    client: httpx.AsyncClient, source: Source, number: int, labels: set[str]
) -> bool:
    """Keep a PR that carries a required label or touches a watched path.

    Protocol repos merge far more SDK and tooling PRs than spec changes, so
    `pr_path_globs` (fnmatch against changed file paths) narrows them to the
    specification. With neither filter set, every merged PR is kept.
    """
    if not source.pr_labels and not source.pr_path_globs:
        return True
    if set(source.pr_labels) & labels:
        return True
    if not source.pr_path_globs:
        return False
    resp = await client.get(
        f"https://api.github.com/repos/{source.repo}/pulls/{number}/files",
        params={"per_page": 100},
    )
    resp.raise_for_status()
    return any(
        fnmatchcase(changed["filename"], pattern)
        for changed in resp.json()
        for pattern in source.pr_path_globs
    )
