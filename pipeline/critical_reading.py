"""Weekly Dispatch — the week's sharpest reporting, investigations, and
perspectives on AI crawlers, agents, copyright/legal, and web-ecosystem
impact. Distinct from the daily Feed (primary-source announcements) in that
Dispatch surfaces outside voices: investigative journalism, op-eds, policy
critique, first-hand field reports, academic commentary.

Architecture: one Gemini grounded-search call PER TOPIC GROUP (4 calls/run,
in parallel), each returning a 1-2 sentence TLDR for that topic's week plus
5-8 items. Splitting per-topic keeps each prompt focused, avoids
max-token truncation, and lets us recover gracefully if a single topic's
call returns nothing.

Cost: 4 x $0.01 = $0.04/week -> $0.16/month.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import httpx
from google import genai
from google.genai import types as gt

log = logging.getLogger("dispatch")

_MODEL = "gemini-2.5-flash"
_REDIRECT_TIMEOUT = httpx.Timeout(10.0)

TOPIC_GROUPS: list[str] = [
    "Crawling & Publisher Controls",
    "Agents",
    "Copyright & Legal",
    "Web Ecosystem & AI Impact",
]

_TOPIC_HINTS: dict[str, str] = {
    "Crawling & Publisher Controls": (
        "AI crawlers (GPTBot / ClaudeBot / PerplexityBot / Bytespider / etc), "
        "robots.txt, publisher-side blocking tooling (Cloudflare AI Crawl Control, "
        "DataDome, TollBit), server-log analyses showing crawler behavior, "
        "new opt-out mechanisms, scraped-content lawsuits about access"
    ),
    "Agents": (
        "AI agent infrastructure, agent-to-agent protocols (MCP, A2A), agent "
        "authentication (Web Bot Auth, agent identity standards), agent-failure "
        "investigations, agent-security incidents, critiques of agentic "
        "commerce, enterprise deployment experience reports"
    ),
    "Copyright & Legal": (
        "AI training-data copyright lawsuits (publisher / author / rights-holder "
        "vs AI company), regulatory action (UK CMA, EU AI Office, Italian Garante, "
        "US Copyright Office, US courts), amicus briefs, licensing disputes, "
        "government policy changes on AI + copyright"
    ),
    "Web Ecosystem & AI Impact": (
        "AI Overviews / AI search impact on publisher traffic & revenue, "
        "first-party data monetization strategies, indigenous-content and minority-"
        "language protection, pay-per-crawl negotiations, content-licensing deals, "
        "AI's effect on small publishers / niche media"
    ),
}


def _prompt_for(topic: str, hint: str) -> str:
    return f"""Find the week's 6–10 most important pieces of REPORTING, ANALYSIS, or
PERSPECTIVE on:
{topic} — {hint}

Published in the last 7 days (stretch to 14 if this week was quiet).

Include any of these:
- Substantive news reporting from reputable outlets (Reuters, NYT, Bloomberg,
  WSJ, Politico, FT, The Guardian, Ars Technica, TechCrunch, Information,
  Platformer, Semafor, Axios, trade-press outlets, etc.)
- Investigative journalism, exclusives, and deep-dive features
- Op-eds / commentary with a distinct argument
- First-hand field reports (server-log analyses, case studies, postmortems)
- Filed legal documents, regulator briefs, policy critiques
- Academic / specialist-researcher analyses
- Serious think-piece / essay commentary on the ecosystem

EXCLUDE (these are noise):
- Generic explainer / 101 posts ("X Impact on Y Explained", "What is Z?")
- SEO listicles ("Top 10 Tools for…", "N Things You Should Know…")
- Vendor product launches / press releases (those live in our daily feed)
- Tutorial / how-to content
- Aggregator posts that just summarize someone else's report without adding anything
- PDF lawyer-marketing pieces and other thinly-veiled sales content

News reporting IS welcome here — the point is WHO is reporting it and
whether the piece adds anything: context, argument, or primary-source detail.
A solid Reuters story on an AI lawsuit counts. A random law-firm blog
summarizing the same lawsuit does not.

Return ONLY this JSON (no prose, no code fences):

{{"tldr":"1–2 sentence synthesis of the week's thread on this topic","items":[{{"tag":"#CamelCase","title":"exact published headline","frame":"what the author argues or reports, ≤25 words","quote":"verbatim pull-quote, ≤30 words","kind":"investigation|commentary|field-report|legal|research"}}]}}

Hard rules:
- title MUST be the exact published headline. We use it to look up the
  source URL from your grounded citations — precision matters more than style.
  Don't rewrite, shorten, or paraphrase headlines.
- Only include items you actually surfaced via search in THIS response.
  Don't list items from memory or prior knowledge. We'll discard anything
  that isn't backed by a grounded citation, so there's no point padding.
- tag: a specific CamelCase hashtag capturing this item's angle. Avoid
  generic #AI / #Tech. Examples: #SearchImpact, #OptOut, #PayPerCrawl,
  #BotVerification, #AIRegulation, #DataLicensing, #AgentSecurity.
- quote must appear verbatim in the source.
- Don't pad. If the week had only 3 items, return 3. If nothing qualified,
  return items: [] and an honest tldr like "A quiet week; most activity
  flowed through the daily feed."
"""


async def build_weekly_dispatch(
    *,
    out_dir: Path,
    now: datetime,
) -> Path:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    client = genai.Client(api_key=api_key)

    # Run one Gemini call per topic in parallel. Each retries up to 3 times
    # if it returns empty (grounded-search responses are occasionally empty
    # or truncated).
    topic_results = await asyncio.gather(
        *[_run_topic(client, t) for t in TOPIC_GROUPS],
        return_exceptions=True,
    )

    topics_payload: list[dict] = []
    for t, res in zip(TOPIC_GROUPS, topic_results):
        if isinstance(res, Exception):
            log.exception("dispatch: topic %s errored", t)
            topics_payload.append({"topic": t, "tldr": f"(error generating: {res})", "items": []})
            continue
        tldr, items = res
        log.info("dispatch: %s — %d items", t, len(items))
        topics_payload.append({"topic": t, "tldr": tldr, "items": items})

    iso_year, iso_week, _ = now.isocalendar()
    filename = f"{iso_year}-W{iso_week:02d}.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    payload = {
        "generated_at": now.isoformat(),
        "iso_year": iso_year,
        "iso_week": iso_week,
        "topics": topics_payload,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    total = sum(len(t["items"]) for t in topics_payload)
    log.info("dispatch: wrote %s (%d items across %d topics)", out_path, total, len(topics_payload))
    return out_path


async def _run_topic(client, topic: str) -> tuple[str, list[dict]]:
    """Run one Gemini call for a single topic, retrying up to 5 times on empty."""
    hint = _TOPIC_HINTS[topic]
    prompt = _prompt_for(topic, hint)
    items: list[dict] = []
    tldr: str = ""
    for attempt in range(5):
        resp = client.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config=gt.GenerateContentConfig(
                tools=[gt.Tool(google_search=gt.GoogleSearch())],
                temperature=0.3 + attempt * 0.1,
                max_output_tokens=32768,
            ),
        )
        text = _extract_text(resp)
        parsed = _parse_json(text)
        items_raw = parsed.get("items", [])
        tldr = (parsed.get("tldr") or "").strip()

        for it in items_raw:
            it["topic"] = topic

        # Gemini's JSON only carries editorial fields (title/frame/quote/tag/
        # kind). The *URL* and source_domain come from grounding_metadata —
        # the model is instructed not to emit URLs itself, since it frequently
        # hallucinates them. Match each item to a grounded citation by
        # title-token overlap.
        citations = _collect_grounding_citations(resp)
        resolved = await _resolve_citations(citations)
        items = _map_items_to_grounded_citations(items_raw, resolved)

        if items or tldr:
            if items_raw and not items:
                log.warning(
                    "dispatch[%s]: attempt %d — %d raw items, 0 matched grounded citations; retrying",
                    topic,
                    attempt + 1,
                    len(items_raw),
                )
                continue
            return tldr, items
        finish = _extract_finish_reason(resp)
        log.warning(
            "dispatch[%s]: attempt %d empty (response %d chars, finish=%s); retrying",
            topic,
            attempt + 1,
            len(text),
            finish,
        )
    return tldr or "(no items surfaced this week)", items


def _collect_grounding_citations(resp) -> list[tuple[str, str]]:
    """Return (title, redirect_uri) pairs from Gemini's grounding_metadata.
    These are the real sources Google Search grounded against — unlike the
    URLs the model emits into its JSON body, which are frequently fabricated."""
    candidates = getattr(resp, "candidates", None) or []
    if not candidates:
        return []
    meta = getattr(candidates[0], "grounding_metadata", None)
    if meta is None:
        return []
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for chunk in getattr(meta, "grounding_chunks", None) or []:
        web = getattr(chunk, "web", None)
        if web is None:
            continue
        uri = getattr(web, "uri", None) or ""
        if not uri or uri in seen:
            continue
        seen.add(uri)
        title = getattr(web, "title", None) or uri
        out.append((title, uri))
    return out


async def _resolve_redirect(client: httpx.AsyncClient, uri: str) -> str:
    """Follow a Gemini grounding-api-redirect URL to the real publisher URL."""
    try:
        resp = await client.get(uri)
        return str(resp.url) if resp.url else uri
    except Exception:
        return uri


async def _resolve_citations(citations: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Follow redirect URIs in parallel so downstream gets real publisher URLs
    (the redirect URIs expire fast and 404 for non-Gemini clients)."""
    if not citations:
        return []
    async with httpx.AsyncClient(timeout=_REDIRECT_TIMEOUT, follow_redirects=True) as client:
        real_urls = await asyncio.gather(
            *[_resolve_redirect(client, uri) for _, uri in citations],
            return_exceptions=False,
        )
    return [(title, url) for (title, _), url in zip(citations, real_urls)]


def _normalize_domain(d: str) -> str:
    d = (d or "").strip().lower()
    return d[4:] if d.startswith("www.") else d


def _url_domain(url: str) -> str:
    try:
        return _normalize_domain(urlparse(url).netloc)
    except Exception:
        return ""


_TOKEN_RX = re.compile(r"[a-z0-9]+")
# Common title noise that shouldn't count toward overlap. Keep small —
# real stopwords are handled by the len-3 floor.
_TITLE_STOPWORDS = frozenset({"with", "from", "that", "this", "your", "will",
                              "what", "when", "were", "them", "they", "their",
                              "have", "been", "into", "about", "against",
                              "news", "report", "says", "just", "more"})


def _title_tokens(s: str) -> set[str]:
    return {t for t in _TOKEN_RX.findall((s or "").lower())
            if len(t) > 3 and t not in _TITLE_STOPWORDS}


def _title_overlap(a: str, b: str) -> int:
    return len(_title_tokens(a) & _title_tokens(b))


def _map_items_to_grounded_citations(
    items: list[dict],
    grounded: list[tuple[str, str]],
    *,
    min_overlap: int = 3,
) -> list[dict]:
    """Match each item to the grounded citation whose title shares the most
    meaningful tokens with the item's title. Populate ``url`` and
    ``source_domain`` from the matched citation. Drop items whose best match
    has fewer than ``min_overlap`` shared tokens — fewer shared tokens means
    we're likely attaching the wrong article."""
    if not grounded:
        return []
    kept: list[dict] = []
    for it in items:
        item_title = it.get("title") or ""
        if not item_title:
            continue
        item_tokens = _title_tokens(item_title)
        if not item_tokens:
            continue
        best_score = 0
        best: tuple[str, str] | None = None
        for g_title, g_url in grounded:
            score = len(item_tokens & _title_tokens(g_title))
            if score > best_score:
                best_score = score
                best = (g_title, g_url)
        if best is None or best_score < min_overlap:
            continue
        _, url = best
        kept.append({**it, "url": url, "source_domain": _url_domain(url)})
    return kept


def _extract_text(resp) -> str:
    candidates = getattr(resp, "candidates", None) or []
    if not candidates:
        return ""
    parts = getattr(candidates[0].content, "parts", None) or []
    return "".join(getattr(p, "text", "") or "" for p in parts).strip()


def _extract_finish_reason(resp) -> str:
    candidates = getattr(resp, "candidates", None) or []
    if not candidates:
        return "?"
    return str(getattr(candidates[0], "finish_reason", "?"))


_CODE_FENCE_RX = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL)


def _parse_json(text: str) -> dict:
    body = text.strip()
    m = _CODE_FENCE_RX.match(body)
    if m:
        body = m.group(1).strip()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        pass
    start = body.find("{")
    if start < 0:
        return {}
    depth = 0
    for i, ch in enumerate(body[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(body[start : i + 1])
                except json.JSONDecodeError:
                    break
    return {}


def _cli() -> None:
    import argparse
    from datetime import timezone

    from pipeline.config import Config

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()

    cfg = Config.from_env()
    # Migrate display name but keep file path backwards-compatible for now.
    out_dir = args.out_dir or (cfg.data_dir / "critical-reading")
    asyncio.run(build_weekly_dispatch(out_dir=out_dir, now=datetime.now(tz=timezone.utc)))


# Backwards-compat alias for any callers still using the old name.
build_critical_reading = build_weekly_dispatch


if __name__ == "__main__":
    _cli()
