"""Freshness and exclusivity gate for live X discovery candidates.

An X post is only worth surfacing when it is recent and reports a development
the publication has not already carried. Each candidate is checked against the
recent feed and recent X evidence: first deterministically (age, shared URLs),
then with one small structured model call that judges whether it describes
the same underlying development as anything already seen.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

import yaml
from pydantic import BaseModel

from pipeline.evidence import EvidenceRecord, EvidenceStage, load_evidence
from pipeline.model_provider import StructuredModel

MAX_AGE = timedelta(hours=48)
_FEED_LOOKBACK = timedelta(days=14)
_X_LOOKBACK = timedelta(days=3)
_MAX_SEEN = 80

NoveltyOutcome = Literal["new", "stale", "covered", "duplicate"]


@dataclass(frozen=True)
class SeenItem:
    ref: str
    title: str
    origin: str
    when: datetime
    urls: frozenset[str]


@dataclass(frozen=True)
class NoveltyDecision:
    outcome: NoveltyOutcome
    reason: str
    matched: str | None = None

    @property
    def surfaces(self) -> bool:
        return self.outcome == "new"

    def as_metadata(self) -> dict[str, str | None]:
        return {"outcome": self.outcome, "matched": self.matched, "reason": self.reason}


class NoveltyVerdict(BaseModel):
    is_new: bool
    matched_ref: str | None = None
    reason: str


_NOVELTY_PROMPT = """You screen breaking-news candidates for Crawler Policy, a publication on
AI crawling, agents, content rights, governance, and AI traffic economics.
Decide whether the candidate reports a development that is NOT already in the
list of items the publication has seen. It is not new when it describes the same
underlying development as a listed item, even in different words, from a
different outlet, or with a different headline. It is new when no listed item
covers it, or when it adds a materially new step (for example a ruling after a
filing, or a launch after an announcement). When it is not new, set matched_ref
to the ref of the closest listed item. Give a one-sentence reason.
"""


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix("www.")
    return f"{host}{parts.path.rstrip('/')}"


def load_seen(
    *,
    feed_dir: Path,
    evidence_dir: Path,
    x_source: str,
    exclude_evidence_id: str,
    now: datetime,
) -> list[SeenItem]:
    seen: list[SeenItem] = []
    if feed_dir.exists():
        for path in feed_dir.glob("*.md"):
            parts = path.read_text().split("---", 2)
            if len(parts) != 3:
                continue
            data = yaml.safe_load(parts[1]) or {}
            when = data.get("detected_at")
            if not isinstance(when, datetime) or now - when > _FEED_LOOKBACK:
                continue
            if exclude_evidence_id in (data.get("evidence_ids") or []):
                continue
            seen.append(
                SeenItem(
                    ref=f"feed:{data.get('slug', path.stem)}",
                    title=str(data.get("title", "")),
                    origin=str(data.get("source", "")),
                    when=when,
                    urls=frozenset(
                        normalize_url(url) for url in data.get("source_urls") or []
                    ),
                )
            )
    x_dir = evidence_dir / x_source
    if x_dir.exists():
        for path in x_dir.glob("*.json"):
            record = load_evidence(path)
            if record.evidence_id == exclude_evidence_id:
                continue
            if record.stage not in {EvidenceStage.ANALYZED, EvidenceStage.PUBLISHED}:
                continue
            if now - record.detected_at > _X_LOOKBACK:
                continue
            seen.append(
                SeenItem(
                    ref=f"x:{record.evidence_id}",
                    title=record.title or "",
                    origin=f"X @{record.discovery_metadata.get('author_handle', '')}",
                    when=record.detected_at,
                    urls=frozenset(
                        normalize_url(url) for url in _record_urls(record)
                    ),
                )
            )
    seen.sort(key=lambda item: item.when, reverse=True)
    return seen[:_MAX_SEEN]


def _record_urls(record: EvidenceRecord) -> list[str]:
    # The post URL is unique per post; only linked articles identify a story.
    return list(record.supporting_urls)


async def screen_x_candidate(
    record: EvidenceRecord,
    *,
    seen: list[SeenItem],
    model: StructuredModel | None,
    now: datetime,
) -> NoveltyDecision:
    published = record.published_at or record.detected_at
    if now - published > MAX_AGE:
        return NoveltyDecision("stale", f"posted more than {MAX_AGE} before screening")
    urls = {normalize_url(url) for url in _record_urls(record)}
    for item in seen:
        shared = urls & item.urls
        if shared:
            outcome = "duplicate" if item.ref.startswith("x:") else "covered"
            return NoveltyDecision(
                outcome, f"links the same page as {item.origin}", matched=item.ref
            )
    if model is None or not seen:
        return NoveltyDecision("new", "no overlapping item found")
    listing = "\n".join(
        f"- ref={item.ref} | {item.when.date().isoformat()} | {item.origin} | {item.title}"
        for item in seen
    )
    verdict = await model.generate(
        response_model=NoveltyVerdict,
        system_instruction=_NOVELTY_PROMPT,
        prompt=(
            f"Candidate:\nTitle: {record.title}\n{record.content}\n\n"
            f"Items already seen:\n{listing}"
        ),
    )
    if verdict.is_new:
        return NoveltyDecision("new", verdict.reason)
    matched = verdict.matched_ref
    outcome = "duplicate" if matched and matched.startswith("x:") else "covered"
    return NoveltyDecision(outcome, verdict.reason, matched=matched)
