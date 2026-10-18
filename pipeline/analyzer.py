"""Structured editorial analysis for detected ecosystem changes."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, model_validator

from pipeline.entities import EntityRegistry
from pipeline.model_provider import StructuredModel
from pipeline.positions import PositionStatus
from pipeline.sources import Source
from pipeline.taxonomy import Subject, Track, validate_tracks

Confidence = Literal["low", "medium", "high"]
ChangeKind = Literal["material", "cosmetic", "noise"]


class PositionClaim(BaseModel):
    """What the model says a development implies, before resolution."""

    player: str
    protocol: str
    status: str


class ResolvedPositionClaim(BaseModel):
    """A claim whose names resolved to registry slugs and whose status is valid."""

    player_slug: str
    protocol_slug: str
    status: PositionStatus


class AnalyzerResponse(BaseModel):
    """Provider response before taxonomy validation and safe fallbacks."""

    change_kind: ChangeKind
    importance: float = Field(ge=0.0, le=1.0)
    title: str
    summary: str
    insight: str
    implication: str
    why_it_matters: str
    key_facts: list[str] = Field(default_factory=list)
    primary_track: str
    tracks: list[str]
    actors: list[str]
    subject: str = "unknown"
    protocols: list[str] = Field(default_factory=list)
    position_claims: list[PositionClaim] = Field(default_factory=list)
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
    key_facts: list[str] = Field(default_factory=list)
    primary_track: Track
    tracks: list[Track]
    actors: list[str]
    subject: Subject = Subject.UNKNOWN
    players: list[str] = Field(default_factory=list)
    protocols: list[str] = Field(default_factory=list)
    position_claims: list[ResolvedPositionClaim] = Field(default_factory=list)
    # Carried to the caller for the review queue; never written to frontmatter.
    unknown_players: list[str] = Field(default_factory=list)
    unknown_protocols: list[str] = Field(default_factory=list)
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

The summary is short by design, so detail must not be lost there. Also return `key_facts`:
3-8 standalone factual statements extracted from the evidence, staying close to the source's
own words. Cover who acted, exactly what changed, scope and exceptions, every figure that
matters (numbers, percentages, money, counts, dates), named mechanisms or clauses, and the
responses of affected parties, with short quotes attributed to their speaker when the source
quotes someone. No interpretation in key_facts. Return an empty list for cosmetic or noise.

Use inline Markdown links only when the supplied content contains the exact URL. Keep claims
proportional to the evidence. Reserve importance above 0.9 for ecosystem-shaping developments.

Name only entities you are confident appear in the evidence. Set `subject` to `crawler` when
the development concerns automated crawling, `agent` when it concerns delegated agents acting
for a user, `both` when it genuinely concerns both, and `unknown` when the evidence does not
say. List protocol names in `protocols`.

When the evidence states a named company's position on a named protocol, add it to
`position_claims` with `status` one of: shipped (in production), preview (limited or
beta), stated (publicly committed but not shipped), declined (publicly refused or
rejected). Omit the claim entirely when the evidence does not say. Never infer `declined`
from silence — it requires an explicit public refusal.
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

_REGISTRY: EntityRegistry | None = None


def _registry() -> EntityRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        from pipeline.entities import load_registry

        _REGISTRY = load_registry()
    return _REGISTRY


def resolve_entities(
    registry: EntityRegistry,
    *,
    actors: list[str],
    protocols: list[str],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Split observed names into registry slugs and out-of-vocabulary names.

    Slugs are deduplicated, so two aliases of one entity collapse to one slug.
    """
    player_slugs: list[str] = []
    protocol_slugs: list[str] = []
    unknown_players: list[str] = []
    unknown_protocols: list[str] = []

    for name in actors:
        slug = registry.resolve_player(name)
        if slug is None:
            unknown_players.append(name)
        elif slug not in player_slugs:
            player_slugs.append(slug)

    for name in protocols:
        slug = registry.resolve_protocol(name)
        if slug is None:
            unknown_protocols.append(name)
        elif slug not in protocol_slugs:
            protocol_slugs.append(slug)

    return player_slugs, protocol_slugs, unknown_players, unknown_protocols


def resolve_position_claims(
    registry: EntityRegistry,
    claims: list[PositionClaim],
) -> tuple[list[ResolvedPositionClaim], list[str], list[str]]:
    """Resolve claim names to registry slugs and validate the status.

    A claim survives only when both names resolve and the status is one of the
    five published values. Everything else is reported for review rather than
    guessed at — a wrong cell is a factual error on a published matrix.
    """
    resolved: list[ResolvedPositionClaim] = []
    unknown_players: list[str] = []
    unknown_protocols: list[str] = []

    for claim in claims:
        player_slug = registry.resolve_player(claim.player)
        protocol_slug = registry.resolve_protocol(claim.protocol)
        if player_slug is None:
            unknown_players.append(claim.player)
        if protocol_slug is None:
            unknown_protocols.append(claim.protocol)
        if player_slug is None or protocol_slug is None:
            continue
        try:
            status = PositionStatus(claim.status.strip().lower())
        except ValueError:
            continue
        resolved.append(
            ResolvedPositionClaim(
                player_slug=player_slug, protocol_slug=protocol_slug, status=status
            )
        )

    return resolved, unknown_players, unknown_protocols


def _validated_subject(raw: AnalyzerResponse, source: Source) -> Subject:
    """Fall back to the source's declared subject, mirroring track fallback.

    `AnalyzerResponse.subject` defaults to the string "unknown", which is also a
    valid `Subject` member, so an unresolved or absent model answer is indistinguishable
    from the parsed value `Subject.UNKNOWN`. Treat both as "the model didn't say" and
    defer to the source's own default rather than publishing an uninformative subject.
    """
    try:
        value = Subject(raw.subject)
    except ValueError:
        return source.default_subject
    if value is Subject.UNKNOWN:
        return source.default_subject
    return value


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
    crawler_control_source = Track.ACCESS_CONTROLS in source.default_tracks
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
            f"=== CURRENT ===\n{curr_content[:40000]}",
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
    actors = _clean_string_list(raw.actors)
    players, protocols, unknown_players, unknown_protocols = resolve_entities(
        _registry(),
        actors=actors,
        protocols=_clean_string_list(raw.protocols),
    )
    claims, claim_unknown_players, claim_unknown_protocols = resolve_position_claims(
        _registry(), raw.position_claims
    )
    return AnalysisResult(
        change_kind=raw.change_kind,
        importance=raw.importance,
        title=raw.title.strip() or "Untitled ecosystem development",
        summary=raw.summary.strip(),
        insight=raw.insight.strip(),
        implication=raw.implication.strip(),
        why_it_matters=raw.why_it_matters.strip(),
        key_facts=[" ".join(fact.split()) for fact in _clean_string_list(raw.key_facts)][:8],
        primary_track=primary_track,
        tracks=tracks,
        actors=actors,
        subject=_validated_subject(raw, source),
        players=players,
        protocols=protocols,
        position_claims=claims,
        unknown_players=list(dict.fromkeys([*unknown_players, *claim_unknown_players])),
        unknown_protocols=list(dict.fromkeys([*unknown_protocols, *claim_unknown_protocols])),
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
