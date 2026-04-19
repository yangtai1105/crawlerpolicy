"""Roll up each pillar's last 30 days of events into a synthesized briefing.

Writes `data/pillar-digests.json` with one entry per pillar:
  {
    "crawler":   {"headline": "...", "body": "...", "themes": ["...", ...], "event_count": N},
    "ecosystem": {...},
    "agent":     {...},
    "generated_at": "...",
    "window_days": 30
  }

The site's homepage reads this and renders three "State of [pillar]" cards.
Each call reads a compact events-context (titles + implications), not full
bodies — keeps cost low (Haiku × 3 calls/day ≈ \$1/month).
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from anthropic import AsyncAnthropic

from pipeline.sources import Pillar

log = logging.getLogger("pillar_digest")

HAIKU_MODEL = "claude-haiku-4-5-20251001"

_TOOL = {
    "name": "emit_pillar_digest",
    "description": "Emit a synthesized briefing on the pillar's last 30 days.",
    "input_schema": {
        "type": "object",
        "properties": {
            "headline": {
                "type": "string",
                "description": "One sentence capturing the central shift of the period (≤140 chars).",
            },
            "body": {
                "type": "string",
                "description": "4-6 sentences synthesizing themes, notable shifts, and what matters for readers.",
            },
            "themes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-5 short theme labels (2-4 words each).",
            },
        },
        "required": ["headline", "body", "themes"],
    },
}

_FRONT_RX = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
_TITLE_RX = re.compile(r'^title:\s*"?(.+?)"?\s*$', re.MULTILINE)
_SOURCE_RX = re.compile(r"^source:\s*(\S+)\s*$", re.MULTILINE)
_PILLAR_RX = re.compile(r"^pillar:\s*(\S+)\s*$", re.MULTILINE)
_DETECTED_RX = re.compile(r"^detected_at:\s*(\S+)\s*$", re.MULTILINE)
_IMPORTANCE_RX = re.compile(r"^importance:\s*([0-9.]+)\s*$", re.MULTILINE)
_IMPL_RX = re.compile(r"## Implication\s*\n+(.+?)(?=\n## |\Z)", re.DOTALL)


def _load_events_in_window(events_dir: Path, pillar: Pillar, now: datetime, days: int) -> list[dict]:
    cutoff = now - timedelta(days=days)
    events: list[dict] = []
    if not events_dir.exists():
        return events
    for path in events_dir.glob("*.md"):
        text = path.read_text()
        front_match = _FRONT_RX.search(text)
        if not front_match:
            continue
        frontmatter = front_match.group(1)
        m_pillar = _PILLAR_RX.search(frontmatter)
        if not m_pillar or m_pillar.group(1) != pillar.value:
            continue
        m_detected = _DETECTED_RX.search(frontmatter)
        if not m_detected:
            continue
        try:
            detected = datetime.fromisoformat(m_detected.group(1))
        except ValueError:
            continue
        if detected < cutoff:
            continue
        m_title = _TITLE_RX.search(frontmatter)
        m_source = _SOURCE_RX.search(frontmatter)
        m_importance = _IMPORTANCE_RX.search(frontmatter)
        m_impl = _IMPL_RX.search(text)
        events.append(
            {
                "detected_at": detected,
                "title": m_title.group(1) if m_title else "(untitled)",
                "source": m_source.group(1) if m_source else "",
                "importance": float(m_importance.group(1)) if m_importance else 0.0,
                "implication": (m_impl.group(1).strip() if m_impl else "")[:500],
            }
        )
    events.sort(key=lambda e: e["detected_at"], reverse=True)
    return events


_PILLAR_LABEL = {
    Pillar.CRAWLER: "AI crawler / bot documentation",
    Pillar.ECOSYSTEM: "AI content ecosystem (publisher actions, regulators, CDNs, deals)",
    Pillar.AGENT: "AI agent infrastructure and bot-identity standards",
}

_SYSTEM = (
    "You are writing a 'state of the pillar' briefing for an AI ecosystem "
    "tracker. The reader has been busy and wants the big picture of the last "
    "30 days in under a minute. Synthesize — don't list. Find the 3-5 threads "
    "that matter. If the window is quiet, say so plainly (don't manufacture "
    "drama). Neutral voice; no hype. Always call the emit_pillar_digest tool."
)


async def _synthesize(client: AsyncAnthropic, pillar: Pillar, events: list[dict]) -> dict:
    label = _PILLAR_LABEL[pillar]
    lines = [f"PILLAR: {label}", f"EVENTS IN LAST 30 DAYS (n={len(events)}, newest first):", ""]
    for e in events[:40]:  # cap context
        date = e["detected_at"].date().isoformat()
        lines.append(f"- [{date}] ({e['source']}, importance {e['importance']:.2f}) {e['title']}")
        if e["implication"]:
            lines.append(f"  implication: {e['implication']}")
    user = "\n".join(lines)

    msg = await client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=800,
        system=[{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}],
        tools=[_TOOL],
        tool_choice={"type": "tool", "name": "emit_pillar_digest"},
        messages=[{"role": "user", "content": user}],
    )
    for block in msg.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "emit_pillar_digest":
            return dict(block.input)
    raise RuntimeError(f"pillar_digest for {pillar.value}: no tool_use returned")


async def build_pillar_digests(
    *,
    client: AsyncAnthropic,
    events_dir: Path,
    out_path: Path,
    now: datetime,
    window_days: int = 30,
) -> None:
    digests: dict[str, dict] = {}
    for pillar in (Pillar.CRAWLER, Pillar.ECOSYSTEM, Pillar.AGENT):
        events = _load_events_in_window(events_dir, pillar, now, window_days)
        if not events:
            digests[pillar.value] = {
                "headline": f"Quiet window for {pillar.value}.",
                "body": (
                    f"No material events detected in the {pillar.value} pillar over the last "
                    f"{window_days} days. This is not necessarily a sign of ecosystem inactivity — "
                    "it can mean our tracked sources happened not to publish, or what they "
                    "published didn't pass the relevance filter. Add or adjust sources in "
                    "sources.yaml to broaden the radar."
                ),
                "themes": [],
                "event_count": 0,
            }
            continue
        try:
            result = await _synthesize(client, pillar, events)
            digests[pillar.value] = {**result, "event_count": len(events)}
            log.info("pillar_digest %s: %d events → %s", pillar.value, len(events), result["headline"])
        except Exception as e:
            log.exception("pillar_digest %s failed", pillar.value)
            digests[pillar.value] = {
                "headline": f"({pillar.value} digest generation failed)",
                "body": f"Digest synthesis errored: {e}",
                "themes": [],
                "event_count": len(events),
            }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "generated_at": now.isoformat(),
                "window_days": window_days,
                **digests,
            },
            indent=2,
        )
    )
