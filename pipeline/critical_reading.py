"""Weekly 'Critical Reading' module — a curated list of critical commentary,
analysis, and investigative pieces across our four topic groups.

Distinct from the daily news feed: these are opinions / deep analyses /
investigative journalism, not vendor announcements. The shape matches the
example workflow: source + 1-sentence frame + pull-quote + hashtag, grouped
by topic.

Runs once per ISO week (Monday morning via GitHub Actions). One Gemini call
with Google Search grounding, structured-JSON response parsed out of the
response text. Cost: ~\$0.005/run → ~\$0.02/month.
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

log = logging.getLogger("critical_reading")

_MODEL = "gemini-2.5-flash"

TOPIC_GROUPS: list[str] = [
    "Crawling & Publisher Controls",
    "Agents",
    "Copyright & Legal",
    "Web Ecosystem & AI Impact",
]

_PROMPT_TEMPLATE = """Find 2-3 CRITICAL commentary / analysis / investigative pieces per topic
below, published in the last 7 days (stretch to 14 if quiet):

{topics}

Criteria: independent analyst, specialist blogger, regulator, investigator,
or academic — NOT vendor announcements / product launches. Distinct argument,
not news summary.

Return ONLY this JSON, no prose, no code fences:

{{"items":[{{"topic":"...","tag":"#CamelCase","source_domain":"example.com","url":"...","title":"...","frame":"what the author argues, ≤25 words","quote":"verbatim pull-quote, ≤30 words"}}]}}

Hard requirements:
- url: THE ACTUAL PUBLISHER'S URL (e.g. https://mariehaynes.com/agentic-web).
  Never a Google / vertexaisearch grounding redirect URL. Never a search
  result page. If you cannot cite a real publisher URL, skip the item.
- source_domain: the bare hostname of that URL without "www." or protocol
  (e.g. "mariehaynes.com"). Must match the url.
- tag: specific hashtag (#SearchImpact, #OptOut, #PayPerCrawl, #AIRegulation,
  #DataLicensing, #BotVerification, #Copyright, etc.). Don't use generic #AI.
- quote: must appear verbatim in the source. Don't fabricate.
- Skip a topic group if nothing genuinely critical emerged — do NOT pad with
  placeholders or vendor content.
"""


async def build_critical_reading(
    *,
    out_dir: Path,
    now: datetime,
) -> Path:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)

    topics_bullet = "\n".join(f"  - {t}" for t in TOPIC_GROUPS)
    prompt = _PROMPT_TEMPLATE.format(topics=topics_bullet)

    log.info("critical_reading: querying Gemini…")
    # Gemini grounded responses are occasionally truncated or empty; retry
    # up to 3 times with slightly varied temperature if we get no items.
    items: list[dict] = []
    for attempt in range(3):
        resp = client.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config=gt.GenerateContentConfig(
                tools=[gt.Tool(google_search=gt.GoogleSearch())],
                temperature=0.3 + attempt * 0.1,
                # Gemini grounded-search responses include reasoning tokens
                # in the budget. 32k leaves room for all of that + the JSON.
                max_output_tokens=32768,
            ),
        )
        text = _extract_text(resp)
        parsed = _parse_json_items(text)
        items = parsed.get("items", [])
        if items:
            log.info("critical_reading: attempt %d returned %d items", attempt + 1, len(items))
            break
        finish = _extract_finish_reason(resp)
        log.warning(
            "critical_reading: attempt %d returned 0 items (response %d chars, finish=%s); retrying",
            attempt + 1,
            len(text),
            finish,
        )

    # Drop Gemini-injected placeholder items (no real source/url) + items
    # that still cite Google's grounding-redirect URL (which expires quickly
    # and can't be resolved post-hoc). We'd rather ship a short week than
    # a row pointing to a dead link.
    def _is_valid(it: dict) -> bool:
        sd = (it.get("source_domain") or "").strip().lower()
        url = (it.get("url") or "").strip().lower()
        if not url or sd in {"", "n/a", "none"}:
            return False
        if _GEMINI_REDIRECT_HOST in url or _GEMINI_REDIRECT_HOST in sd:
            return False
        return True
    before = len(items)
    items = [it for it in items if _is_valid(it)]
    dropped = before - len(items)
    if dropped:
        log.warning("critical_reading: dropped %d items with redirect/placeholder URLs", dropped)

    if not items:
        log.warning("critical_reading: zero items; raw response preview follows")
        log.warning("----- RAW GEMINI RESPONSE (first 2000 chars) -----")
        for line in text[:2000].splitlines():
            log.warning("  %s", line)
        log.warning("--------------------------------------------------")
    log.info("critical_reading: Gemini returned %d items", len(items))

    iso_year, iso_week, _ = now.isocalendar()
    filename = f"{iso_year}-W{iso_week:02d}.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename

    payload = {
        "generated_at": now.isoformat(),
        "iso_year": iso_year,
        "iso_week": iso_week,
        "topic_groups": TOPIC_GROUPS,
        "items": items,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    log.info("critical_reading: wrote %s (%d items)", out_path, len(items))
    return out_path


_GEMINI_REDIRECT_HOST = "vertexaisearch.cloud.google.com"


async def _resolve_urls(items: list[dict]) -> list[dict]:
    """For any item whose URL points to a Gemini grounding redirect, follow
    the redirect to the real source and repair source_domain. Leave
    non-redirect URLs untouched so we don't accidentally hit sites that
    rate-limit head requests."""
    needs_resolve = [
        (i, it["url"])
        for i, it in enumerate(items)
        if it.get("url") and _GEMINI_REDIRECT_HOST in it["url"]
    ]
    if not needs_resolve:
        return items

    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0), follow_redirects=True) as client:
        resolved = await asyncio.gather(
            *[_follow(client, url) for _, url in needs_resolve],
            return_exceptions=False,
        )
    for (idx, _original), real_url in zip(needs_resolve, resolved):
        if not real_url:
            continue
        items[idx]["url"] = real_url
        parsed = urlparse(real_url)
        if parsed.hostname:
            items[idx]["source_domain"] = parsed.hostname.removeprefix("www.")
    return items


async def _follow(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        resp = await client.get(url)
        return str(resp.url) if resp.url else None
    except Exception:
        return None


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


def _parse_json_items(text: str) -> dict:
    """Gemini sometimes wraps JSON in ```json fences despite the prompt.
    Strip those, then json.loads. If that fails, fall back to finding the
    outermost {...} block via bracket matching."""
    body = text.strip()
    m = _CODE_FENCE_RX.match(body)
    if m:
        body = m.group(1).strip()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        pass

    # Fallback: find first '{' to matching '}'.
    start = body.find("{")
    if start < 0:
        return {"items": []}
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
    log.warning("critical_reading: could not parse Gemini JSON response")
    return {"items": []}


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

    import asyncio

    cfg = Config.from_env()
    out_dir = args.out_dir or (cfg.data_dir / "critical-reading")
    asyncio.run(build_critical_reading(out_dir=out_dir, now=datetime.now(tz=timezone.utc)))


if __name__ == "__main__":
    _cli()
