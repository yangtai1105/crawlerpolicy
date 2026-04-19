"""Extract per-crawler facts with Haiku and aggregate State-of-Play JSON."""
from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from anthropic import AsyncAnthropic

from pipeline.sources import Source

HAIKU_MODEL = "claude-haiku-4-5-20251001"

_CRAWLER_FACTS_TOOL = {
    "name": "emit_crawler_facts",
    "description": "Emit structured facts about this crawler's opt-out behavior.",
    "input_schema": {
        "type": "object",
        "properties": {
            "supports_robots_txt": {"type": "boolean"},
            "supports_user_agent_opt_out": {"type": "boolean"},
            "policy_url": {"type": "string"},
        },
        "required": ["supports_robots_txt", "supports_user_agent_opt_out", "policy_url"],
    },
}


async def _extract_crawler_facts(
    client: AsyncAnthropic, source: Source, content: str
) -> dict:
    msg = await client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=300,
        system=(
            "You extract factual fields from an AI crawler's official documentation. "
            "Be conservative: only mark true when the documentation explicitly supports it."
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
                "supports_robots_txt": facts["supports_robots_txt"],
                "supports_user_agent_opt_out": facts["supports_user_agent_opt_out"],
                "policy_url": facts["policy_url"],
                "days_since_last_change": days_since,
                "last_snapshot_date": snap_date.date().isoformat(),
            }
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"generated_at": now.isoformat(), "entries": entries}, indent=2)
    )
