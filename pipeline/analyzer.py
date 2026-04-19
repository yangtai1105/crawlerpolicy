"""Claude Sonnet analyzer: classifies a diff and emits structured analysis."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from anthropic import AsyncAnthropic

from pipeline.sources import Pillar, Source

DEFAULT_MODEL = "claude-sonnet-4-6"
OPUS_MODEL = "claude-opus-4-7"


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
    "\n\nThis is a pillar-2/3 news source: the reader wants 3–5 sentences of what_changed "
    "and 3–5 sentences of implication explaining why a publisher / policy / agent-infra "
    "practitioner should care. Avoid hype."
)


async def analyze_change(
    *,
    client: AsyncAnthropic,
    source: Source,
    prev_content: str,
    curr_content: str,
    unified_diff: str,
) -> AnalysisResult:
    system = _SYSTEM_BASE + (_CRAWLER_ADDON if source.pillar == Pillar.CRAWLER else _NEWS_ADDON)
    model = _resolve_model(source.model)
    user_content = (
        f"Source: {source.display_name} ({source.pillar.value})\n"
        f"URL: {source.url or ''}\n\n"
        f"=== PREVIOUS ===\n{prev_content[:20000]}\n\n"
        f"=== CURRENT ===\n{curr_content[:20000]}\n\n"
        f"=== DIFF ===\n{unified_diff[:20000]}\n"
    )

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


def _resolve_model(override: str | None) -> str:
    if override == "opus":
        return OPUS_MODEL
    if override and override.startswith("claude-"):
        return override
    return DEFAULT_MODEL
