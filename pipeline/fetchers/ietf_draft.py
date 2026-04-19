"""IETF draft fetcher via datatracker metadata + archived plaintext."""
from __future__ import annotations

import httpx

from pipeline.fetchers.base import FetchResult, ResultMode
from pipeline.sources import Source

_UA = "ai-ecosystem-tracker/0.1"
_TIMEOUT = httpx.Timeout(30.0)


async def fetch_ietf_draft(source: Source) -> FetchResult:
    meta_url = (
        f"https://datatracker.ietf.org/api/v1/doc/document/{source.draft_name}/?format=json"
    )
    async with httpx.AsyncClient(
        headers={"User-Agent": _UA}, timeout=_TIMEOUT, follow_redirects=True
    ) as client:
        meta = await client.get(meta_url)
        meta.raise_for_status()
        rev = meta.json()["rev"]
        txt_url = f"https://www.ietf.org/archive/id/{source.draft_name}-{rev}.txt"
        body = await client.get(txt_url)
        body.raise_for_status()

    return FetchResult(mode=ResultMode.DIFFABLE, normalized_content=body.text, raw_ext="txt")
