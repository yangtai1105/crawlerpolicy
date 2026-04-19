"""Claude Sonnet analyzer: classifies a diff and emits structured analysis."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from anthropic import AsyncAnthropic

from pipeline.sources import Pillar, Source

# Per-pillar default routing: crawler events are rare (1-2/month) and
# high-stakes (the whole site's point is catching these), so they get the
# stronger model. News pillars are high-volume; Haiku is 4x cheaper and
# adequate for "summarize this blog post + 3-sentence implication".
SONNET_MODEL = "claude-sonnet-4-6"
HAIKU_MODEL = "claude-haiku-4-5-20251001"
OPUS_MODEL = "claude-opus-4-7"

DEFAULT_MODEL_BY_PILLAR: dict[Pillar, str] = {
    Pillar.CRAWLER: SONNET_MODEL,
    Pillar.ECOSYSTEM: HAIKU_MODEL,
    Pillar.AGENT: HAIKU_MODEL,
}


@dataclass
class AnalysisResult:
    change_kind: Literal["material", "cosmetic", "noise"]
    importance: float
    title: str
    what_changed: str
    implication: str


_TOOL = {
    "name": "emit_analysis",
    "description": "Emit a structured analysis of a detected content change.",
    "input_schema": {
        "type": "object",
        "properties": {
            "change_kind": {"type": "string", "enum": ["material", "cosmetic", "noise"]},
            "importance": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "title": {"type": "string"},
            "what_changed": {"type": "string"},
            "implication": {"type": "string"},
        },
        "required": ["change_kind", "importance", "title", "what_changed", "implication"],
    },
}


_SYSTEM_BASE = (
    "You are a precise analyst for an AI-content-ecosystem tracker. "
    "Given a change (diff + before/after content) from a specific source, "
    "classify and summarize it.\n\n"
    "Classification rules:\n"
    "- material: substantive content change (new policy, new UA string, new section, "
    "semantic revision of existing policy).\n"
    "- cosmetic: wording polish, small clarification without changing meaning.\n"
    "- noise: formatting, dates, unrelated artifact.\n\n"
    "Importance rubric (0.0–1.0): reserve 0.9+ for ecosystem-reshaping events; "
    "0.6–0.8 for notable-but-bounded news; 0.3–0.5 incremental; below 0.3 is likely cosmetic.\n\n"
    "Always call the emit_analysis tool exactly once with your verdict."
)


_CRAWLER_ADDON = (
    "\n\nThis is a PILLAR 1 crawler-doc source: the reader is looking for precise fact "
    "(what UA string changed, what directive was added, what opt-out mechanism shifted). "
    "Keep `what_changed` ≤3 sentences, factual. `implication` may be empty if no notable "
    "reader takeaway."
)

_NEWS_ADDON = (
    "\n\nThis is a pillar-2/3 news source: lead with IMPLICATION. The reader wants "
    "3-5 factual sentences in what_changed, then 4-6 sentences of implication "
    "explaining why a publisher / policy person / agent-infra practitioner should "
    "care. Avoid hype. If RECENT ITEMS context is provided, ground your implication "
    "in the pattern — e.g. 'the third such deal this month', 'reverses a stance from "
    "last quarter', 'continues a trend' — when the facts actually support it. "
    "Don't invent patterns that aren't in the history. Set importance based on the "
    "item's reshaping potential for the ecosystem, not just its novelty."
)


async def analyze_change(
    *,
    client: AsyncAnthropic,
    source: Source,
    prev_content: str,
    curr_content: str,
    unified_diff: str,
    trend_context: str = "",
) -> AnalysisResult:
    system = _SYSTEM_BASE + (_CRAWLER_ADDON if source.pillar == Pillar.CRAWLER else _NEWS_ADDON)
    model = _resolve_model(source)
    user_content_parts = [
        f"Source: {source.display_name} ({source.pillar.value})",
        f"URL: {source.url or ''}",
        "",
    ]
    if trend_context:
        user_content_parts.extend([trend_context, ""])
    user_content_parts.extend([
        f"=== PREVIOUS ===\n{prev_content[:20000]}",
        "",
        f"=== CURRENT ===\n{curr_content[:20000]}",
        "",
        f"=== DIFF ===\n{unified_diff[:20000]}",
    ])
    user_content = "\n".join(user_content_parts)

    msg = await client.messages.create(
        model=model,
        max_tokens=1500,
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        tools=[_TOOL],
        tool_choice={"type": "tool", "name": "emit_analysis"},
        messages=[{"role": "user", "content": user_content}],
    )

    for block in msg.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "emit_analysis":
            return AnalysisResult(**block.input)
    raise RuntimeError("analyzer did not return tool_use")


def _resolve_model(source: Source) -> str:
    override = source.model
    if override == "opus":
        return OPUS_MODEL
    if override == "sonnet":
        return SONNET_MODEL
    if override == "haiku":
        return HAIKU_MODEL
    if override and override.startswith("claude-"):
        return override
    return DEFAULT_MODEL_BY_PILLAR.get(source.pillar, SONNET_MODEL)
