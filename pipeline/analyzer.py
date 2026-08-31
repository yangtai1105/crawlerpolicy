"""Structured editorial analysis for detected ecosystem changes."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, model_validator

from pipeline.model_provider import StructuredModel
from pipeline.sources import Source
from pipeline.taxonomy import Track, validate_tracks

Confidence = Literal["low", "medium", "high"]
ChangeKind = Literal["material", "cosmetic", "noise"]


class AnalyzerResponse(BaseModel):
    """Provider response before taxonomy validation and safe fallbacks."""

    change_kind: ChangeKind
    importance: float = Field(ge=0.0, le=1.0)
    title: str
    summary: str
    insight: str
    implication: str
    why_it_matters: str
    primary_track: str
    tracks: list[str]
    actors: list[str]
    trend_signals: list[str]
    confidence: str


class AnalysisResult(BaseModel):
    change_kind: ChangeKind
    importance: float = Field(ge=0.0, le=1.0)
    title: str
    summary: str = Field(validation_alias=AliasChoices("summary", "what_changed"))
    insight: str = ""
    implication: str = ""
    why_it_matters: str = ""
    primary_track: Track
    tracks: list[Track]
    actors: list[str]
    trend_signals: list[str]
    confidence: Confidence

    @model_validator(mode="after")
    def _fill_reader_layers(self) -> AnalysisResult:
        if not self.insight:
            self.insight = self.summary
        if not self.why_it_matters:
            self.why_it_matters = self.implication
        return self

    @property
    def what_changed(self) -> str:
        """Compatibility name used by existing trend and event code."""
        return self.summary


_SYSTEM_BASE = """You are the editorial analyst for Crawler Policy, an English-language
publication about machine access to the web. Analyze only the supplied evidence. Never invent
facts, dates, actors, or URLs.

Classify the evidence as:
- material: a substantive policy, product, legal, market, measurement, or standards development;
- cosmetic: wording or presentation changed without altering meaning;
- noise: formatting, dates, duplicate material, or unrelated content.

Write four distinct reader layers:
- summary: 2-3 factual sentences explaining what happened;
- insight: the new pattern, distinction, or mechanism exposed by the evidence;
- implication: who or what may be affected next;
- why_it_matters: the clearest reason a reader should care now.

Use inline Markdown links only when the supplied content contains the exact URL. Keep claims
proportional to the evidence. Reserve importance above 0.9 for ecosystem-shaping developments.
"""

_CRAWLER_ADDON = """
This is a crawler-control source. Be precise about user-agent strings, directives, scope,
enforcement, and opt-out mechanisms. Do not turn a cosmetic documentation edit into a policy
change.
"""

_NEWS_ADDON = """
This is a news or ecosystem item. Summarize the announcement, filing, release, or observation
rather than describing a page diff. Use recent-item context only when it directly supports a
pattern.
"""


async def analyze_change(
    *,
    model: StructuredModel,
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
    primary_url = item_url or source.url or ""
    prompt_parts = [
        f"Source: {source.display_name}",
        f"Source tier: {source.tier.value}",
        f"Default tracks: {', '.join(track.value for track in source.default_tracks)}",
        f"Allowed tracks: {', '.join(track.value for track in Track)}",
        f"Published at: {published_at.isoformat() if published_at else 'unknown'}",
        f"URL: {primary_url}",
        "",
    ]
    if trend_context:
        prompt_parts.extend([trend_context, ""])
    prompt_parts.extend(
        [
            f"=== PREVIOUS ===\n{prev_content[:20000]}",
            "",
            f"=== CURRENT ===\n{curr_content[:20000]}",
            "",
            f"=== DIFF ===\n{unified_diff[:20000]}",
        ]
    )

    raw = await model.generate(
        response_model=AnalyzerResponse,
        system_instruction=system,
        prompt="\n".join(prompt_parts),
    )
    primary_track, tracks, confidence = _validated_classification(raw, source)
    return AnalysisResult(
        change_kind=raw.change_kind,
        importance=raw.importance,
        title=raw.title.strip() or "Untitled ecosystem development",
        summary=raw.summary.strip(),
        insight=raw.insight.strip(),
        implication=raw.implication.strip(),
        why_it_matters=raw.why_it_matters.strip(),
        primary_track=primary_track,
        tracks=tracks,
        actors=_clean_string_list(raw.actors),
        trend_signals=_clean_string_list(raw.trend_signals),
        confidence=confidence,
    )


def _validated_classification(
    raw: AnalyzerResponse, source: Source
) -> tuple[Track, list[Track], Confidence]:
    try:
        primary_track = Track(raw.primary_track)
        tracks = [Track(value) for value in raw.tracks]
        validate_tracks(primary_track, tracks)
        if raw.confidence not in {"low", "medium", "high"}:
            raise ValueError("invalid confidence")
        return primary_track, tracks, raw.confidence
    except (TypeError, ValueError):
        fallback = source.default_tracks[0]
        return fallback, [fallback], "low"


def _clean_string_list(value: list[str]) -> list[str]:
    return list(dict.fromkeys(item.strip() for item in value if item.strip()))
