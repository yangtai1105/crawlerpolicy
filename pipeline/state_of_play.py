"""Extract per-crawler facts and aggregate the State of Play matrix."""
from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from pipeline.model_provider import StructuredModel
from pipeline.sources import Source
from pipeline.taxonomy import Track


class UserAgentFact(BaseModel):
    name: str
    purpose: str
    scope: str = ""
    opt_out: str = ""


class CrawlerFacts(BaseModel):
    supports_robots_txt: bool | None
    supports_user_agent_opt_out: bool | None
    policy_url: str
    user_agents: list[UserAgentFact] = Field(default_factory=list)


def select_crawler_control_sources(sources: list[Source]) -> list[Source]:
    """Return sources that document crawler access controls."""
    return [
        source
        for source in sources
        if Track.CRAWLER_CONTROLS in source.default_tracks
    ]


_CRAWLER_FACTS_PROMPT = """Extract factual fields from official AI crawler documentation.
Be conservative: use true only when the documentation explicitly supports it and null when the
answer is unknown. List every distinct user-agent name mentioned, including training crawlers,
search crawlers, user-triggered fetchers, and agent actions. Use the vendor's exact names. Keep
purpose under 15 words, scope under 25 words, and opt_out under 20 words. Never infer a policy URL
that is not present in the supplied evidence.
"""


async def _extract_crawler_facts(
    model: StructuredModel,
    source: Source,
    content: str,
) -> CrawlerFacts:
    return await model.generate(
        response_model=CrawlerFacts,
        system_instruction=_CRAWLER_FACTS_PROMPT,
        prompt=f"Vendor: {source.display_name}\n\n{content[:15000]}",
    )


async def build_opt_out_matrix(
    *,
    model: StructuredModel,
    crawler_sources: list[Source],
    load_latest_snapshot: Callable[[str], tuple[str, datetime] | None],
    out_path: Path,
    now: datetime,
) -> None:
    entries = []
    for source in crawler_sources:
        snapshot = load_latest_snapshot(source.slug)
        if not snapshot:
            continue
        content, snapshot_date = snapshot
        facts = await _extract_crawler_facts(model, source, content)
        entries.append(
            {
                "slug": source.slug,
                "display_name": source.display_name,
                "supports_robots_txt": facts.supports_robots_txt,
                "supports_user_agent_opt_out": facts.supports_user_agent_opt_out,
                "policy_url": facts.policy_url,
                "days_since_last_change": (now.date() - snapshot_date.date()).days,
                "last_snapshot_date": snapshot_date.date().isoformat(),
                "user_agents": [
                    item.model_dump(mode="json") for item in facts.user_agents
                ],
            }
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {"generated_at": now.isoformat(), "entries": entries},
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
