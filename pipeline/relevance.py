"""Two-stage relevance funnel: cheap keyword regex, then a structured model."""
from __future__ import annotations

import re

from pydantic import BaseModel

from pipeline.model_provider import StructuredModel


def keyword_match(text: str, keywords: list[str]) -> bool:
    """Stage 1: cheap word-boundary regex match against any keyword.

    Keywords match at the start of a word, so "bot" still catches "bots" and
    "auth" catches "authentication". A keyword written in capitals ("AI",
    "API", "DSA") is an acronym and must end the word, allowing a plural "s":
    otherwise "AI" matches the "aid" in every "State aid" press release.
    """
    if not keywords:
        return True
    haystack = text.lower()
    for keyword in keywords:
        stripped = keyword.strip()
        if not stripped:
            continue
        acronym = not any(c.islower() for c in stripped) and stripped[-1].isalnum()
        tail = r"s?(?![a-z0-9])" if acronym else ""
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(stripped.lower()) + tail)
        if pattern.search(haystack):
            return True
    return False


class RelevanceVerdict(BaseModel):
    is_relevant: bool
    reason: str


_RELEVANCE_PROMPT = """Classify whether the supplied item is relevant to Crawler Policy.
Relevant subjects are AI crawler policy, AI training data, bot access and robots.txt, AI-related
content regulation, agent infrastructure, crawler identity and authentication, content rights,
licensing, AI search and discovery (AI answers, citations, referrals), AI platforms' programs,
products, or deals with publishers and other content owners, and the economics or measurement of
machine traffic. Return a concise reason grounded
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
