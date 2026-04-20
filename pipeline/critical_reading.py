"""Weekly Dispatch — the week's sharpest reporting, investigations, and
perspectives on AI crawlers, agents, copyright/legal, and web-ecosystem
impact. Distinct from the daily Feed (primary-source announcements) in that
Dispatch surfaces outside voices: investigative journalism, op-eds, policy
critique, first-hand field reports, academic commentary.

Architecture: one Claude + web_search call PER TOPIC GROUP (4 calls/run,
in parallel), each returning a 1-2 sentence TLDR for that topic's week plus
5-8 items. Splitting per-topic keeps each prompt focused, avoids
max-token truncation, and lets us recover gracefully if a single topic's
call returns nothing.

Why Anthropic web_search instead of Gemini grounded search: Gemini's
grounding ranked SEO-optimized law-firm blogs and startup explainers over
real journalism because those rank well in Google Search for these topics.
Sonnet's instruction-following on the EXCLUDE list (skip explainers, skip
law-firm SEO, skip content farms) is substantially better.

Cost: ~4 x $0.05 (Sonnet tokens + web_search uses) = ~$0.20/week = ~$0.80/mo.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from anthropic import AsyncAnthropic

log = logging.getLogger("dispatch")

_MODEL = "claude-sonnet-4-6"
# Cap web_search invocations per topic — roughly how many distinct queries
# Claude can issue during one topic's reasoning. 8 is plenty for a news roundup
# while keeping cost bounded (web_search is $10/1k uses).
_WEB_SEARCH_MAX_USES = 8

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


def _prompt_for(topic: str, hint: str, today: str) -> str:
    return f"""Today is {today}. Find THIS WEEK's most important pieces of
REPORTING, ANALYSIS, or PERSPECTIVE on:
{topic} — {hint}

Hard recency requirement: each item MUST be published in the last 7 days
(stretch to 14 if this week was genuinely quiet). Nothing older. Verify
the publication date via your search — if you can't confirm a piece is
from the last 14 days, skip it.

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

HARD EXCLUDE (do not return these, even if they rank well in search):
- Generic explainer / 101 posts ("X Impact on Y Explained", "What is Z?",
  "Who Owns…", "Understanding X", "A Guide to…", "Introduction to…")
- SEO listicles ("Top 10 Tools for…", "N Things You Should Know…")
- Vendor product launches / press releases (those live in our daily feed)
- Tutorial / how-to content
- Aggregator posts that just summarize someone else's report without adding anything
- Law-firm blog posts / client-alert SEO content (Mondaq, JD Supra,
  Lexology, individual firm blogs like "X Firm's guide to Y")
- Personal-blog explainers with no independent reporting or argument
- Anything from {{2022, 2023, 2024, 2025}} — we want THIS week only

News reporting IS welcome — the point is WHO is reporting it and whether
the piece adds anything: context, argument, or primary-source detail.
A solid Reuters story on an AI lawsuit counts. A law-firm blog summarizing
the same lawsuit does not.

Return ONLY this JSON (no prose, no code fences):

{{"tldr":"1–2 sentence synthesis of THIS week's thread on this topic","items":[{{"tag":"#CamelCase","title":"exact published headline","published":"YYYY-MM-DD","frame":"what the author argues or reports, ≤25 words","quote":"verbatim pull-quote, ≤30 words","kind":"investigation|commentary|field-report|legal|research"}}]}}

Hard rules:
- title MUST be the exact published headline as it appears at the source.
  Don't rewrite, shorten, or paraphrase — we look up the URL from the
  headline, so precision matters more than style.
- published MUST be the actual publication date in YYYY-MM-DD. If you're
  not sure, skip the item — don't guess.
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
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    client = AsyncAnthropic(api_key=api_key)

    today = now.date().isoformat()
    topic_results = await asyncio.gather(
        *[_run_topic(client, t, now=now, today=today) for t in TOPIC_GROUPS],
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


async def _run_topic(
    client: AsyncAnthropic,
    topic: str,
    *,
    now: datetime,
    today: str,
) -> tuple[str, list[dict]]:
    """Run one Claude + web_search call for a single topic."""
    hint = _TOPIC_HINTS[topic]
    prompt = _prompt_for(topic, hint, today)

    resp = await client.messages.create(
        model=_MODEL,
        max_tokens=16000,
        tools=[{
            "type": "web_search_20260209",
            "name": "web_search",
            "max_uses": _WEB_SEARCH_MAX_USES,
        }],
        messages=[{"role": "user", "content": prompt}],
    )

    text = _extract_text_blocks(resp)
    parsed = _parse_json(text)
    items_raw = parsed.get("items", [])
    tldr = (parsed.get("tldr") or "").strip()

    for it in items_raw:
        it["topic"] = topic

    # URLs and source_domain come from Anthropic's web_search_tool_result
    # blocks — real publisher URLs Claude actually searched and cited, not
    # anything the model wrote into the JSON body. Match each item to a
    # grounded citation by title-token overlap.
    citations = _collect_grounding_citations(resp)
    matched = _map_items_to_grounded_citations(items_raw, citations)
    items = _filter_quality(matched, now=now)

    if items_raw and not items:
        sample_items = "; ".join((it.get("title") or "?")[:80] for it in items_raw[:3])
        sample_cits = "; ".join(
            f"{(t or '(no title)')[:50]} -> {u[:80]}" for t, u in citations[:3]
        )
        log.warning(
            "dispatch[%s]: %d raw items, %d grounded, 0 matched-and-kept",
            topic, len(items_raw), len(citations),
        )
        log.warning("dispatch[%s]: sample items: %s", topic, sample_items)
        log.warning("dispatch[%s]: sample citations: %s", topic, sample_cits)

    if not items_raw and not tldr:
        log.warning("dispatch[%s]: no items or tldr returned", topic)

    return tldr or "(no items surfaced this week)", items


def _collect_grounding_citations(resp) -> list[tuple[str, str]]:
    """Return (title, url) pairs from the ``web_search_tool_result`` content
    blocks in the Messages response. These are the real publisher URLs
    Anthropic's web_search actually searched — not anything the model wrote
    into its own text output, which could be fabricated."""
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for block in getattr(resp, "content", None) or []:
        if getattr(block, "type", None) != "web_search_tool_result":
            continue
        results = getattr(block, "content", None) or []
        for result in results:
            if getattr(result, "type", None) != "web_search_result":
                continue
            url = getattr(result, "url", None) or ""
            if not url or url in seen:
                continue
            seen.add(url)
            title = getattr(result, "title", None) or url
            out.append((title, url))
    return out

# Domains consistently surfacing as law-firm / SEO-farm content. These are
# NOT reporting or commentary in the sense we want, and they rank well in
# Google Search so they flood grounded results. Drop wholesale.
_BLOCKED_DOMAINS = frozenset({
    "mondaq.com",
    "jdsupra.com",
    "lexology.com",
    "natlawreview.com",
})

# URL slug patterns that reliably indicate explainer / how-to / listicle
# content, which the prompt already says to EXCLUDE but Gemini sometimes
# still surfaces because these posts are SEO-optimized.
_EXPLAINER_PATTERNS = (
    "-explained",
    "/explained-",
    "what-is-",
    "/what-is/",
    "how-to-",
    "/how-to/",
    "-guide-to-",
    "-a-guide-",
    "/guide-to-",
    "introduction-to-",
    "understanding-",
    "-for-dummies",
    "-101-",
    "/101/",
    "who-owns-",
)

# Year-in-URL-path pattern catches articles filed under an old year even
# when Gemini claims they're recent.
_OLD_YEAR_IN_PATH_RX = re.compile(r"[-/_](20\d\d)[-/_]")


def _filter_quality(items: list[dict], *, now: datetime, max_age_days: int = 60) -> list[dict]:
    """Post-filter matched items for quality and recency.

    Drops (with a log line for each drop so the run is debuggable):
    - Items on the blocked-domain list (law-firm content farms)
    - Items whose URL path matches an obvious-explainer slug pattern
    - Items whose URL path contains a year older than the current year
    - Items whose ``published`` field parses to older than ``max_age_days``
      (60-day cutoff is generous on purpose — Gemini's self-reported dates
      are unreliable, but clearly-old content is still clearly old)
    """
    kept: list[dict] = []
    cutoff_year = now.year
    cutoff = now.date() - timedelta(days=max_age_days)
    for it in items:
        url = it.get("url", "")
        domain = (it.get("source_domain") or _url_domain(url) or "").lower()
        path_lower = ""
        try:
            path_lower = urlparse(url).path.lower()
        except Exception:
            pass

        if any(domain == b or domain.endswith("." + b) for b in _BLOCKED_DOMAINS):
            log.info("dispatch: drop %s (blocked domain)", url)
            continue

        hit = next((pat for pat in _EXPLAINER_PATTERNS if pat in path_lower), None)
        if hit:
            log.info("dispatch: drop %s (explainer pattern %r)", url, hit)
            continue

        m = _OLD_YEAR_IN_PATH_RX.search(path_lower)
        if m and int(m.group(1)) < cutoff_year:
            log.info("dispatch: drop %s (URL year %s)", url, m.group(1))
            continue

        pub = _parse_published(it.get("published"))
        if pub is not None and pub < cutoff:
            log.info("dispatch: drop %s (published %s, older than %dd)", url, pub, max_age_days)
            continue

        kept.append(it)
    return kept


def _parse_published(raw) -> "date | None":
    if not raw or not isinstance(raw, str):
        return None
    try:
        return datetime.strptime(raw[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


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
                              "news", "report", "says", "just", "more", "html",
                              "http", "https", "www"})


def _title_tokens(s: str) -> set[str]:
    return {t for t in _TOKEN_RX.findall((s or "").lower())
            if len(t) > 3 and t not in _TITLE_STOPWORDS}


def _title_overlap(a: str, b: str) -> int:
    return len(_title_tokens(a) & _title_tokens(b))


def _citation_tokens(title: str, url: str) -> set[str]:
    """Token pool for a grounded citation: meaningful tokens from both the
    citation title AND the URL path. Grounded titles from the Gemini SDK
    are sometimes empty or the raw URI; the URL slug usually contains the
    headline and gives us something to match against."""
    tokens = _title_tokens(title)
    try:
        path = urlparse(url).path
    except Exception:
        path = ""
    for t in _TOKEN_RX.findall(path.lower()):
        if len(t) > 3 and t not in _TITLE_STOPWORDS:
            tokens.add(t)
    return tokens


def _map_items_to_grounded_citations(
    items: list[dict],
    grounded: list[tuple[str, str]],
    *,
    min_overlap: int = 2,
) -> list[dict]:
    """Match each item to the grounded citation whose title + URL-slug shares
    the most meaningful tokens with the item's title. Populate ``url`` and
    ``source_domain`` from the matched citation. Drop items whose best match
    has fewer than ``min_overlap`` shared tokens — fewer shared tokens means
    we're likely attaching the wrong article."""
    if not grounded:
        return []
    pool = [(title, url, _citation_tokens(title, url)) for title, url in grounded]
    kept: list[dict] = []
    for it in items:
        item_title = it.get("title") or ""
        if not item_title:
            continue
        item_tokens = _title_tokens(item_title)
        if not item_tokens:
            continue
        best_score = 0
        best_url: str | None = None
        for _g_title, g_url, g_tokens in pool:
            score = len(item_tokens & g_tokens)
            if score > best_score:
                best_score = score
                best_url = g_url
        if best_url is None or best_score < min_overlap:
            continue
        kept.append({**it, "url": best_url, "source_domain": _url_domain(best_url)})
    return kept


def _extract_text_blocks(resp) -> str:
    """Concatenate all ``text`` content blocks from an Anthropic Messages
    response. Other block types (server_tool_use, web_search_tool_result,
    thinking) are skipped — the JSON output lives in text blocks."""
    out: list[str] = []
    for block in getattr(resp, "content", None) or []:
        if getattr(block, "type", None) == "text":
            text = getattr(block, "text", None) or ""
            if text:
                out.append(text)
    return "\n".join(out).strip()


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
