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

import logging
import os
from typing import Any

from google import genai
from google.genai import types as gt

from pipeline.fetchers.base import FetchResult, ResultMode
from pipeline.sources import Source

log = logging.getLogger("gemini_search")

_MODEL = "gemini-2.5-flash"


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

    report = _compose_report(resp)
    log.info("gemini_search %s: report length %d chars", source.slug, len(report))
    return FetchResult(mode=ResultMode.DIFFABLE, normalized_content=report, raw_ext="md")


def _compose_report(resp: Any) -> str:
    """Turn Gemini's response into a stable markdown digest for diffing.

    Includes the synthesized text + a dedup'd list of cited URLs. Redirects
    are kept as-is (they're stable per Gemini's attribution system, so
    diffing won't churn unless the cited sources actually change).
    """
    candidates = getattr(resp, "candidates", None) or []
    if not candidates:
        return ""
    candidate = candidates[0]
    parts = getattr(candidate.content, "parts", None) or []
    full_text = "".join(getattr(p, "text", "") or "" for p in parts).strip()

    meta = getattr(candidate, "grounding_metadata", None)
    citations: list[tuple[str, str]] = []
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
            citations.append((title, uri))

    body = full_text + "\n\n## Cited sources\n"
    for i, (title, uri) in enumerate(citations, start=1):
        body += f"{i}. [{title}]({uri})\n"
    return body
