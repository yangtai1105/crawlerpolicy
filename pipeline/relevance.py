"""Two-stage relevance funnel: cheap keyword regex, then Haiku classifier."""
from __future__ import annotations

import json
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
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(needle) + r"(?![a-z0-9])")
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
    "Return a single JSON object: "
    '{"is_relevant": true|false, "reason": "<one short sentence>"}'
)


async def haiku_relevance(
    client: AsyncAnthropic, title: str, summary: str
) -> RelevanceVerdict:
    """Stage 2: Haiku call returning structured verdict."""
    resp = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        system=_RELEVANCE_PROMPT,
        messages=[{"role": "user", "content": f"Title: {title}\n\nSummary: {summary}"}],
    )
    text = resp.content[0].text
    data = json.loads(text)
    return RelevanceVerdict(is_relevant=bool(data["is_relevant"]), reason=data["reason"])
