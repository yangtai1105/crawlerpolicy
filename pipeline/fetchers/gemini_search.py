"""Gemini-with-Google-Search source: run a natural-language query, return
the grounded synthesis as ONE DIFFABLE report.

A gemini_search source has a `query` and `lookback_days`. Each run produces
a synthesized report (text + cited URLs) summarizing recent developments.
We treat this as a living-document page: diff today's synthesis against
yesterday's, emit an event only if the content materially changed.

Why DIFFABLE, not PER_ITEM: Gemini's grounding attaches multiple citations
to one synthesized narrative. Fanning that out to per-citation items
produces dozens of near-duplicate events per run. One digest-per-query is
the right grain — and trend tracking is better served by a daily report
whose diff shows what's NEW this week vs last.
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx
from google import genai
from google.genai import types as gt

from pipeline.fetchers.base import FetchResult, ResultMode
from pipeline.sources import Source

log = logging.getLogger("gemini_search")

_MODEL = "gemini-2.5-flash"
_REDIRECT_TIMEOUT = httpx.Timeout(10.0)


async def fetch_gemini_search(
    source: Source,
    since: Any = None,  # unused — gemini_search is DIFFABLE, not item-stream
    seen_guids: Any = None,
) -> FetchResult:
    """Run source.query with Google Search grounding; return a DIFFABLE report."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set; cannot run gemini_search source")

    client = genai.Client(api_key=api_key)

    lookback_days = source.lookback_days or 14
    prompt = (
        f"{source.query}\n\n"
        f"Focus on developments from the last {lookback_days} days.\n\n"
        "Produce a compact digest of the most important distinct items you find. "
        "For each item, give a specific headline, a 2-3 sentence neutral description, "
        "and cite the authoritative source URL inline. Prefer primary sources "
        "(vendor blogs, regulator pages, standards bodies) over second-hand commentary. "
        "Organize as a numbered list. Skip items you've been asked to cover in other searches. "
        "If nothing new emerged in the window, say so plainly."
    )

    resp = client.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=gt.GenerateContentConfig(
            tools=[gt.Tool(google_search=gt.GoogleSearch())],
            temperature=0.2,
        ),
    )

    report = await _compose_report(resp)
    log.info("gemini_search %s: report length %d chars", source.slug, len(report))
    return FetchResult(mode=ResultMode.DIFFABLE, normalized_content=report, raw_ext="md")


async def _resolve_redirect(client: httpx.AsyncClient, uri: str) -> str:
    """Follow a Gemini grounding-api-redirect URL to the real source. Return
    the original URI if resolution fails (so the citation still works)."""
    try:
        resp = await client.get(uri)
        return str(resp.url) if resp.url else uri
    except Exception:
        return uri


async def _compose_report(resp: Any) -> str:
    """Turn Gemini's response into a markdown digest with REAL source URLs
    (not opaque grounding-redirect URLs), so downstream analysis and inline
    citations have clickable primary sources."""
    candidates = getattr(resp, "candidates", None) or []
    if not candidates:
        return ""
    candidate = candidates[0]
    parts = getattr(candidate.content, "parts", None) or []
    full_text = "".join(getattr(p, "text", "") or "" for p in parts).strip()

    meta = getattr(candidate, "grounding_metadata", None)
    raw_citations: list[tuple[str, str]] = []  # (title, redirect_uri)
    seen_uris: set[str] = set()
    if meta is not None:
        for chunk in getattr(meta, "grounding_chunks", None) or []:
            web = getattr(chunk, "web", None)
            if web is None:
                continue
            uri = getattr(web, "uri", None)
            title = getattr(web, "title", None) or uri or "(untitled)"
            if not uri or uri in seen_uris:
                continue
            seen_uris.add(uri)
            raw_citations.append((title, uri))

    # Follow redirects in parallel so the digest stores real source URLs.
    # This makes citations durable even if Gemini's attribution URLs rotate.
    resolved: list[tuple[str, str]] = []
    if raw_citations:
        async with httpx.AsyncClient(timeout=_REDIRECT_TIMEOUT, follow_redirects=True) as client:
            real_urls = await asyncio.gather(
                *[_resolve_redirect(client, uri) for _, uri in raw_citations],
                return_exceptions=False,
            )
        for (title, _original), real_url in zip(raw_citations, real_urls):
            resolved.append((title, real_url))

    body = full_text + "\n\n## Cited sources\n"
    for i, (title, url) in enumerate(resolved, start=1):
        body += f"{i}. [{title}]({url})\n"
    return body
