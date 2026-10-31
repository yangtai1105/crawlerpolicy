"""Read vendor articles that refuse declared crawlers, through Google's index.

akamai.com and humansecurity.com answer every automated request with a block
page, but both let search engines index their blogs. Gemini with Google
Search grounding reads that index, so an article can be analysed without
fetching it, spoofing a browser, or retrying around a block.

Two rules keep this honest:

- A URL is trusted only when it comes from a grounding citation, resolved to
  its real address. URLs Gemini writes in its answer text are frequently
  invented, and the same article came back under two different made-up paths
  in successive calls.
- A read counts only if one of its citations is the article itself: same
  host and same final path segment. Akamai's index drops the /2026/oct/ part
  of its feed URLs, so a full-path match would miss them.

The notes are model input and, like linked X articles, are never written to
this public repository; evidence keeps only metadata about the read.
"""
from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urlsplit

import httpx
from google import genai
from google.genai import types as gt

from pipeline.model_provider import classify_provider_failure

MAX_CHARS = 15_000
_MIN_CHARS = 400
_NOT_FOUND = "NOT_FOUND"
_REDIRECT_TIMEOUT = httpx.Timeout(10.0)
_HEADER = re.compile(r"^\s*(TITLE|DATE):\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


class NotIndexed(LookupError):
    """The article is not (yet) readable through the search index."""


@dataclass(frozen=True)
class GroundedRead:
    url: str
    title: str
    published_on: datetime | None
    text: str
    cited_urls: list[str]
    model: str

    def as_metadata(self) -> dict[str, object]:
        return {
            "url": self.url,
            "method": "gemini-grounded",
            "model": self.model,
            "chars": len(self.text),
            "sha256": hashlib.sha256(self.text.encode()).hexdigest(),
            "cited_urls": self.cited_urls,
        }


def host(url: str) -> str:
    return urlsplit(url).netloc.lower().removeprefix("www.")


def _slug(url: str) -> str:
    segments = [segment for segment in urlsplit(url).path.split("/") if segment]
    return segments[-1].lower() if segments else ""


def same_article(left: str, right: str) -> bool:
    """True when two URLs name one article: same host, same final path segment."""
    return bool(_slug(left)) and host(left) == host(right) and _slug(left) == _slug(right)


def is_article_url(url: str, domain: str) -> bool:
    """A cited page on `domain` whose last segment looks like an article slug."""
    return host(url) == host(f"https://{domain}") and "-" in _slug(url)


def default_model() -> str:
    return os.environ.get("GEMINI_ANALYSIS_MODEL", "gemini-3.8-flash")


def _client(client: genai.Client | None) -> genai.Client:
    if client is not None:
        return client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set; cannot read through grounded search")
    return genai.Client(api_key=api_key)


async def _resolve(http: httpx.AsyncClient, uri: str) -> str | None:
    """Turn a grounding redirect into the real URL without fetching the target."""
    try:
        response = await http.get(uri)
    except httpx.HTTPError:
        return None
    location = response.headers.get("location")
    if location:
        return location
    return None if "vertexaisearch" in host(uri) else uri


async def grounded_search(
    prompt: str,
    *,
    model: str,
    client: genai.Client | None = None,
    http: httpx.AsyncClient | None = None,
) -> tuple[str, list[str]]:
    """Run one grounded call; return its text and resolved citation URLs."""
    try:
        response = await _client(client).aio.models.generate_content(
            model=model,
            contents=prompt,
            config=gt.GenerateContentConfig(
                tools=[gt.Tool(google_search=gt.GoogleSearch())],
                temperature=0.1,
            ),
        )
    except Exception as error:
        raise classify_provider_failure(error) from error
    candidates = getattr(response, "candidates", None) or []
    meta = getattr(candidates[0], "grounding_metadata", None) if candidates else None
    uris = [
        chunk.web.uri
        for chunk in (getattr(meta, "grounding_chunks", None) or [])
        if getattr(chunk, "web", None) is not None and chunk.web.uri
    ]
    owns_http = http is None
    active = http or httpx.AsyncClient(timeout=_REDIRECT_TIMEOUT, follow_redirects=False)
    try:
        resolved = [await _resolve(active, uri) for uri in dict.fromkeys(uris)]
    finally:
        if owns_http:
            await active.aclose()
    return (response.text or "").strip(), list(dict.fromkeys(url for url in resolved if url))


def _split_header(text: str) -> tuple[str, datetime | None, str]:
    title, published = "", None
    for match in _HEADER.finditer(text[:600]):
        key, value = match.group(1).upper(), match.group(2).strip("*` ")
        if key == "TITLE":
            title = value
        else:
            try:
                published = datetime.strptime(value[:10], "%Y-%m-%d").replace(tzinfo=UTC)
            except ValueError:
                published = None
    body = _HEADER.sub("", text, count=2).strip()
    return title, published, body


_cache: dict[str, GroundedRead] = {}


async def read_article(
    url: str,
    *,
    title: str = "",
    model: str | None = None,
    client: genai.Client | None = None,
    http: httpx.AsyncClient | None = None,
) -> GroundedRead:
    """Read one article from the search index, or raise NotIndexed."""
    if url in _cache:
        return _cache[url]
    model = model or default_model()
    named = f'"{title}" ({url})' if title else url
    prompt = (
        f"Search the web for the article {named} and read it.\n"
        "Start your answer with two lines:\n"
        "TITLE: <the article's exact headline>\n"
        "DATE: <its publication date as YYYY-MM-DD, or unknown>\n"
        "Then write detailed notes on what the article itself says: its main claims, "
        "every figure and statistic, named products, companies, AI agents and crawlers, "
        "and direct quotes with who said them. Report only what the article says; do not "
        "add background from other pages.\n"
        f"If you cannot find the article itself, reply exactly {_NOT_FOUND}."
    )
    text, cited = await grounded_search(prompt, model=model, client=client, http=http)
    if not text or text.startswith(_NOT_FOUND):
        raise NotIndexed(f"{url}: article not found in the search index")
    matching = [candidate for candidate in cited if same_article(candidate, url)]
    if not matching:
        raise NotIndexed(f"{url}: no grounding citation of the article itself")
    found_title, published, notes = _split_header(text)
    if len(notes) < _MIN_CHARS:
        raise NotIndexed(f"{url}: grounded notes too short ({len(notes)} chars)")
    read = GroundedRead(
        url=matching[0],
        title=found_title or title,
        published_on=published,
        text=notes[:MAX_CHARS],
        cited_urls=cited,
        model=model,
    )
    _cache[url] = read
    return read


def article_context(read: GroundedRead) -> str:
    return (
        f"=== ARTICLE NOTES (read via search index, {host(read.url)}) ===\n"
        f"Title: {read.title}\n{read.text}"
    )


async def discover_articles(
    domain: str,
    query: str,
    *,
    lookback_days: int,
    model: str | None = None,
    client: genai.Client | None = None,
    http: httpx.AsyncClient | None = None,
) -> list[str]:
    """Return cited article URLs on `domain` that a listing query surfaced."""
    prompt = (
        f"Search the web for {query} published on {domain} in the last "
        f"{lookback_days} days. For each one give its title, date and a one-line "
        f"summary. Only include pages you actually found on {domain}. "
        "If there are none, reply NONE."
    )
    _text, cited = await grounded_search(
        prompt, model=model or default_model(), client=client, http=http
    )
    unique: list[str] = []
    for url in cited:
        if is_article_url(url, domain) and not any(same_article(url, kept) for kept in unique):
            unique.append(url)
    return unique
