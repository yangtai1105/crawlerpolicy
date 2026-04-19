"""Extract per-crawler facts with Haiku and aggregate State-of-Play JSON."""
from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from anthropic import AsyncAnthropic

from pipeline.sources import Source

HAIKU_MODEL = "claude-haiku-4-5-20251001"


def _as_bool(v) -> bool | None:
    """Coerce Haiku tool output to a strict bool or None.

    Haiku occasionally ignores the schema and returns a string placeholder
    (e.g. '<UNKNOWN>') instead of a true bool. Fall back to null so the
    frontend can render 'unknown' rather than crash on truthy strings.
    """
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.strip().lower() in ("true", "false"):
        return v.strip().lower() == "true"
    return None

_CRAWLER_FACTS_TOOL = {
    "name": "emit_crawler_facts",
    "description": "Emit structured facts about this vendor's AI bot/crawler documentation.",
    "input_schema": {
        "type": "object",
        "properties": {
            "supports_robots_txt": {"type": "boolean"},
            "supports_user_agent_opt_out": {"type": "boolean"},
            "policy_url": {"type": "string"},
            "user_agents": {
                "type": "array",
                "description": (
                    "Each distinct user-agent documented on this page. List ALL of them — "
                    "training crawlers, search crawlers, user-triggered fetchers, agent "
                    "actions, etc. If the page only mentions one, return one."
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The UA string or product name (e.g. 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User')",
                        },
                        "purpose": {
                            "type": "string",
                            "description": "≤15 words — what this UA is for (e.g. 'training data collection', 'search index updates')",
                        },
                        "scope": {
                            "type": "string",
                            "description": "≤25 words — what it crawls or when it fires (e.g. 'general web crawl', 'user-triggered fetch for live responses')",
                        },
                        "opt_out": {
                            "type": "string",
                            "description": "≤20 words — documented opt-out mechanism for THIS specific UA (e.g. 'User-agent: GPTBot / Disallow: /', 'honors Google-Extended robots token')",
                        },
                    },
                    "required": ["name", "purpose"],
                },
            },
        },
        "required": ["supports_robots_txt", "supports_user_agent_opt_out", "policy_url", "user_agents"],
    },
}


async def _extract_crawler_facts(
    client: AsyncAnthropic, source: Source, content: str
) -> dict:
    msg = await client.messages.create(
        model=HAIKU_MODEL,
        # Needs enough room for the UA array (vendors can document 5-8 UAs).
        max_tokens=2500,
        system=(
            "You extract factual fields from an AI crawler's official documentation. "
            "Be conservative: only mark booleans true when the documentation explicitly "
            "supports it. For user_agents, list EVERY distinct UA name mentioned on the "
            "page — don't skip any, even if purpose is similar to another. Use the "
            "specific name the vendor uses (e.g. 'GPTBot', 'OAI-SearchBot', 'Claude-User')."
        ),
        tools=[_CRAWLER_FACTS_TOOL],
        tool_choice={"type": "tool", "name": "emit_crawler_facts"},
        messages=[
            {
                "role": "user",
                "content": f"Vendor: {source.display_name}\n\n{content[:15000]}",
            }
        ],
    )
    for block in msg.content:
        if getattr(block, "type", None) == "tool_use":
            return dict(block.input)
    raise RuntimeError(f"state_of_play: no tool_use for {source.slug}")


async def build_opt_out_matrix(
    *,
    client: AsyncAnthropic,
    crawler_sources: list[Source],
    load_latest_snapshot: Callable[[str], tuple[str, datetime] | None],
    out_path: Path,
    now: datetime,
) -> None:
    entries = []
    for s in crawler_sources:
        snap = load_latest_snapshot(s.slug)
        if not snap:
            continue
        content, snap_date = snap
        facts = await _extract_crawler_facts(client, s, content)
        days_since = (now.date() - snap_date.date()).days
        entries.append(
            {
                "slug": s.slug,
                "display_name": s.display_name,
                "supports_robots_txt": _as_bool(facts["supports_robots_txt"]),
                "supports_user_agent_opt_out": _as_bool(facts["supports_user_agent_opt_out"]),
                "policy_url": facts["policy_url"],
                "days_since_last_change": days_since,
                "last_snapshot_date": snap_date.date().isoformat(),
                "user_agents": facts.get("user_agents") or [],
            }
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"generated_at": now.isoformat(), "entries": entries}, indent=2)
    )
