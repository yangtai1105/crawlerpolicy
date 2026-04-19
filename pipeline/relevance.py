"""Two-stage relevance funnel: cheap keyword regex, then Haiku classifier."""
from __future__ import annotations

import re
from dataclasses import dataclass

from anthropic import AsyncAnthropic


def keyword_match(text: str, keywords: list[str]) -> bool:
    """Stage 1: cheap word-boundary regex match against any keyword."""
    if not keywords:
        return True
    haystack = text.lower()
    for kw in keywords:
        needle = kw.lower().strip()
        if not needle:
            continue
        # Leading boundary only, so "AI bot" matches "AI bots" / "AI botnet".
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(needle))
        if pattern.search(haystack):
            return True
    return False


@dataclass
class RelevanceVerdict:
    is_relevant: bool
    reason: str


_RELEVANCE_PROMPT = (
    "You are a classifier for an AI-content-ecosystem tracker. "
    "Given a post title and summary, decide whether it is RELEVANT to: "
    "AI crawler policy, AI training data, bot access / robots.txt, "
    "content-ecosystem regulation (AI), AI agent infrastructure, "
    "AI bot identity / auth. "
    "Always call the emit_verdict tool with your decision."
)

_TOOL = {
    "name": "emit_verdict",
    "description": "Emit a structured relevance verdict.",
    "input_schema": {
        "type": "object",
        "properties": {
            "is_relevant": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": ["is_relevant", "reason"],
    },
}


async def haiku_relevance(
    client: AsyncAnthropic, title: str, summary: str
) -> RelevanceVerdict:
    """Stage 2: Haiku tool-use call returning a guaranteed-structured verdict."""
    resp = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        system=_RELEVANCE_PROMPT,
        tools=[_TOOL],
        tool_choice={"type": "tool", "name": "emit_verdict"},
        messages=[{"role": "user", "content": f"Title: {title}\n\nSummary: {summary}"}],
    )
    for block in resp.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "emit_verdict":
            args = block.input
            return RelevanceVerdict(
                is_relevant=bool(args.get("is_relevant", False)),
                reason=str(args.get("reason", "")),
            )
    # Fallback: if the model refused to call the tool, treat as not relevant.
    return RelevanceVerdict(is_relevant=False, reason="no tool_use returned")
