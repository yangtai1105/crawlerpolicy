"""GitHub releases + merged PRs fetcher."""
from __future__ import annotations

import os
from datetime import datetime

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
    required_labels = set(source.pr_labels)
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
        if required_labels and not (required_labels & labels):
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
