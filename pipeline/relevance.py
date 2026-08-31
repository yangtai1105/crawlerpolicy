"""Two-stage relevance funnel: cheap keyword regex, then a structured model."""
from __future__ import annotations

import re

from pydantic import BaseModel

from pipeline.model_provider import StructuredModel


def keyword_match(text: str, keywords: list[str]) -> bool:
    """Stage 1: cheap word-boundary regex match against any keyword."""
    if not keywords:
        return True
    haystack = text.lower()
    for keyword in keywords:
        needle = keyword.lower().strip()
        if not needle:
            continue
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(needle))
        if pattern.search(haystack):
            return True
    return False


class RelevanceVerdict(BaseModel):
    is_relevant: bool
    reason: str


_RELEVANCE_PROMPT = """Classify whether the supplied item is relevant to Crawler Policy.
Relevant subjects are AI crawler policy, AI training data, bot access and robots.txt, AI-related
content regulation, agent infrastructure, crawler identity and authentication, content rights,
licensing, and the economics or measurement of machine traffic. Return a concise reason grounded
only in the supplied title and summary.
"""


async def model_relevance(
    model: StructuredModel,
    title: str,
    summary: str,
) -> RelevanceVerdict:
    return await model.generate(
        response_model=RelevanceVerdict,
        system_instruction=_RELEVANCE_PROMPT,
        prompt=f"Title: {title}\n\nSummary: {summary}",
    )


# Compatibility alias for the orchestrator while it migrates to provider-neutral naming.
haiku_relevance = model_relevance
