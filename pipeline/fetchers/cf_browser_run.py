"""Cloudflare Browser Run crawl endpoint — for pages that Python/httpx
can't fetch directly (CF-challenged sites, sites requiring JS, vendor docs
behind bot protection).

Only attach this fetcher type to sources that actually NEED it — it's
paid-per-page and slower than direct httpx. The default for Python-fetchable
pages remains `html_page`.

Flow:
  1. POST /crawl with {url, limit:1, formats:["markdown"], render:true}
  2. Poll GET /crawl/{job_id} until status == "completed" (or a terminal error)
  3. Read markdown from records[0]

Auth: uses legacy X-Auth-Email + X-Auth-Key headers (the cfk_-prefixed token
variant we were issued works only under this scheme, not Bearer).
"""
from __future__ import annotations

import asyncio
import logging
import os

import httpx

from pipeline.fetchers.base import FetchResult, ResultMode
from pipeline.sources import Source

log = logging.getLogger("cf_browser_run")

_UA = "ai-ecosystem-tracker/0.1 (cf-browser-run)"
_TIMEOUT = httpx.Timeout(60.0)
_POLL_INTERVAL = 5.0
_POLL_MAX_SEC = 420.0  # 7 minutes — render=true with CF-challenged sites takes time


def _headers() -> dict[str, str]:
    email = os.environ.get("CLOUDFLARE_EMAIL")
    key = os.environ.get("CLOUDFLARE_CRAWLER_API_KEY")
    if not email or not key:
        raise RuntimeError(
            "CLOUDFLARE_EMAIL and CLOUDFLARE_CRAWLER_API_KEY must be set "
            "to use cf_browser_run sources"
        )
    return {
        "X-Auth-Email": email,
        "X-Auth-Key": key,
        "Content-Type": "application/json",
        "User-Agent": _UA,
    }


def _base_url() -> str:
    acct = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if not acct:
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID must be set")
    return f"https://api.cloudflare.com/client/v4/accounts/{acct}/browser-rendering/crawl"


async def fetch_cf_browser_run(source: Source) -> FetchResult:
    """Fetch a single URL via Cloudflare Browser Run and return its markdown."""
    url = source.url
    headers = _headers()
    base = _base_url()

    async with httpx.AsyncClient(headers=headers, timeout=_TIMEOUT) as client:
        # 1. Initiate crawl (single page, markdown output)
        init = await client.post(
            base,
            json={
                "url": url,
                "limit": 1,           # only the starting page
                "formats": ["markdown"],
                "render": True,       # CF-challenged sites need JS
                "crawlPurposes": ["ai-input"],
                # depth omitted — CF enforces minimum 1; limit=1 bounds pages anyway
            },
        )
        init.raise_for_status()
        init_data = init.json()
        if not init_data.get("success"):
            raise RuntimeError(f"cf_browser_run init failed: {init_data}")
        job_id = init_data["result"]
        log.info("cf_browser_run %s → job %s", source.slug, job_id)

        # 2. Poll
        elapsed = 0.0
        result_json: dict = {}
        while elapsed < _POLL_MAX_SEC:
            await asyncio.sleep(_POLL_INTERVAL)
            elapsed += _POLL_INTERVAL
            poll = await client.get(f"{base}/{job_id}?limit=1")
            poll.raise_for_status()
            result_json = poll.json()
            status = (result_json.get("result") or {}).get("status", "")
            if status == "completed":
                break
            if status in ("errored", "cancelled_due_to_timeout", "cancelled_due_to_limits", "cancelled_by_user"):
                raise RuntimeError(f"cf_browser_run {source.slug} terminal status: {status}")
        else:
            raise RuntimeError(f"cf_browser_run {source.slug}: timed out after {_POLL_MAX_SEC}s")

        records = (result_json.get("result") or {}).get("records") or []
        if not records:
            raise RuntimeError(f"cf_browser_run {source.slug}: completed with zero records")
        record = records[0]
        markdown = record.get("markdown") or ""
        html = record.get("html") or ""
        metadata = record.get("metadata") or {}

        if not markdown and html:
            # Fallback: extract ourselves if CF returned HTML but no markdown.
            from bs4 import BeautifulSoup
            from readability import Document

            doc = Document(html)
            node = BeautifulSoup(doc.summary(html_partial=True), "lxml")
            for tag in node.find_all(["script", "style", "noscript"]):
                tag.decompose()
            text = node.get_text(separator="\n", strip=True)
            markdown = "\n".join(line.strip() for line in text.splitlines() if line.strip())

        if not markdown.strip():
            raise RuntimeError(
                f"cf_browser_run {source.slug}: empty content (status={metadata.get('status')})"
            )

    return FetchResult(mode=ResultMode.DIFFABLE, normalized_content=markdown, raw_ext="md")
