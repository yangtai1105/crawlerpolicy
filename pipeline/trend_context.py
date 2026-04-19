"""Load recent historical events for a source so the analyzer can reason
about trends ("third major settlement this week", "second time this vendor
shipped an AI-crawler feature in a month", etc.) rather than treating each
item in isolation.

For ecosystem + agent pillars, this is a meaningful quality lift — news
items land in patterns, and readers care about the pattern as much as the
single item. For crawler pillar, events are rare enough that ambient trend
context isn't as useful.
"""
from __future__ import annotations

import re
from pathlib import Path

# Parse the minimal frontmatter fields we need without pulling in yaml.
_SLUG_RX = re.compile(r"^slug:\s*(\S+)\s*$", re.MULTILINE)
_TITLE_RX = re.compile(r'^title:\s*"?(.+?)"?\s*$', re.MULTILINE)
_SOURCE_RX = re.compile(r"^source:\s*(\S+)\s*$", re.MULTILINE)
_DETECTED_RX = re.compile(r"^detected_at:\s*(\S+)\s*$", re.MULTILINE)
_IMPORTANCE_RX = re.compile(r"^importance:\s*([0-9.]+)\s*$", re.MULTILINE)
_IMPL_RX = re.compile(r"## Implication\s*\n+(.+?)(?=\n## |\Z)", re.DOTALL)


def load_recent_events_for_source(
    events_dir: Path, source_slug: str, limit: int = 10
) -> list[dict]:
    """Return up to `limit` most recent events from the given source, newest first.

    Each event is a dict of {slug, title, source, detected_at, importance, implication}.
    Reads directly from markdown to avoid a full yaml dependency at this layer.
    """
    if not events_dir.exists():
        return []
    # Files are named {YYYY-MM-DD}-{source}-{slug}.md — prefix match on source.
    candidates = sorted(
        events_dir.glob(f"*-{source_slug}-*.md"),
        key=lambda p: p.name,
        reverse=True,
    )
    events: list[dict] = []
    for path in candidates[: limit * 2]:  # read a few extra in case of parse fails
        text = path.read_text()
        # Only keep events whose source field matches exactly (guard against
        # false-positive prefix matches like source=gemini-agent vs gemini-agent-infra).
        m_source = _SOURCE_RX.search(text)
        if not m_source or m_source.group(1) != source_slug:
            continue
        m_title = _TITLE_RX.search(text)
        m_detected = _DETECTED_RX.search(text)
        m_importance = _IMPORTANCE_RX.search(text)
        m_impl = _IMPL_RX.search(text)
        if not (m_title and m_detected):
            continue
        events.append(
            {
                "title": m_title.group(1),
                "detected_at": m_detected.group(1),
                "importance": float(m_importance.group(1)) if m_importance else 0.0,
                "implication": (m_impl.group(1).strip() if m_impl else "")[:400],
            }
        )
        if len(events) >= limit:
            break
    return events


def format_trend_context(events: list[dict]) -> str:
    """Render a compact block the analyzer can reference in prompts."""
    if not events:
        return ""
    lines = [
        "RECENT ITEMS FROM THIS SAME SOURCE (newest first — use to place the "
        "new item in context; note any patterns, continuations, or reversals):"
    ]
    for e in events:
        date = e["detected_at"][:10]
        lines.append(f"- [{date}] {e['title']} (importance {e['importance']:.2f})")
        if e["implication"]:
            lines.append(f"  prior implication: {e['implication']}")
    return "\n".join(lines)
