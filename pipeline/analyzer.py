"""Claude Sonnet analyzer: classifies a diff and emits structured analysis."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from anthropic import AsyncAnthropic

from pipeline.sources import Source
from pipeline.taxonomy import Track, validate_tracks

# Per-pillar default routing: crawler events are rare (1-2/month) and
# high-stakes (the whole site's point is catching these), so they get the
# stronger model. News pillars are high-volume; Haiku is 4x cheaper and
# adequate for "summarize this blog post + 3-sentence implication".
SONNET_MODEL = "claude-sonnet-4-6"
HAIKU_MODEL = "claude-haiku-4-5-20251001"
OPUS_MODEL = "claude-opus-4-7"

Confidence = Literal["low", "medium", "high"]


@dataclass
class AnalysisResult:
    change_kind: Literal["material", "cosmetic", "noise"]
    importance: float
    title: str
    what_changed: str
    implication: str
    primary_track: Track
    tracks: list[Track]
    actors: list[str]
    trend_signals: list[str]
    confidence: Confidence


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
            "primary_track": {
                "type": "string",
                "enum": [track.value for track in Track],
            },
            "tracks": {
                "type": "array",
                "items": {"type": "string", "enum": [track.value for track in Track]},
                "minItems": 1,
                "uniqueItems": True,
            },
            "actors": {"type": "array", "items": {"type": "string"}},
            "trend_signals": {"type": "array", "items": {"type": "string"}},
            "confidence": {
                "type": "string",
                "enum": ["low", "medium", "high"],
            },
        },
        "required": [
            "change_kind",
            "importance",
            "title",
            "what_changed",
            "implication",
            "primary_track",
            "tracks",
            "actors",
            "trend_signals",
            "confidence",
        ],
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
    "CITATION STYLE: In what_changed and implication, cite primary sources INLINE "
    "using markdown link syntax at the point the claim is made — e.g. "
    "'[Cloudflare ships redirects for AI training](https://blog.cloudflare.com/ai-redirects/) "
    "signals...'. Use the specific URLs from CURRENT or the Cited-sources section if present. "
    "Never invent URLs. If a claim isn't supported by a listed URL, state the claim "
    "without a link rather than fabricating one. Never link the same URL more than twice.\n\n"
    "Always call the emit_analysis tool exactly once with your verdict."
)


_CRAWLER_ADDON = (
    "\n\nThis is a PILLAR 1 crawler-doc source: the reader is looking for precise fact "
    "(what UA string changed, what directive was added, what opt-out mechanism shifted). "
    "Keep `what_changed` ≤3 sentences, factual. `implication` may be empty if no notable "
    "reader takeaway."
)

_NEWS_ADDON = (
    "\n\nThis is a pillar-2/3 news source. You are covering a NEWS ITEM, not a "
    "change to a page — don't use 'what changed' framing. Structure your answer "
    "as:\n"
    "  - what_changed: 3-5 sentences summarizing the NEWS itself — what was "
    "announced / filed / shipped / said, with inline [markdown](url) citations "
    "to primary sources at the point each fact is stated. Treat this as the "
    "news brief.\n"
    "  - implication: 4-6 sentences of WHY IT MATTERS — the effect on "
    "publishers, regulators, or agent-infra practitioners. Continue citing "
    "inline when you reference external facts or prior context. "
    "If RECENT ITEMS context is provided, ground your analysis in the pattern — "
    "'third such deal this month', 'reverses a stance from last quarter', "
    "'continues a trend' — when the facts actually support it. Don't invent "
    "patterns that aren't in the history.\n"
    "\n"
    "MANDATORY: include at least one inline primary-source link in the news "
    "brief (what_changed). Never write news without a citation anchor. If the "
    "only URL you have is the item's own URL (shown as URL above), cite that. "
    "Set importance based on ecosystem-reshaping potential, not novelty."
)


async def analyze_change(
    *,
    client: AsyncAnthropic,
    source: Source,
    prev_content: str,
    curr_content: str,
    unified_diff: str,
    trend_context: str = "",
    item_url: str | None = None,
    published_at: datetime | None = None,
) -> AnalysisResult:
    crawler_control_source = Track.CRAWLER_CONTROLS in source.default_tracks
    system = _SYSTEM_BASE + (_CRAWLER_ADDON if crawler_control_source else _NEWS_ADDON)
    model = _resolve_model(source)
    primary_url = item_url or source.url or ""
    user_content_parts = [
        f"Source: {source.display_name}",
        f"Source tier: {source.tier.value}",
        f"Default tracks: {', '.join(track.value for track in source.default_tracks)}",
        f"Allowed tracks: {', '.join(track.value for track in Track)}",
        f"Published at: {published_at.isoformat() if published_at else 'unknown'}",
        f"URL: {primary_url}",
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
            # Defensive construction — LLMs occasionally drop a required field
            # (particularly Haiku on long prompts). Fill with safe defaults
            # rather than crashing the whole pipeline run.
            args = dict(block.input or {})
            primary_track, tracks, confidence = _validated_classification(args, source)
            return AnalysisResult(
                change_kind=args.get("change_kind", "cosmetic"),
                importance=float(args.get("importance", 0.3) or 0.3),
                title=args.get("title") or "(untitled change)",
                what_changed=args.get("what_changed") or "",
                implication=args.get("implication") or "",
                primary_track=primary_track,
                tracks=tracks,
                actors=_clean_string_list(args.get("actors")),
                trend_signals=_clean_string_list(args.get("trend_signals")),
                confidence=confidence,
            )
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
    if Track.CRAWLER_CONTROLS in source.default_tracks:
        return SONNET_MODEL
    return HAIKU_MODEL


def _validated_classification(
    args: dict, source: Source
) -> tuple[Track, list[Track], Confidence]:
    try:
        primary_track = Track(args.get("primary_track"))
        tracks = [Track(value) for value in args.get("tracks", [])]
        validate_tracks(primary_track, tracks)
        confidence = args.get("confidence", "low")
        if confidence not in {"low", "medium", "high"}:
            raise ValueError("invalid confidence")
        return primary_track, tracks, confidence
    except (TypeError, ValueError):
        fallback = source.default_tracks[0]
        return fallback, [fallback], "low"


def _clean_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(
        dict.fromkeys(
            item.strip() for item in value if isinstance(item, str) and item.strip()
        )
    )
