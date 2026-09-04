"""Official xAI X Search adapter returning validated per-post candidates."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from pydantic import AnyHttpUrl, BaseModel, Field, ValidationError, field_validator

from pipeline.fetchers.base import CandidateItem, FetchResult, ResultMode
from pipeline.sources import Source

_RESPONSES_URL = "https://api.x.ai/v1/responses"
_TOOL_COST_USD = 0.005


class XSearchCandidate(BaseModel):
    """One post selected by the xAI discovery model."""

    post_id: str = Field(min_length=1)
    post_url: AnyHttpUrl
    author_handle: str = Field(min_length=1)
    published_at: datetime
    title: str = Field(min_length=1)
    synopsis: str = Field(min_length=1)
    linked_urls: list[AnyHttpUrl] = Field(default_factory=list)

    @field_validator("post_url")
    @classmethod
    def _post_must_be_https_x(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        if value.scheme != "https" or value.host not in {"x.com", "www.x.com"}:
            raise ValueError("post_url must be an HTTPS x.com URL")
        return value

    @field_validator("linked_urls")
    @classmethod
    def _links_must_be_https(cls, values: list[AnyHttpUrl]) -> list[AnyHttpUrl]:
        if any(value.scheme != "https" for value in values):
            raise ValueError("linked_urls must use HTTPS")
        return values

    @field_validator("published_at")
    @classmethod
    def _published_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("published_at must include a timezone")
        return value.astimezone(UTC)


class XSearchEnvelope(BaseModel):
    candidates: list[XSearchCandidate] = Field(default_factory=list)


def build_x_search_payload(
    source: Source,
    model: str,
    window_start: datetime,
    window_end: datetime,
) -> dict[str, Any]:
    tool: dict[str, Any] = {
        "type": "x_search",
        "from_date": window_start.date().isoformat(),
        "to_date": window_end.date().isoformat(),
    }
    if source.x_handles:
        tool["allowed_x_handles"] = source.x_handles
    prompt = (
        f"{source.query}\n\n"
        f"Use only posts published from {window_start.isoformat()} through "
        f"{window_end.isoformat()}. Return only consequential, factual items within "
        "the requested web-ecosystem scope. Exclude reposts, reactions, generic AI news, "
        "unsupported predictions, and duplicate claims. Return one JSON object with a "
        "candidates array. Every candidate must contain post_id, post_url, author_handle, "
        "published_at, title, synopsis, and linked_urls. Use [] when there are no candidates."
    )
    return {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
        "tools": [tool],
        "max_turns": 2,
    }


def parse_x_search_envelope(response: dict[str, Any]) -> XSearchEnvelope:
    text = _response_text(response).strip()
    if text.startswith("```json") and text.endswith("```"):
        text = text[7:-3].strip()
    elif text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()
    try:
        return XSearchEnvelope.model_validate_json(text)
    except (ValidationError, ValueError) as error:
        raise ValueError("xAI X Search did not return valid candidate JSON") from error


def _response_text(response: dict[str, Any]) -> str:
    fragments: list[str] = []
    for output in response.get("output", []):
        if not isinstance(output, dict) or output.get("type") != "message":
            continue
        for content in output.get("content", []):
            if not isinstance(content, dict):
                continue
            if content.get("type") in {"output_text", "text"}:
                fragments.append(str(content.get("text", "")))
    return "".join(fragments)


def _candidates_to_items(
    candidates: list[XSearchCandidate],
    *,
    window_start: datetime,
    window_end: datetime,
    citations: list[str],
) -> list[CandidateItem]:
    seen: set[str] = set()
    items: list[CandidateItem] = []
    for candidate in candidates:
        if candidate.post_id in seen:
            continue
        if not window_start <= candidate.published_at <= window_end:
            continue
        seen.add(candidate.post_id)
        post_url = str(candidate.post_url)
        linked_urls = [str(url) for url in candidate.linked_urls]
        source_lines = "\n".join(f"- {url}" for url in linked_urls)
        body = (
            f"X author: @{candidate.author_handle.lstrip('@')}\n\n"
            f"{candidate.synopsis}\n\n"
            f"Linked sources:\n{source_lines if source_lines else '- None supplied'}"
        )
        items.append(
            CandidateItem(
                guid=candidate.post_id,
                title=candidate.title.strip(),
                published_at=candidate.published_at,
                url=post_url,
                summary=candidate.synopsis.strip(),
                body=body,
                metadata={
                    "author_handle": candidate.author_handle.lstrip("@"),
                    "post_url": post_url,
                    "linked_urls": linked_urls,
                    "provider_citations": list(dict.fromkeys(citations)),
                },
            )
        )
    return items


async def fetch_xai_search(
    source: Source,
    *,
    api_key: str,
    model: str,
    now: datetime,
    client: httpx.AsyncClient | None = None,
) -> FetchResult:
    """Run one bounded xAI X Search request for a configured discovery source."""
    if not api_key.strip():
        raise RuntimeError("XAI_API_KEY not set; cannot run xai_search source")
    window_end = now.astimezone(UTC)
    window_start = window_end - timedelta(hours=source.lookback_hours)
    payload = build_x_search_payload(source, model, window_start, window_end)

    owns_client = client is None
    active_client = client or httpx.AsyncClient(timeout=httpx.Timeout(45.0))
    try:
        response = await active_client.post(
            _RESPONSES_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        )
        response.raise_for_status()
        raw = response.json()
    finally:
        if owns_client:
            await active_client.aclose()

    envelope = parse_x_search_envelope(raw)
    citations = [
        value
        for value in raw.get("citations", [])
        if isinstance(value, str) and value.startswith("https://")
    ]
    items = _candidates_to_items(
        envelope.candidates,
        window_start=window_start,
        window_end=window_end,
        citations=citations,
    )
    usage = raw.get("server_side_tool_usage", {})
    calls = int(usage.get("SERVER_SIDE_TOOL_X_SEARCH", 0))
    return FetchResult(
        mode=ResultMode.PER_ITEM,
        items=items,
        metadata={
            "x_search_calls": calls,
            "estimated_tool_cost_usd": round(calls * _TOOL_COST_USD, 6),
            "model": model,
            "usage": raw.get("usage", {}),
        },
    )
