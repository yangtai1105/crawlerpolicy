# Plan 1: Pipeline + GitHub Actions — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Python pipeline that fetches 28 AI-ecosystem sources daily, detects material changes, generates LLM analysis, writes event markdown + snapshot + State-of-Play JSON files, and commits them back to the repo via a GitHub Actions cron. This plan delivers a working end-to-end pipeline whose output is ready to be consumed by the static site (Plan 2) and distribution (Plan 3).

**Architecture:** Git-as-DB: the scheduled pipeline runs once per day on GitHub Actions, reads `sources.yaml`, dispatches per-source-type fetchers, applies a two-stage relevance funnel (regex keyword filter + Claude Haiku classifier), hashes/diffs content, calls Claude Sonnet for analysis, writes one markdown file per material event, regenerates State-of-Play JSON aggregates, and commits everything to `main`. The site (Plan 2) auto-rebuilds on each commit.

**Tech Stack:** Python 3.12, `uv` package manager, `httpx` (async HTTP), `feedparser` (RSS), `readability-lxml` + `beautifulsoup4` (HTML normalization), `anthropic` SDK (Claude API), `PyYAML` (config), `pydantic` (schema validation), `pytest` + `pytest-asyncio` + `respx` (testing), `ruff` (lint/format). GitHub Actions for cron.

---

## File Structure

```
ai-ecosystem-tracker/
├── sources.yaml                         # 28 v1 sources
├── pyproject.toml                       # uv project config + deps
├── .python-version                      # 3.12
├── .env.example                         # ANTHROPIC_API_KEY, ALERT_EMAILS, etc.
├── .gitignore
├── .github/workflows/
│   └── daily-check.yml                  # cron
├── content/
│   ├── snapshots/                       # {source_slug}/{YYYY-MM-DD}.{ext}
│   └── events/                          # {YYYY-MM-DD}-{slug}.md
├── data/
│   ├── opt-out-matrix.json              # SoP aggregate
│   ├── policy-fronts.json
│   ├── agent-standards.json
│   └── health.json                      # last-run status per source
├── state/
│   └── {source_slug}.json               # last_checked_at, last_seen_guid, last_hash
├── pipeline/
│   ├── __init__.py
│   ├── config.py                        # env + paths + constants
│   ├── sources.py                       # Source dataclass + YAML loader
│   ├── state.py                         # read/write state/*.json
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── base.py                      # FetcherResult type
│   │   ├── html_page.py
│   │   ├── rss_feed.py
│   │   ├── github_repo.py
│   │   └── ietf_draft.py
│   ├── differ.py                        # HTML → markdown → line diff
│   ├── relevance.py                     # keyword + Haiku funnel
│   ├── analyzer.py                      # Sonnet structured analysis
│   ├── event_writer.py                  # markdown frontmatter writer
│   ├── state_of_play.py                 # Haiku extractor + data/*.json
│   ├── check.py                         # daily cron entrypoint
│   └── git_ops.py                       # subprocess wrapper for git commit
└── tests/
    ├── conftest.py
    ├── test_sources.py
    ├── test_state.py
    ├── test_fetchers/
    │   ├── test_html_page.py
    │   ├── test_rss_feed.py
    │   ├── test_github_repo.py
    │   └── test_ietf_draft.py
    ├── test_differ.py
    ├── test_relevance.py
    ├── test_analyzer.py
    ├── test_event_writer.py
    ├── test_state_of_play.py
    └── test_check.py                    # end-to-end integration
```

---

## Phase 0: Repo & Tooling Bootstrap

### Task 0.1: Initialize git repo and create directory scaffolding

**Files:**
- Create: `/Users/jasonyang/Documents/Claude/Skills/ai-ecosystem-tracker/.gitignore`
- Create: `/Users/jasonyang/Documents/Claude/Skills/ai-ecosystem-tracker/README.md`

- [ ] **Step 1: Initialize git repo in the project directory**

```bash
cd /Users/jasonyang/Documents/Claude/Skills/ai-ecosystem-tracker
git init
git branch -M main
```

- [ ] **Step 2: Create `.gitignore`**

Write `.gitignore`:
```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/

# Node / Astro (Plan 2)
node_modules/
dist/
.astro/

# Env
.env
.env.local
.env.*.local

# OS
.DS_Store

# Brainstorm artifacts (keep out of prod commits)
.superpowers/
```

- [ ] **Step 3: Create minimal `README.md`**

Write `README.md`:
```markdown
# AI Ecosystem Tracker

Automated tracker for AI crawler documentation, content-ecosystem news, and AI agent infrastructure. Site at TBD. See `docs/superpowers/specs/` for design.

## Repo layout

- `pipeline/` — Python scraping + LLM pipeline (runs on GitHub Actions daily)
- `content/` — events (markdown) and snapshots (git-versioned history)
- `data/` — State of Play JSON aggregates
- `sources.yaml` — tracked-source configuration
- `site/` — Astro static site (Plan 2)
- `api/` — Vercel serverless functions for subscriptions (Plan 3)

## Dev

```
uv sync
uv run pytest
uv run python -m pipeline.check --dry-run
```
```

- [ ] **Step 4: Create empty directory structure with `.gitkeep` placeholders**

```bash
mkdir -p content/snapshots content/events data state \
  pipeline/fetchers tests/test_fetchers \
  .github/workflows
touch content/snapshots/.gitkeep content/events/.gitkeep \
  data/.gitkeep state/.gitkeep \
  pipeline/__init__.py pipeline/fetchers/__init__.py \
  tests/__init__.py tests/test_fetchers/__init__.py
```

- [ ] **Step 5: Initial commit**

```bash
git add .gitignore README.md content/ data/ state/ pipeline/ tests/ .github/ docs/
git commit -m "chore: initialize repo scaffolding + import design spec and plan"
```

Expected: commit succeeds. The existing `docs/superpowers/specs/2026-04-18-ai-ecosystem-tracker-design.md` and `docs/superpowers/plans/2026-04-18-plan-1-pipeline.md` are included.

---

### Task 0.2: Python environment with `uv` and `pyproject.toml`

**Files:**
- Create: `.python-version`
- Create: `pyproject.toml`

- [ ] **Step 1: Pin Python version**

Write `.python-version`:
```
3.12
```

- [ ] **Step 2: Create `pyproject.toml`**

Write `pyproject.toml`:
```toml
[project]
name = "ai-ecosystem-tracker"
version = "0.1.0"
description = "Automated tracker for AI crawler docs, content ecosystem, and agent infrastructure."
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27",
    "feedparser>=6.0",
    "readability-lxml>=0.8.1",
    "beautifulsoup4>=4.12",
    "lxml>=5.2",
    "anthropic>=0.40",
    "pyyaml>=6.0",
    "pydantic>=2.7",
    "python-dotenv>=1.0",
    "jinja2>=3.1",
]

[dependency-groups]
dev = [
    "pytest>=8.2",
    "pytest-asyncio>=0.23",
    "respx>=0.21",
    "ruff>=0.5",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

- [ ] **Step 3: Initialize the uv environment**

```bash
uv sync
```

Expected: creates `.venv/` and `uv.lock`.

- [ ] **Step 4: Sanity-check Python and pytest work**

```bash
uv run python --version
uv run pytest --version
```

Expected: Python 3.12.x, pytest 8.x.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock .python-version
git commit -m "chore: add uv + pyproject.toml with pipeline dependencies"
```

---

### Task 0.3: Config module (env + paths)

**Files:**
- Create: `pipeline/config.py`
- Create: `.env.example`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

Write `tests/test_config.py`:
```python
from pathlib import Path

from pipeline.config import Config


def test_config_paths_resolve_relative_to_repo_root(tmp_path, monkeypatch):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    cfg = Config.from_env()
    assert cfg.repo_root == tmp_path
    assert cfg.snapshots_dir == tmp_path / "content" / "snapshots"
    assert cfg.events_dir == tmp_path / "content" / "events"
    assert cfg.data_dir == tmp_path / "data"
    assert cfg.state_dir == tmp_path / "state"
    assert cfg.sources_yaml == tmp_path / "sources.yaml"


def test_config_reads_required_env(monkeypatch, tmp_path):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("ALERT_EMAILS", "a@x.com,b@x.com")
    cfg = Config.from_env()
    assert cfg.anthropic_api_key == "sk-ant-test"
    assert cfg.alert_emails == ["a@x.com", "b@x.com"]
```

- [ ] **Step 2: Run test and watch it fail**

```bash
uv run pytest tests/test_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'pipeline.config'`.

- [ ] **Step 3: Implement `pipeline/config.py`**

Write `pipeline/config.py`:
```python
"""Runtime configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Config:
    repo_root: Path
    anthropic_api_key: str
    alert_emails: list[str] = field(default_factory=list)

    @property
    def snapshots_dir(self) -> Path:
        return self.repo_root / "content" / "snapshots"

    @property
    def events_dir(self) -> Path:
        return self.repo_root / "content" / "events"

    @property
    def data_dir(self) -> Path:
        return self.repo_root / "data"

    @property
    def state_dir(self) -> Path:
        return self.repo_root / "state"

    @property
    def sources_yaml(self) -> Path:
        return self.repo_root / "sources.yaml"

    @classmethod
    def from_env(cls) -> "Config":
        repo_root_raw = os.environ.get("REPO_ROOT")
        if not repo_root_raw:
            # Default: two levels up from this file (pipeline/config.py → repo root)
            repo_root_raw = str(Path(__file__).resolve().parent.parent)
        emails_raw = os.environ.get("ALERT_EMAILS", "")
        emails = [e.strip() for e in emails_raw.split(",") if e.strip()]
        return cls(
            repo_root=Path(repo_root_raw).resolve(),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            alert_emails=emails,
        )
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_config.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Create `.env.example`**

Write `.env.example`:
```
# Required at runtime (set these in GitHub Actions secrets + Vercel env)
ANTHROPIC_API_KEY=sk-ant-...

# Comma-separated internal addresses that receive immediate crawler alerts
ALERT_EMAILS=alice@example.com,bob@example.com

# Plan 3 additions
RESEND_API_KEY=re_...
KV_REST_API_URL=https://...
KV_REST_API_TOKEN=...
SITE_URL=https://tracker.example.com
```

- [ ] **Step 6: Commit**

```bash
git add pipeline/config.py tests/test_config.py .env.example
git commit -m "feat(pipeline): add Config module and .env.example"
```

---

## Phase 1: sources.yaml loader + state management

### Task 1.1: Source dataclass schema

**Files:**
- Create: `pipeline/sources.py`
- Create: `tests/test_sources.py`

- [ ] **Step 1: Write the failing test**

Write `tests/test_sources.py`:
```python
import pytest
from pydantic import ValidationError

from pipeline.sources import Source, SourceType, Pillar, load_sources


def test_html_page_source_minimum_fields():
    s = Source(
        slug="gptbot",
        pillar=Pillar.CRAWLER,
        type=SourceType.HTML_PAGE,
        url="https://platform.openai.com/docs/gptbot",
        display_name="OpenAI GPTBot",
    )
    assert s.slug == "gptbot"
    assert s.pillar == Pillar.CRAWLER


def test_rss_feed_requires_keyword_filter():
    with pytest.raises(ValidationError):
        Source(
            slug="cloudflare-blog",
            pillar=Pillar.ECOSYSTEM,
            type=SourceType.RSS_FEED,
            url="https://blog.cloudflare.com/rss/",
            display_name="Cloudflare Blog",
            # missing keyword_filter
        )


def test_github_repo_requires_repo_field():
    with pytest.raises(ValidationError):
        Source(
            slug="mcp",
            pillar=Pillar.AGENT,
            type=SourceType.GITHUB_REPO,
            display_name="MCP",
            # missing repo
        )


def test_ietf_draft_requires_draft_name():
    with pytest.raises(ValidationError):
        Source(
            slug="wba",
            pillar=Pillar.AGENT,
            type=SourceType.IETF_DRAFT,
            display_name="Web Bot Auth",
            # missing draft_name
        )


def test_load_sources_from_yaml(tmp_path):
    yaml_text = """
- slug: gptbot
  pillar: crawler
  type: html_page
  url: https://platform.openai.com/docs/gptbot
  display_name: OpenAI GPTBot
- slug: cloudflare-blog
  pillar: ecosystem
  type: rss_feed
  url: https://blog.cloudflare.com/rss/
  keyword_filter: ["AI bot", "crawler"]
  display_name: Cloudflare Blog
"""
    p = tmp_path / "sources.yaml"
    p.write_text(yaml_text)
    sources = load_sources(p)
    assert len(sources) == 2
    assert sources[0].slug == "gptbot"
    assert sources[1].keyword_filter == ["AI bot", "crawler"]


def test_load_sources_rejects_duplicate_slugs(tmp_path):
    yaml_text = """
- slug: dup
  pillar: crawler
  type: html_page
  url: https://a.example
  display_name: A
- slug: dup
  pillar: crawler
  type: html_page
  url: https://b.example
  display_name: B
"""
    p = tmp_path / "sources.yaml"
    p.write_text(yaml_text)
    with pytest.raises(ValueError, match="duplicate slug"):
        load_sources(p)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_sources.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `pipeline/sources.py`**

Write `pipeline/sources.py`:
```python
"""Source configuration schema and loader."""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, Field, model_validator


class Pillar(str, Enum):
    CRAWLER = "crawler"
    ECOSYSTEM = "ecosystem"
    AGENT = "agent"


class SourceType(str, Enum):
    HTML_PAGE = "html_page"
    RSS_FEED = "rss_feed"
    GITHUB_REPO = "github_repo"
    IETF_DRAFT = "ietf_draft"


class Source(BaseModel):
    slug: str
    pillar: Pillar
    type: SourceType
    display_name: str

    # html_page + rss_feed
    url: str | None = None
    content_selector: str | None = None

    # rss_feed
    keyword_filter: list[str] | None = None

    # github_repo
    repo: str | None = None
    pr_labels: list[str] = Field(default_factory=list)
    pr_path_globs: list[str] = Field(default_factory=list)

    # ietf_draft
    draft_name: str | None = None

    # Optional Sonnet/Opus override per source
    model: str | None = None

    @model_validator(mode="after")
    def _validate_type_requirements(self) -> Self:
        if self.type in (SourceType.HTML_PAGE, SourceType.RSS_FEED) and not self.url:
            raise ValueError(f"source {self.slug}: {self.type} requires `url`")
        if self.type == SourceType.RSS_FEED and not self.keyword_filter:
            raise ValueError(f"source {self.slug}: rss_feed requires `keyword_filter`")
        if self.type == SourceType.GITHUB_REPO and not self.repo:
            raise ValueError(f"source {self.slug}: github_repo requires `repo`")
        if self.type == SourceType.IETF_DRAFT and not self.draft_name:
            raise ValueError(f"source {self.slug}: ietf_draft requires `draft_name`")
        return self


def load_sources(yaml_path: Path) -> list[Source]:
    raw = yaml.safe_load(yaml_path.read_text())
    if not isinstance(raw, list):
        raise ValueError(f"{yaml_path} must be a YAML list")
    sources = [Source.model_validate(item) for item in raw]
    seen: set[str] = set()
    for s in sources:
        if s.slug in seen:
            raise ValueError(f"duplicate slug: {s.slug}")
        seen.add(s.slug)
    return sources
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_sources.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add pipeline/sources.py tests/test_sources.py
git commit -m "feat(pipeline): add Source schema and YAML loader"
```

---

### Task 1.2: Per-source state management

**Files:**
- Create: `pipeline/state.py`
- Create: `tests/test_state.py`

- [ ] **Step 1: Write the failing test**

Write `tests/test_state.py`:
```python
from datetime import datetime, timezone

from pipeline.state import SourceState, load_state, save_state


def test_new_source_returns_empty_state(tmp_path):
    state = load_state(tmp_path, "newsource")
    assert state.last_checked_at is None
    assert state.last_hash is None
    assert state.last_seen_guids == []
    assert state.consecutive_failures == 0


def test_round_trip_state(tmp_path):
    t = datetime(2026, 4, 18, 12, 0, 0, tzinfo=timezone.utc)
    state = SourceState(
        last_checked_at=t,
        last_hash="abc123",
        last_seen_guids=["g1", "g2"],
        consecutive_failures=0,
    )
    save_state(tmp_path, "gptbot", state)
    loaded = load_state(tmp_path, "gptbot")
    assert loaded.last_checked_at == t
    assert loaded.last_hash == "abc123"
    assert loaded.last_seen_guids == ["g1", "g2"]


def test_state_file_written_atomically(tmp_path):
    state = SourceState(last_hash="v1")
    save_state(tmp_path, "gptbot", state)
    # No .tmp left behind
    leftovers = list(tmp_path.glob("*.tmp"))
    assert leftovers == []
```

- [ ] **Step 2: Run test to watch it fail**

```bash
uv run pytest tests/test_state.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `pipeline/state.py`**

Write `pipeline/state.py`:
```python
"""Per-source state persistence under `state/{slug}.json`."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class SourceState:
    last_checked_at: datetime | None = None
    last_hash: str | None = None
    last_seen_guids: list[str] = field(default_factory=list)
    consecutive_failures: int = 0
    # first_seen flag: True before the source has ever been checked; check.py
    # uses this for catch-up mode (record state, emit no events on first run).
    first_seen: bool = True


def load_state(state_dir: Path, slug: str) -> SourceState:
    p = state_dir / f"{slug}.json"
    if not p.exists():
        return SourceState()
    raw = json.loads(p.read_text())
    if raw.get("last_checked_at"):
        raw["last_checked_at"] = datetime.fromisoformat(raw["last_checked_at"])
    return SourceState(**raw)


def save_state(state_dir: Path, slug: str, state: SourceState) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    p = state_dir / f"{slug}.json"
    tmp = p.with_suffix(".json.tmp")
    d = asdict(state)
    if d["last_checked_at"]:
        d["last_checked_at"] = d["last_checked_at"].isoformat()
    tmp.write_text(json.dumps(d, indent=2))
    os.replace(tmp, p)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/test_state.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pipeline/state.py tests/test_state.py
git commit -m "feat(pipeline): add per-source state persistence"
```

---

## Phase 2: Fetchers

### Task 2.1: `html_page` fetcher

**Files:**
- Create: `pipeline/fetchers/base.py`
- Create: `pipeline/fetchers/html_page.py`
- Create: `tests/test_fetchers/test_html_page.py`

- [ ] **Step 1: Define the base result type**

Write `pipeline/fetchers/base.py`:
```python
"""Fetcher contracts. Each fetcher implementation returns a FetchResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ResultMode(str, Enum):
    # html_page / ietf_draft: full content diffed against previous snapshot
    DIFFABLE = "diffable"
    # rss_feed / github_repo: list of candidate items, each potentially a separate event
    PER_ITEM = "per_item"


@dataclass
class CandidateItem:
    """One item from a per-item source (RSS post, GitHub release, etc.)."""
    guid: str                        # unique id within source (URL, release tag, PR number)
    title: str
    published_at: datetime | None
    url: str | None
    summary: str                     # short text for relevance filter
    body: str                        # full text for analyzer


@dataclass
class FetchResult:
    mode: ResultMode
    # DIFFABLE fields
    normalized_content: str | None = None
    raw_ext: str = "html"
    # PER_ITEM fields
    items: list[CandidateItem] = field(default_factory=list)
```

- [ ] **Step 2: Write the failing test for html_page**

Write `tests/test_fetchers/test_html_page.py`:
```python
import pytest
import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.html_page import fetch_html_page
from pipeline.sources import Pillar, Source, SourceType


@pytest.fixture
def html_source():
    return Source(
        slug="gptbot",
        pillar=Pillar.CRAWLER,
        type=SourceType.HTML_PAGE,
        url="https://platform.openai.com/docs/gptbot",
        display_name="OpenAI GPTBot",
    )


@respx.mock
async def test_fetches_and_normalizes_main_content(html_source):
    html = """
    <html><head><title>GPTBot</title>
    <script>var x=1;</script>
    </head>
    <body>
      <nav>site nav (should drop)</nav>
      <main>
        <article>
          <h1>GPTBot</h1>
          <p>GPTBot is OpenAI's web crawler.</p>
        </article>
      </main>
      <footer>footer junk</footer>
    </body></html>
    """
    respx.get(html_source.url).mock(return_value=Response(200, text=html))

    result = await fetch_html_page(html_source)

    assert result.mode == ResultMode.DIFFABLE
    assert "GPTBot is OpenAI's web crawler." in result.normalized_content
    assert "script" not in result.normalized_content.lower()
    assert "site nav" not in result.normalized_content
    assert "footer junk" not in result.normalized_content


@respx.mock
async def test_honors_content_selector(html_source):
    html_source_with_sel = html_source.model_copy(
        update={"content_selector": "#doc-body"}
    )
    html = """
    <html><body>
      <div id="doc-body">
        <p>canonical body</p>
      </div>
      <div class="sidebar">sidebar noise</div>
    </body></html>
    """
    respx.get(html_source_with_sel.url).mock(return_value=Response(200, text=html))

    result = await fetch_html_page(html_source_with_sel)

    assert "canonical body" in result.normalized_content
    assert "sidebar noise" not in result.normalized_content


@respx.mock
async def test_raises_on_http_error(html_source):
    respx.get(html_source.url).mock(return_value=Response(503))
    with pytest.raises(Exception, match="503"):
        await fetch_html_page(html_source)
```

- [ ] **Step 3: Run test to watch it fail**

```bash
uv run pytest tests/test_fetchers/test_html_page.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 4: Implement `fetch_html_page`**

Write `pipeline/fetchers/html_page.py`:
```python
"""HTML page fetcher. Normalizes page content for day-over-day diffing."""
from __future__ import annotations

import httpx
from bs4 import BeautifulSoup
from readability import Document

from pipeline.fetchers.base import FetchResult, ResultMode
from pipeline.sources import Source

_UA = "ai-ecosystem-tracker/0.1 (+https://github.com/yangtai1105/ai-ecosystem-tracker)"
_TIMEOUT = httpx.Timeout(30.0)


async def fetch_html_page(source: Source) -> FetchResult:
    async with httpx.AsyncClient(headers={"User-Agent": _UA}, timeout=_TIMEOUT, follow_redirects=True) as client:
        resp = await client.get(source.url)
        resp.raise_for_status()

    html = resp.text
    if source.content_selector:
        soup = BeautifulSoup(html, "lxml")
        node = soup.select_one(source.content_selector)
        if node is None:
            raise ValueError(f"selector {source.content_selector!r} matched nothing")
        text = _clean_text(node)
    else:
        doc = Document(html)
        article_html = doc.summary(html_partial=True)
        text = _clean_text(BeautifulSoup(article_html, "lxml"))

    return FetchResult(mode=ResultMode.DIFFABLE, normalized_content=text, raw_ext="html")


def _clean_text(node) -> str:
    """Strip scripts/styles and collapse whitespace to stable normalized text."""
    for tag in node.find_all(["script", "style", "noscript"]):
        tag.decompose()
    text = node.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_fetchers/test_html_page.py -v
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add pipeline/fetchers/base.py pipeline/fetchers/html_page.py tests/test_fetchers/test_html_page.py
git commit -m "feat(pipeline): html_page fetcher with readability + selector"
```

---

### Task 2.2: `rss_feed` fetcher

**Files:**
- Create: `pipeline/fetchers/rss_feed.py`
- Create: `tests/test_fetchers/test_rss_feed.py`

- [ ] **Step 1: Write the failing test**

Write `tests/test_fetchers/test_rss_feed.py`:
```python
from datetime import datetime, timezone

import pytest
import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.rss_feed import fetch_rss_feed
from pipeline.sources import Pillar, Source, SourceType

RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Example Blog</title>
<item>
<title>AI crawler update: new opt-out</title>
<link>https://example.com/posts/ai-crawler-opt-out</link>
<guid>https://example.com/posts/ai-crawler-opt-out</guid>
<pubDate>Wed, 18 Apr 2026 12:00:00 GMT</pubDate>
<description>We added a new AI bot opt-out flow.</description>
</item>
<item>
<title>Old post from last month</title>
<link>https://example.com/posts/old</link>
<guid>https://example.com/posts/old</guid>
<pubDate>Sat, 15 Mar 2026 00:00:00 GMT</pubDate>
<description>Something unrelated.</description>
</item>
</channel>
</rss>
"""


@pytest.fixture
def rss_source():
    return Source(
        slug="example",
        pillar=Pillar.ECOSYSTEM,
        type=SourceType.RSS_FEED,
        url="https://example.com/rss",
        display_name="Example",
        keyword_filter=["AI bot", "crawler"],
    )


@respx.mock
async def test_fetches_all_items_when_no_state(rss_source):
    respx.get(rss_source.url).mock(return_value=Response(200, text=RSS))

    result = await fetch_rss_feed(rss_source, since=None, seen_guids=[])

    assert result.mode == ResultMode.PER_ITEM
    assert len(result.items) == 2
    titles = {item.title for item in result.items}
    assert "AI crawler update: new opt-out" in titles


@respx.mock
async def test_excludes_items_older_than_since(rss_source):
    since = datetime(2026, 4, 1, tzinfo=timezone.utc)
    respx.get(rss_source.url).mock(return_value=Response(200, text=RSS))

    result = await fetch_rss_feed(rss_source, since=since, seen_guids=[])

    assert len(result.items) == 1
    assert result.items[0].title == "AI crawler update: new opt-out"


@respx.mock
async def test_excludes_seen_guids(rss_source):
    respx.get(rss_source.url).mock(return_value=Response(200, text=RSS))

    result = await fetch_rss_feed(
        rss_source,
        since=None,
        seen_guids=["https://example.com/posts/ai-crawler-opt-out"],
    )

    titles = {item.title for item in result.items}
    assert "AI crawler update: new opt-out" not in titles
```

- [ ] **Step 2: Run test to watch it fail**

```bash
uv run pytest tests/test_fetchers/test_rss_feed.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `fetch_rss_feed`**

Write `pipeline/fetchers/rss_feed.py`:
```python
"""RSS feed fetcher. Returns items newer than `since` and not in `seen_guids`."""
from __future__ import annotations

from datetime import datetime, timezone
from time import mktime

import feedparser
import httpx

from pipeline.fetchers.base import CandidateItem, FetchResult, ResultMode
from pipeline.sources import Source

_UA = "ai-ecosystem-tracker/0.1"
_TIMEOUT = httpx.Timeout(30.0)


async def fetch_rss_feed(
    source: Source,
    since: datetime | None,
    seen_guids: list[str],
) -> FetchResult:
    async with httpx.AsyncClient(headers={"User-Agent": _UA}, timeout=_TIMEOUT, follow_redirects=True) as client:
        resp = await client.get(source.url)
        resp.raise_for_status()
    parsed = feedparser.parse(resp.text)

    seen = set(seen_guids)
    items: list[CandidateItem] = []
    for entry in parsed.entries:
        guid = getattr(entry, "id", None) or getattr(entry, "link", None)
        if not guid or guid in seen:
            continue
        published = _parse_date(entry)
        if since and published and published < since:
            continue
        summary = getattr(entry, "summary", "") or ""
        body = _extract_body(entry)
        items.append(
            CandidateItem(
                guid=guid,
                title=entry.title,
                published_at=published,
                url=getattr(entry, "link", None),
                summary=summary,
                body=body,
            )
        )
    return FetchResult(mode=ResultMode.PER_ITEM, items=items)


def _parse_date(entry) -> datetime | None:
    for attr in ("published_parsed", "updated_parsed"):
        v = getattr(entry, attr, None)
        if v:
            return datetime.fromtimestamp(mktime(v), tz=timezone.utc)
    return None


def _extract_body(entry) -> str:
    # Prefer full content:encoded if present, else fall back to summary.
    content = getattr(entry, "content", None)
    if content:
        return "\n\n".join(c.value for c in content)
    return getattr(entry, "summary", "") or ""
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_fetchers/test_rss_feed.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pipeline/fetchers/rss_feed.py tests/test_fetchers/test_rss_feed.py
git commit -m "feat(pipeline): rss_feed fetcher with since + seen-guid filtering"
```

---

### Task 2.3: `github_repo` fetcher

**Files:**
- Create: `pipeline/fetchers/github_repo.py`
- Create: `tests/test_fetchers/test_github_repo.py`

- [ ] **Step 1: Write the failing test**

Write `tests/test_fetchers/test_github_repo.py`:
```python
from datetime import datetime, timezone

import pytest
import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.github_repo import fetch_github_repo
from pipeline.sources import Pillar, Source, SourceType


@pytest.fixture
def gh_source():
    return Source(
        slug="mcp",
        pillar=Pillar.AGENT,
        type=SourceType.GITHUB_REPO,
        repo="modelcontextprotocol/specification",
        display_name="MCP",
    )


@respx.mock
async def test_includes_releases_and_merged_prs_since_cutoff(gh_source):
    releases_url = "https://api.github.com/repos/modelcontextprotocol/specification/releases"
    prs_url = "https://api.github.com/repos/modelcontextprotocol/specification/pulls"

    respx.get(releases_url).mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": 1,
                    "name": "v1.2.0",
                    "tag_name": "v1.2.0",
                    "published_at": "2026-04-17T12:00:00Z",
                    "html_url": "https://github.com/x/y/releases/tag/v1.2.0",
                    "body": "Added new tool-use protocol.",
                }
            ],
        )
    )
    respx.get(prs_url).mock(
        return_value=Response(
            200,
            json=[
                {
                    "number": 42,
                    "title": "Add structured outputs field to tool call",
                    "merged_at": "2026-04-17T09:00:00Z",
                    "html_url": "https://github.com/x/y/pull/42",
                    "body": "Details about the change.",
                    "labels": [{"name": "spec"}],
                },
                {
                    "number": 43,
                    "title": "Fix typo in readme",
                    "merged_at": "2026-04-16T09:00:00Z",
                    "html_url": "https://github.com/x/y/pull/43",
                    "body": "",
                    "labels": [{"name": "docs"}],
                },
            ],
        )
    )

    since = datetime(2026, 4, 16, tzinfo=timezone.utc)
    result = await fetch_github_repo(gh_source, since=since, seen_guids=[])

    assert result.mode == ResultMode.PER_ITEM
    kinds = {item.guid.split(":")[0] for item in result.items}
    assert kinds == {"release", "pr"}
    assert len(result.items) == 3  # 1 release + 2 PRs (no label filter set)


@respx.mock
async def test_applies_pr_label_filter_when_set(gh_source):
    labeled = gh_source.model_copy(update={"pr_labels": ["spec"]})
    releases_url = "https://api.github.com/repos/modelcontextprotocol/specification/releases"
    prs_url = "https://api.github.com/repos/modelcontextprotocol/specification/pulls"

    respx.get(releases_url).mock(return_value=Response(200, json=[]))
    respx.get(prs_url).mock(
        return_value=Response(
            200,
            json=[
                {
                    "number": 42,
                    "title": "Add structured outputs",
                    "merged_at": "2026-04-17T09:00:00Z",
                    "html_url": "https://x",
                    "body": "",
                    "labels": [{"name": "spec"}],
                },
                {
                    "number": 43,
                    "title": "Typo fix",
                    "merged_at": "2026-04-17T09:00:00Z",
                    "html_url": "https://x",
                    "body": "",
                    "labels": [{"name": "docs"}],
                },
            ],
        )
    )

    result = await fetch_github_repo(labeled, since=None, seen_guids=[])

    guids = {item.guid for item in result.items}
    assert "pr:42" in guids
    assert "pr:43" not in guids
```

- [ ] **Step 2: Run test to watch it fail**

```bash
uv run pytest tests/test_fetchers/test_github_repo.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `fetch_github_repo`**

Write `pipeline/fetchers/github_repo.py`:
```python
"""GitHub releases + merged PRs fetcher."""
from __future__ import annotations

import os
from datetime import datetime

import httpx

from pipeline.fetchers.base import CandidateItem, FetchResult, ResultMode
from pipeline.sources import Source

_UA = "ai-ecosystem-tracker/0.1"
_TIMEOUT = httpx.Timeout(30.0)


async def fetch_github_repo(
    source: Source,
    since: datetime | None,
    seen_guids: list[str],
) -> FetchResult:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"User-Agent": _UA, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    seen = set(seen_guids)
    items: list[CandidateItem] = []
    async with httpx.AsyncClient(headers=headers, timeout=_TIMEOUT, follow_redirects=True) as client:
        releases = await _fetch_releases(client, source, since, seen)
        prs = await _fetch_merged_prs(client, source, since, seen)
    items.extend(releases)
    items.extend(prs)
    return FetchResult(mode=ResultMode.PER_ITEM, items=items)


async def _fetch_releases(
    client: httpx.AsyncClient, source: Source, since: datetime | None, seen: set[str]
) -> list[CandidateItem]:
    resp = await client.get(f"https://api.github.com/repos/{source.repo}/releases", params={"per_page": 20})
    resp.raise_for_status()
    items: list[CandidateItem] = []
    for r in resp.json():
        guid = f"release:{r['id']}"
        if guid in seen:
            continue
        published = datetime.fromisoformat(r["published_at"].replace("Z", "+00:00"))
        if since and published < since:
            continue
        items.append(
            CandidateItem(
                guid=guid,
                title=f"Release {r.get('name') or r['tag_name']}",
                published_at=published,
                url=r.get("html_url"),
                summary=r.get("body") or "",
                body=r.get("body") or "",
            )
        )
    return items


async def _fetch_merged_prs(
    client: httpx.AsyncClient, source: Source, since: datetime | None, seen: set[str]
) -> list[CandidateItem]:
    resp = await client.get(
        f"https://api.github.com/repos/{source.repo}/pulls",
        params={"state": "closed", "sort": "updated", "direction": "desc", "per_page": 30},
    )
    resp.raise_for_status()
    required_labels = set(source.pr_labels)
    items: list[CandidateItem] = []
    for pr in resp.json():
        if not pr.get("merged_at"):
            continue
        guid = f"pr:{pr['number']}"
        if guid in seen:
            continue
        merged = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
        if since and merged < since:
            continue
        labels = {label["name"] for label in pr.get("labels", [])}
        if required_labels and not (required_labels & labels):
            continue
        items.append(
            CandidateItem(
                guid=guid,
                title=f"PR #{pr['number']}: {pr['title']}",
                published_at=merged,
                url=pr.get("html_url"),
                summary=pr.get("title") or "",
                body=pr.get("body") or "",
            )
        )
    return items
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_fetchers/test_github_repo.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pipeline/fetchers/github_repo.py tests/test_fetchers/test_github_repo.py
git commit -m "feat(pipeline): github_repo fetcher for releases + merged PRs"
```

---

### Task 2.4: `ietf_draft` fetcher

**Files:**
- Create: `pipeline/fetchers/ietf_draft.py`
- Create: `tests/test_fetchers/test_ietf_draft.py`

- [ ] **Step 1: Write the failing test**

Write `tests/test_fetchers/test_ietf_draft.py`:
```python
import pytest
import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.ietf_draft import fetch_ietf_draft
from pipeline.sources import Pillar, Source, SourceType


@pytest.fixture
def ietf_source():
    return Source(
        slug="wba",
        pillar=Pillar.AGENT,
        type=SourceType.IETF_DRAFT,
        draft_name="draft-cloudflare-httpbis-web-bot-auth",
        display_name="Web Bot Auth",
    )


@respx.mock
async def test_fetches_latest_revision_text(ietf_source):
    meta_url = (
        "https://datatracker.ietf.org/api/v1/doc/document/"
        "draft-cloudflare-httpbis-web-bot-auth/?format=json"
    )
    respx.get(meta_url).mock(
        return_value=Response(
            200,
            json={"rev": "02", "name": "draft-cloudflare-httpbis-web-bot-auth"},
        )
    )
    txt_url = "https://www.ietf.org/archive/id/draft-cloudflare-httpbis-web-bot-auth-02.txt"
    respx.get(txt_url).mock(return_value=Response(200, text="Full text of draft-02 body."))

    result = await fetch_ietf_draft(ietf_source)

    assert result.mode == ResultMode.DIFFABLE
    assert "Full text of draft-02 body." in result.normalized_content
    assert result.raw_ext == "txt"
```

- [ ] **Step 2: Run to watch fail**

```bash
uv run pytest tests/test_fetchers/test_ietf_draft.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `fetch_ietf_draft`**

Write `pipeline/fetchers/ietf_draft.py`:
```python
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
    async with httpx.AsyncClient(headers={"User-Agent": _UA}, timeout=_TIMEOUT, follow_redirects=True) as client:
        meta = await client.get(meta_url)
        meta.raise_for_status()
        rev = meta.json()["rev"]
        txt_url = f"https://www.ietf.org/archive/id/{source.draft_name}-{rev}.txt"
        body = await client.get(txt_url)
        body.raise_for_status()

    return FetchResult(mode=ResultMode.DIFFABLE, normalized_content=body.text, raw_ext="txt")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_fetchers/test_ietf_draft.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add pipeline/fetchers/ietf_draft.py tests/test_fetchers/test_ietf_draft.py
git commit -m "feat(pipeline): ietf_draft fetcher via datatracker API"
```

---

## Phase 3: Differ

### Task 3.1: Markdown-normalized diff generator

**Files:**
- Create: `pipeline/differ.py`
- Create: `tests/test_differ.py`

- [ ] **Step 1: Write failing test**

Write `tests/test_differ.py`:
```python
from pipeline.differ import compute_diff


def test_diff_hides_identical_content():
    d = compute_diff("Hello world.\nSecond line.", "Hello world.\nSecond line.")
    assert d.has_changes is False
    assert d.unified_diff == ""


def test_diff_shows_added_and_removed_lines():
    a = "Line one.\nLine two.\nLine three."
    b = "Line one.\nLine two CHANGED.\nLine three.\nLine four added."
    d = compute_diff(a, b)
    assert d.has_changes is True
    assert "-Line two." in d.unified_diff
    assert "+Line two CHANGED." in d.unified_diff
    assert "+Line four added." in d.unified_diff


def test_diff_normalizes_whitespace_but_preserves_semantics():
    a = "Hello   world.\n\n\nSame."
    b = "Hello world.\nSame."
    d = compute_diff(a, b)
    assert d.has_changes is False
```

- [ ] **Step 2: Watch it fail**

```bash
uv run pytest tests/test_differ.py -v
```

- [ ] **Step 3: Implement**

Write `pipeline/differ.py`:
```python
"""Diff two normalized text blobs and emit a unified diff."""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass


@dataclass
class DiffResult:
    has_changes: bool
    unified_diff: str


def compute_diff(prev: str, curr: str, context: int = 3) -> DiffResult:
    a_norm = _normalize(prev)
    b_norm = _normalize(curr)
    if a_norm == b_norm:
        return DiffResult(has_changes=False, unified_diff="")
    diff = difflib.unified_diff(
        a_norm.splitlines(),
        b_norm.splitlines(),
        fromfile="prev",
        tofile="curr",
        n=context,
        lineterm="",
    )
    return DiffResult(has_changes=True, unified_diff="\n".join(diff))


_WS = re.compile(r"[ \t]+")
_MULTI_NL = re.compile(r"\n{2,}")


def _normalize(text: str) -> str:
    text = _WS.sub(" ", text)
    text = _MULTI_NL.sub("\n", text)
    return text.strip()
```

- [ ] **Step 4: Verify passes**

```bash
uv run pytest tests/test_differ.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pipeline/differ.py tests/test_differ.py
git commit -m "feat(pipeline): text normalizer + unified diff"
```

---

## Phase 4: Relevance filter

### Task 4.1: Keyword filter (regex, stage 1)

**Files:**
- Create: `pipeline/relevance.py`
- Create: `tests/test_relevance.py`

- [ ] **Step 1: Write failing test (stage 1 only)**

Write `tests/test_relevance.py`:
```python
from pipeline.relevance import keyword_match


def test_keyword_match_case_insensitive():
    assert keyword_match("AI Bots are evolving", ["AI bot"]) is True
    assert keyword_match("we launched a new firewall", ["AI bot", "crawler"]) is False


def test_keyword_match_substring():
    assert keyword_match("trainingdata policies", ["training data"]) is False
    assert keyword_match("training data policies", ["training data"]) is True


def test_keyword_match_empty_list_returns_true():
    # A source without keywords passes stage 1 by default
    assert keyword_match("anything", []) is True
```

- [ ] **Step 2: Watch it fail**

```bash
uv run pytest tests/test_relevance.py -v
```

- [ ] **Step 3: Implement `keyword_match`**

Write `pipeline/relevance.py`:
```python
"""Two-stage relevance funnel: cheap keyword regex, then Haiku classifier."""
from __future__ import annotations

import re
from dataclasses import dataclass

from anthropic import AsyncAnthropic


def keyword_match(text: str, keywords: list[str]) -> bool:
    """Stage 1: cheap word-boundary regex match against any keyword."""
    if not keywords:
        return True
    haystack = text.lower()
    for kw in keywords:
        needle = kw.lower().strip()
        if not needle:
            continue
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(needle) + r"(?![a-z0-9])")
        if pattern.search(haystack):
            return True
    return False


@dataclass
class RelevanceVerdict:
    is_relevant: bool
    reason: str


_RELEVANCE_PROMPT = (
    "You are a classifier for an AI-content-ecosystem tracker. "
    "Given a post title and summary, decide whether it is RELEVANT to: "
    "AI crawler policy, AI training data, bot access / robots.txt, "
    "content-ecosystem regulation (AI), AI agent infrastructure, "
    "AI bot identity / auth. "
    "Return a single JSON object: "
    '{"is_relevant": true|false, "reason": "<one short sentence>"}'
)


async def haiku_relevance(
    client: AsyncAnthropic, title: str, summary: str
) -> RelevanceVerdict:
    """Stage 2: Haiku call returning structured verdict."""
    resp = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        system=_RELEVANCE_PROMPT,
        messages=[{"role": "user", "content": f"Title: {title}\n\nSummary: {summary}"}],
    )
    text = resp.content[0].text
    import json

    data = json.loads(text)
    return RelevanceVerdict(is_relevant=bool(data["is_relevant"]), reason=data["reason"])
```

- [ ] **Step 4: Verify passes**

```bash
uv run pytest tests/test_relevance.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add pipeline/relevance.py tests/test_relevance.py
git commit -m "feat(pipeline): keyword_match stage-1 regex"
```

---

### Task 4.2: Haiku relevance classifier (stage 2)

**Files:**
- Modify: `tests/test_relevance.py` (add stage-2 tests)

- [ ] **Step 1: Add failing tests for Haiku classifier**

Append to `tests/test_relevance.py`:
```python
from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.relevance import haiku_relevance


class _FakeMessage:
    def __init__(self, text: str):
        self.content = [MagicMock(text=text)]


@pytest.fixture
def fake_client():
    client = MagicMock()
    client.messages.create = AsyncMock()
    return client


async def test_haiku_returns_relevant(fake_client):
    fake_client.messages.create.return_value = _FakeMessage(
        '{"is_relevant": true, "reason": "Discusses GPTBot opt-out"}'
    )
    v = await haiku_relevance(fake_client, "Cloudflare launches AI bot audit", "...")
    assert v.is_relevant is True
    assert "GPTBot" in v.reason


async def test_haiku_returns_not_relevant(fake_client):
    fake_client.messages.create.return_value = _FakeMessage(
        '{"is_relevant": false, "reason": "Unrelated product"}'
    )
    v = await haiku_relevance(fake_client, "We launched new dashboard widgets", "...")
    assert v.is_relevant is False
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/test_relevance.py -v
```

Expected: 5 passed total (3 from 4.1 + 2 new).

- [ ] **Step 3: Commit**

```bash
git add tests/test_relevance.py
git commit -m "test(pipeline): cover Haiku relevance classifier"
```

---

## Phase 5: Analyzer

### Task 5.1: Sonnet analyzer with structured tool use

**Files:**
- Create: `pipeline/analyzer.py`
- Create: `tests/test_analyzer.py`

- [ ] **Step 1: Write failing test**

Write `tests/test_analyzer.py`:
```python
from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.analyzer import AnalysisResult, analyze_change
from pipeline.sources import Pillar, Source, SourceType


@pytest.fixture
def fake_client():
    client = MagicMock()
    client.messages.create = AsyncMock()
    return client


def _tool_response(arguments: dict):
    block = MagicMock()
    block.type = "tool_use"
    block.name = "emit_analysis"
    block.input = arguments
    msg = MagicMock()
    msg.content = [block]
    msg.stop_reason = "tool_use"
    return msg


@pytest.fixture
def crawler_source():
    return Source(
        slug="gptbot",
        pillar=Pillar.CRAWLER,
        type=SourceType.HTML_PAGE,
        url="https://x",
        display_name="OpenAI GPTBot",
    )


async def test_analyzer_returns_structured_result_for_crawler_change(fake_client, crawler_source):
    fake_client.messages.create.return_value = _tool_response(
        {
            "change_kind": "material",
            "importance": 0.80,
            "title": "OpenAI adds Operator UA string",
            "what_changed": "GPTBot docs now list a second UA for Operator.",
            "implication": "",
        }
    )

    result = await analyze_change(
        client=fake_client,
        source=crawler_source,
        prev_content="old doc",
        curr_content="new doc",
        unified_diff="-x\n+y",
    )

    assert isinstance(result, AnalysisResult)
    assert result.change_kind == "material"
    assert result.importance == 0.80
    assert result.title.startswith("OpenAI adds")


async def test_analyzer_cosmetic_change(fake_client, crawler_source):
    fake_client.messages.create.return_value = _tool_response(
        {
            "change_kind": "cosmetic",
            "importance": 0.1,
            "title": "Typo fix",
            "what_changed": "Fixed a typo.",
            "implication": "",
        }
    )

    result = await analyze_change(
        client=fake_client,
        source=crawler_source,
        prev_content="old",
        curr_content="new",
        unified_diff="-typo\n+typo-fixed",
    )

    assert result.change_kind == "cosmetic"
```

- [ ] **Step 2: Watch it fail**

```bash
uv run pytest tests/test_analyzer.py -v
```

- [ ] **Step 3: Implement `pipeline/analyzer.py`**

Write `pipeline/analyzer.py`:
```python
"""Claude Sonnet analyzer: classifies a diff and emits structured analysis."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from anthropic import AsyncAnthropic

from pipeline.sources import Pillar, Source

DEFAULT_MODEL = "claude-sonnet-4-6"
OPUS_MODEL = "claude-opus-4-7"


@dataclass
class AnalysisResult:
    change_kind: Literal["material", "cosmetic", "noise"]
    importance: float
    title: str
    what_changed: str
    implication: str


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
        },
        "required": ["change_kind", "importance", "title", "what_changed", "implication"],
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
    "Always call the emit_analysis tool exactly once with your verdict."
)


_CRAWLER_ADDON = (
    "\n\nThis is a PILLAR 1 crawler-doc source: the reader is looking for precise fact "
    "(what UA string changed, what directive was added, what opt-out mechanism shifted). "
    "Keep `what_changed` ≤3 sentences, factual. `implication` may be empty if no notable "
    "reader takeaway."
)

_NEWS_ADDON = (
    "\n\nThis is a pillar-2/3 news source: the reader wants 3–5 sentences of what_changed "
    "and 3–5 sentences of implication explaining why a publisher / policy / agent-infra "
    "practitioner should care. Avoid hype."
)


async def analyze_change(
    *,
    client: AsyncAnthropic,
    source: Source,
    prev_content: str,
    curr_content: str,
    unified_diff: str,
) -> AnalysisResult:
    system = _SYSTEM_BASE + (_CRAWLER_ADDON if source.pillar == Pillar.CRAWLER else _NEWS_ADDON)
    model = _resolve_model(source.model)
    user_content = (
        f"Source: {source.display_name} ({source.pillar.value})\n"
        f"URL: {source.url or ''}\n\n"
        f"=== PREVIOUS ===\n{prev_content[:20000]}\n\n"
        f"=== CURRENT ===\n{curr_content[:20000]}\n\n"
        f"=== DIFF ===\n{unified_diff[:20000]}\n"
    )

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
            return AnalysisResult(**block.input)
    raise RuntimeError("analyzer did not return tool_use")


def _resolve_model(override: str | None) -> str:
    if override == "opus":
        return OPUS_MODEL
    if override and override.startswith("claude-"):
        return override
    return DEFAULT_MODEL
```

- [ ] **Step 4: Verify passes**

```bash
uv run pytest tests/test_analyzer.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pipeline/analyzer.py tests/test_analyzer.py
git commit -m "feat(pipeline): Sonnet analyzer with structured tool_use + prompt caching"
```

---

### Task 5.2: Event markdown writer

**Files:**
- Create: `pipeline/event_writer.py`
- Create: `tests/test_event_writer.py`

- [ ] **Step 1: Write failing test**

Write `tests/test_event_writer.py`:
```python
from datetime import datetime, timezone
from pathlib import Path

from pipeline.analyzer import AnalysisResult
from pipeline.event_writer import write_event
from pipeline.sources import Pillar, Source, SourceType


def test_write_event_creates_file_with_frontmatter(tmp_path: Path):
    source = Source(
        slug="gptbot",
        pillar=Pillar.CRAWLER,
        type=SourceType.HTML_PAGE,
        url="https://x",
        display_name="OpenAI GPTBot",
    )
    analysis = AnalysisResult(
        change_kind="material",
        importance=0.82,
        title="OpenAI adds Operator UA",
        what_changed="New UA string.",
        implication="",
    )
    detected_at = datetime(2026, 4, 18, 8, 0, 0, tzinfo=timezone.utc)

    path = write_event(
        events_dir=tmp_path,
        source=source,
        analysis=analysis,
        detected_at=detected_at,
        unified_diff="-old\n+new",
    )

    assert path.exists()
    text = path.read_text()
    assert text.startswith("---\n")
    assert "slug: openai-adds-operator-ua" in text
    assert "source: gptbot" in text
    assert "pillar: crawler" in text
    assert "change_kind: material" in text
    assert "importance: 0.82" in text
    assert "## What changed\n\nNew UA string." in text
    assert "```diff\n-old\n+new" in text


def test_write_event_filename_convention(tmp_path: Path):
    source = Source(
        slug="cloudflare-blog",
        pillar=Pillar.ECOSYSTEM,
        type=SourceType.RSS_FEED,
        url="https://x/rss",
        keyword_filter=["AI"],
        display_name="Cloudflare",
    )
    analysis = AnalysisResult(
        change_kind="material",
        importance=0.6,
        title="Cloudflare ships AI Audit",
        what_changed="Details.",
        implication="Implications here.",
    )
    detected_at = datetime(2026, 4, 18, 12, 0, 0, tzinfo=timezone.utc)

    path = write_event(
        events_dir=tmp_path,
        source=source,
        analysis=analysis,
        detected_at=detected_at,
        unified_diff="",
    )

    assert path.name == "2026-04-18-cloudflare-blog-cloudflare-ships-ai-audit.md"
```

- [ ] **Step 2: Watch it fail**

```bash
uv run pytest tests/test_event_writer.py -v
```

- [ ] **Step 3: Implement**

Write `pipeline/event_writer.py`:
```python
"""Write a detected event as markdown with YAML frontmatter."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from pipeline.analyzer import AnalysisResult
from pipeline.sources import Source


def write_event(
    *,
    events_dir: Path,
    source: Source,
    analysis: AnalysisResult,
    detected_at: datetime,
    unified_diff: str,
    source_url: str | None = None,
) -> Path:
    events_dir.mkdir(parents=True, exist_ok=True)
    slug = _slugify(analysis.title)
    filename = f"{detected_at.date().isoformat()}-{source.slug}-{slug}.md"
    path = events_dir / filename

    url = source_url or source.url or ""
    body = _compose(source=source, analysis=analysis, detected_at=detected_at,
                    source_url=url, unified_diff=unified_diff, event_slug=slug)
    path.write_text(body)
    return path


_SLUG_RX = re.compile(r"[^a-z0-9]+")


def _slugify(title: str) -> str:
    s = _SLUG_RX.sub("-", title.lower()).strip("-")
    return s[:80] or "untitled"


def _compose(*, source, analysis, detected_at, source_url, unified_diff, event_slug) -> str:
    frontmatter = (
        "---\n"
        f"slug: {event_slug}\n"
        f'title: "{_yaml_escape(analysis.title)}"\n'
        f"source: {source.slug}\n"
        f"pillar: {source.pillar.value}\n"
        f"detected_at: {detected_at.isoformat()}\n"
        f"source_url: {source_url}\n"
        f"change_kind: {analysis.change_kind}\n"
        f"importance: {analysis.importance:.2f}\n"
        "---\n\n"
    )
    body = f"## What changed\n\n{analysis.what_changed}\n\n"
    if analysis.implication.strip():
        body += f"## Implication\n\n{analysis.implication}\n\n"
    if unified_diff.strip():
        body += "## Raw diff\n\n<details><summary>View diff</summary>\n\n"
        body += f"```diff\n{unified_diff}\n```\n\n</details>\n"
    return frontmatter + body


def _yaml_escape(s: str) -> str:
    return s.replace('"', '\\"')
```

- [ ] **Step 4: Verify passes**

```bash
uv run pytest tests/test_event_writer.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add pipeline/event_writer.py tests/test_event_writer.py
git commit -m "feat(pipeline): event markdown writer with frontmatter"
```

---

## Phase 6: State of Play

### Task 6.1: Haiku extractor + aggregate JSON writer

**Files:**
- Create: `pipeline/state_of_play.py`
- Create: `tests/test_state_of_play.py`

- [ ] **Step 1: Write failing test**

Write `tests/test_state_of_play.py`:
```python
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.sources import Pillar, Source, SourceType
from pipeline.state_of_play import build_opt_out_matrix


@pytest.fixture
def crawler_sources():
    return [
        Source(slug="gptbot", pillar=Pillar.CRAWLER, type=SourceType.HTML_PAGE,
               url="https://x", display_name="OpenAI GPTBot"),
        Source(slug="claudebot", pillar=Pillar.CRAWLER, type=SourceType.HTML_PAGE,
               url="https://y", display_name="Anthropic ClaudeBot"),
    ]


@pytest.fixture
def fake_client():
    client = MagicMock()
    client.messages.create = AsyncMock()
    return client


def _tool_response(args):
    block = MagicMock()
    block.type = "tool_use"
    block.name = "emit_crawler_facts"
    block.input = args
    msg = MagicMock()
    msg.content = [block]
    return msg


async def test_build_opt_out_matrix_writes_json(tmp_path: Path, crawler_sources, fake_client):
    fake_client.messages.create.side_effect = [
        _tool_response({
            "supports_robots_txt": True,
            "supports_user_agent_opt_out": True,
            "policy_url": "https://x/docs",
        }),
        _tool_response({
            "supports_robots_txt": True,
            "supports_user_agent_opt_out": True,
            "policy_url": "https://y/docs",
        }),
    ]

    def load_latest_snapshot(slug: str) -> tuple[str, datetime] | None:
        return ("dummy content", datetime(2026, 4, 18, tzinfo=timezone.utc))

    out_path = tmp_path / "opt-out-matrix.json"
    await build_opt_out_matrix(
        client=fake_client,
        crawler_sources=crawler_sources,
        load_latest_snapshot=load_latest_snapshot,
        out_path=out_path,
        now=datetime(2026, 4, 20, tzinfo=timezone.utc),
    )

    data = json.loads(out_path.read_text())
    assert {row["slug"] for row in data["entries"]} == {"gptbot", "claudebot"}
    first = data["entries"][0]
    assert first["supports_robots_txt"] is True
    assert first["days_since_last_change"] == 2
```

- [ ] **Step 2: Watch it fail**

```bash
uv run pytest tests/test_state_of_play.py -v
```

- [ ] **Step 3: Implement**

Write `pipeline/state_of_play.py`:
```python
"""Extract per-crawler facts with Haiku and aggregate State-of-Play JSON."""
from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from anthropic import AsyncAnthropic

from pipeline.sources import Source

HAIKU_MODEL = "claude-haiku-4-5-20251001"

_CRAWLER_FACTS_TOOL = {
    "name": "emit_crawler_facts",
    "description": "Emit structured facts about this crawler's opt-out behavior.",
    "input_schema": {
        "type": "object",
        "properties": {
            "supports_robots_txt": {"type": "boolean"},
            "supports_user_agent_opt_out": {"type": "boolean"},
            "policy_url": {"type": "string"},
        },
        "required": ["supports_robots_txt", "supports_user_agent_opt_out", "policy_url"],
    },
}


async def _extract_crawler_facts(client: AsyncAnthropic, source: Source, content: str) -> dict:
    msg = await client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=300,
        system=(
            "You extract factual fields from an AI crawler's official documentation. "
            "Be conservative: only mark true when the documentation explicitly supports it."
        ),
        tools=[_CRAWLER_FACTS_TOOL],
        tool_choice={"type": "tool", "name": "emit_crawler_facts"},
        messages=[{"role": "user", "content": f"Vendor: {source.display_name}\n\n{content[:15000]}"}],
    )
    for block in msg.content:
        if getattr(block, "type", None) == "tool_use":
            return dict(block.input)
    raise RuntimeError(f"state_of_play: no tool_use for {source.slug}")


async def build_opt_out_matrix(
    *,
    client: AsyncAnthropic,
    crawler_sources: list[Source],
    load_latest_snapshot: Callable[[str], tuple[str, datetime] | None],
    out_path: Path,
    now: datetime,
) -> None:
    entries = []
    for s in crawler_sources:
        snap = load_latest_snapshot(s.slug)
        if not snap:
            continue
        content, snap_date = snap
        facts = await _extract_crawler_facts(client, s, content)
        days_since = (now.date() - snap_date.date()).days
        entries.append(
            {
                "slug": s.slug,
                "display_name": s.display_name,
                "supports_robots_txt": facts["supports_robots_txt"],
                "supports_user_agent_opt_out": facts["supports_user_agent_opt_out"],
                "policy_url": facts["policy_url"],
                "days_since_last_change": days_since,
                "last_snapshot_date": snap_date.date().isoformat(),
            }
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"generated_at": now.isoformat(), "entries": entries}, indent=2))
```

- [ ] **Step 4: Verify passes**

```bash
uv run pytest tests/test_state_of_play.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add pipeline/state_of_play.py tests/test_state_of_play.py
git commit -m "feat(pipeline): State of Play extractor + opt-out matrix"
```

---

## Phase 7: check.py orchestrator

### Task 7.1: Snapshot helpers

**Files:**
- Create: `pipeline/snapshots.py`
- Create: `tests/test_snapshots.py`

- [ ] **Step 1: Write failing test**

Write `tests/test_snapshots.py`:
```python
from datetime import datetime, timezone
from pathlib import Path

from pipeline.snapshots import hash_content, load_latest, save_snapshot


def test_hash_stable():
    assert hash_content("hello") == hash_content("hello")
    assert hash_content("hello") != hash_content("world")


def test_save_and_load_latest(tmp_path: Path):
    save_snapshot(tmp_path, "gptbot", datetime(2026, 3, 1, tzinfo=timezone.utc),
                  content="v1", ext="html")
    save_snapshot(tmp_path, "gptbot", datetime(2026, 4, 18, tzinfo=timezone.utc),
                  content="v2", ext="html")

    latest = load_latest(tmp_path, "gptbot")
    assert latest is not None
    content, date = latest
    assert content == "v2"
    assert date.date().isoformat() == "2026-04-18"


def test_load_latest_none_when_no_snapshots(tmp_path: Path):
    assert load_latest(tmp_path, "newthing") is None
```

- [ ] **Step 2: Watch fail, implement, verify**

Write `pipeline/snapshots.py`:
```python
"""Per-source snapshot persistence under `content/snapshots/{slug}/{date}.{ext}`."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path


def hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def save_snapshot(snapshots_root: Path, slug: str, when: datetime, *, content: str, ext: str) -> Path:
    folder = snapshots_root / slug
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / f"{when.date().isoformat()}.{ext}"
    p.write_text(content)
    return p


_DATE_RX = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.")


def load_latest(snapshots_root: Path, slug: str) -> tuple[str, datetime] | None:
    folder = snapshots_root / slug
    if not folder.exists():
        return None
    candidates: list[tuple[datetime, Path]] = []
    for p in folder.iterdir():
        m = _DATE_RX.match(p.name)
        if not m:
            continue
        y, mo, d = (int(x) for x in m.groups())
        candidates.append((datetime(y, mo, d, tzinfo=timezone.utc), p))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    dt, p = candidates[0]
    return (p.read_text(), dt)
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/test_snapshots.py -v
```

Expected: 3 passed.

- [ ] **Step 4: Commit**

```bash
git add pipeline/snapshots.py tests/test_snapshots.py
git commit -m "feat(pipeline): snapshot hashing + load_latest helpers"
```

---

### Task 7.2: Main orchestrator (`check.py`)

**Files:**
- Create: `pipeline/check.py`
- Create: `pipeline/git_ops.py`
- Create: `tests/test_check.py`

- [ ] **Step 1: Write an end-to-end orchestrator test**

Write `tests/test_check.py`:
```python
"""Smoke-level orchestration test: one html_page source, one change → one event."""
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import yaml

from pipeline.analyzer import AnalysisResult
from pipeline.check import run_check
from pipeline.fetchers.base import FetchResult, ResultMode


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "content" / "snapshots").mkdir(parents=True)
    (tmp_path / "content" / "events").mkdir(parents=True)
    (tmp_path / "data").mkdir(parents=True)
    (tmp_path / "state").mkdir(parents=True)
    (tmp_path / "sources.yaml").write_text(
        yaml.safe_dump(
            [
                {
                    "slug": "gptbot",
                    "pillar": "crawler",
                    "type": "html_page",
                    "url": "https://platform.openai.com/docs/gptbot",
                    "display_name": "OpenAI GPTBot",
                }
            ]
        )
    )
    return tmp_path


async def test_new_source_first_run_is_catchup_no_event(repo):
    fetch = AsyncMock(return_value=FetchResult(mode=ResultMode.DIFFABLE, normalized_content="v1", raw_ext="html"))
    analyze = AsyncMock()
    now = datetime(2026, 4, 18, 8, tzinfo=timezone.utc)

    await run_check(
        repo_root=repo,
        now=now,
        fetch_dispatch=lambda s, state: fetch(s),
        analyze_change=analyze,
        extract_sop=AsyncMock(),
        only=None,
        dry_run=False,
    )

    events = list((repo / "content" / "events").glob("*.md"))
    assert events == []
    snaps = list((repo / "content" / "snapshots" / "gptbot").glob("*.html"))
    assert len(snaps) == 1
    analyze.assert_not_called()


async def test_subsequent_change_emits_event(repo):
    (repo / "content" / "snapshots" / "gptbot").mkdir(parents=True)
    (repo / "content" / "snapshots" / "gptbot" / "2026-03-01.html").write_text("v1")
    (repo / "state" / "gptbot.json").write_text(
        '{"last_checked_at": "2026-03-01T00:00:00+00:00", "last_hash": "'
        + __import__("hashlib").sha256(b"v1").hexdigest()
        + '", "last_seen_guids": [], "consecutive_failures": 0, "first_seen": false}'
    )

    fetch = AsyncMock(
        return_value=FetchResult(mode=ResultMode.DIFFABLE, normalized_content="v2 updated", raw_ext="html")
    )
    analyze = AsyncMock(
        return_value=AnalysisResult(
            change_kind="material",
            importance=0.85,
            title="GPTBot adds section",
            what_changed="Added.",
            implication="Important.",
        )
    )
    now = datetime(2026, 4, 18, 8, tzinfo=timezone.utc)

    await run_check(
        repo_root=repo,
        now=now,
        fetch_dispatch=lambda s, state: fetch(s),
        analyze_change=analyze,
        extract_sop=AsyncMock(),
        only=None,
        dry_run=False,
    )

    events = list((repo / "content" / "events").glob("*.md"))
    assert len(events) == 1
    assert "gptbot-gptbot-adds-section" in events[0].name
    analyze.assert_called_once()
```

- [ ] **Step 2: Watch it fail**

```bash
uv run pytest tests/test_check.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: Implement `pipeline/check.py`**

Write `pipeline/check.py`:
```python
"""Daily orchestrator: fetch → diff/relevance → analyze → write → commit."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from pathlib import Path

from anthropic import AsyncAnthropic

from pipeline.analyzer import AnalysisResult, analyze_change
from pipeline.config import Config
from pipeline.differ import compute_diff
from pipeline.event_writer import write_event
from pipeline.fetchers.base import FetchResult, ResultMode
from pipeline.fetchers.github_repo import fetch_github_repo
from pipeline.fetchers.html_page import fetch_html_page
from pipeline.fetchers.ietf_draft import fetch_ietf_draft
from pipeline.fetchers.rss_feed import fetch_rss_feed
from pipeline.relevance import haiku_relevance, keyword_match
from pipeline.snapshots import hash_content, load_latest, save_snapshot
from pipeline.sources import Pillar, Source, SourceType, load_sources
from pipeline.state import SourceState, load_state, save_state
from pipeline.state_of_play import build_opt_out_matrix

log = logging.getLogger("check")


FetchDispatch = Callable[[Source, SourceState], Awaitable[FetchResult]]


async def _default_fetch(source: Source, state: SourceState) -> FetchResult:
    if source.type == SourceType.HTML_PAGE:
        return await fetch_html_page(source)
    if source.type == SourceType.RSS_FEED:
        return await fetch_rss_feed(source, since=state.last_checked_at, seen_guids=state.last_seen_guids)
    if source.type == SourceType.GITHUB_REPO:
        return await fetch_github_repo(source, since=state.last_checked_at, seen_guids=state.last_seen_guids)
    if source.type == SourceType.IETF_DRAFT:
        return await fetch_ietf_draft(source)
    raise ValueError(f"unknown source type {source.type}")


async def run_check(
    *,
    repo_root: Path,
    now: datetime,
    fetch_dispatch: FetchDispatch | None = None,
    analyze_change: Callable = analyze_change,  # noqa: A002 (shadow ok in this scope)
    extract_sop: Callable | None = None,
    anthropic_client: AsyncAnthropic | None = None,
    only: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Run the daily pipeline. Returns a health summary dict."""
    cfg = Config(repo_root=repo_root, anthropic_api_key="", alert_emails=[])
    sources = load_sources(cfg.sources_yaml)
    if only:
        sources = [s for s in sources if s.slug == only]
        if not sources:
            raise ValueError(f"--only {only!r} did not match any source")

    fetch_dispatch = fetch_dispatch or _default_fetch
    client = anthropic_client  # may be None in tests

    per_source_status: dict[str, str] = {}
    events_written: list[Path] = []

    for source in sources:
        state = load_state(cfg.state_dir, source.slug)
        try:
            result = await fetch_dispatch(source, state)
            new_events, updated_state = await _process_result(
                source=source, state=state, result=result, now=now,
                cfg=cfg, client=client, analyze_change=analyze_change, dry_run=dry_run,
            )
            events_written.extend(new_events)
            state = updated_state
            state.last_checked_at = now
            state.consecutive_failures = 0
            if not dry_run:
                save_state(cfg.state_dir, source.slug, state)
            per_source_status[source.slug] = "ok"
        except Exception as e:
            log.exception("fetch failed for %s", source.slug)
            state.consecutive_failures += 1
            if not dry_run:
                save_state(cfg.state_dir, source.slug, state)
            per_source_status[source.slug] = f"error: {e}"

    # State of Play — only if we have a real client and there are crawler sources
    if extract_sop is not None and not dry_run:
        try:
            await extract_sop(sources=sources, repo_root=repo_root, now=now)
        except Exception as e:
            log.exception("state_of_play failed")
            per_source_status["_sop"] = f"error: {e}"

    health = {
        "last_run_at": now.isoformat(),
        "per_source_status": per_source_status,
        "events_written": [str(p.relative_to(repo_root)) for p in events_written],
    }
    if not dry_run:
        (cfg.data_dir).mkdir(parents=True, exist_ok=True)
        (cfg.data_dir / "health.json").write_text(json.dumps(health, indent=2))
    return health


async def _process_result(
    *, source: Source, state: SourceState, result: FetchResult,
    now: datetime, cfg: Config, client: AsyncAnthropic | None,
    analyze_change, dry_run: bool,
) -> tuple[list[Path], SourceState]:
    new_events: list[Path] = []

    if result.mode == ResultMode.DIFFABLE:
        new_hash = hash_content(result.normalized_content)
        if state.last_hash == new_hash:
            return new_events, state
        if not dry_run:
            save_snapshot(cfg.snapshots_dir, source.slug, now,
                          content=result.normalized_content, ext=result.raw_ext)
        prev = load_latest(cfg.snapshots_dir, source.slug)
        # Catch-up: first-ever snapshot → no event
        if state.first_seen or prev is None or prev[0] == result.normalized_content:
            state.first_seen = False
            state.last_hash = new_hash
            return new_events, state
        diff = compute_diff(prev[0], result.normalized_content)
        if not diff.has_changes:
            state.last_hash = new_hash
            return new_events, state
        if client is None:
            raise RuntimeError(f"{source.slug}: change detected but no anthropic client provided")
        analysis: AnalysisResult = await analyze_change(
            client=client, source=source,
            prev_content=prev[0], curr_content=result.normalized_content,
            unified_diff=diff.unified_diff,
        )
        if analysis.change_kind == "material" and not dry_run:
            path = write_event(
                events_dir=cfg.events_dir, source=source, analysis=analysis,
                detected_at=now, unified_diff=diff.unified_diff,
            )
            new_events.append(path)
        state.last_hash = new_hash
        return new_events, state

    # PER_ITEM
    for item in result.items:
        # Stage 1 — cheap keyword filter
        blob = f"{item.title}\n{item.summary}"
        if not keyword_match(blob, source.keyword_filter or []):
            state.last_seen_guids.append(item.guid)
            continue
        # Stage 2 — Haiku relevance
        if client is None:
            raise RuntimeError(f"{source.slug}: per-item item passed stage 1 but no client")
        verdict = await haiku_relevance(client, item.title, item.summary)
        if not verdict.is_relevant:
            state.last_seen_guids.append(item.guid)
            continue
        analysis: AnalysisResult = await analyze_change(
            client=client, source=source,
            prev_content="", curr_content=item.body or item.summary,
            unified_diff="",
        )
        if analysis.change_kind == "material" and not dry_run:
            path = write_event(
                events_dir=cfg.events_dir, source=source, analysis=analysis,
                detected_at=item.published_at or now,
                unified_diff="", source_url=item.url,
            )
            new_events.append(path)
        state.last_seen_guids.append(item.guid)

    # Catch-up for newly-added RSS/GitHub source: drop events emitted on first run
    if state.first_seen:
        for p in new_events:
            p.unlink(missing_ok=True)
        new_events = []
        state.first_seen = False

    # Cap last_seen_guids to avoid unbounded growth
    state.last_seen_guids = state.last_seen_guids[-500:]
    return new_events, state


def _cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", type=str, default=None)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    cfg = Config.from_env()
    client = AsyncAnthropic(api_key=cfg.anthropic_api_key) if cfg.anthropic_api_key else None

    async def _sop(sources, repo_root, now):
        from pipeline import snapshots as snap_mod
        crawler_sources = [s for s in sources if s.pillar == Pillar.CRAWLER]

        def _load(slug: str):
            return snap_mod.load_latest(cfg.snapshots_dir, slug)

        await build_opt_out_matrix(
            client=client, crawler_sources=crawler_sources,
            load_latest_snapshot=_load,
            out_path=cfg.data_dir / "opt-out-matrix.json",
            now=now,
        )

    asyncio.run(
        run_check(
            repo_root=cfg.repo_root,
            now=datetime.now(tz=timezone.utc),
            anthropic_client=client,
            extract_sop=_sop if client else None,
            only=args.only,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    _cli()
```

- [ ] **Step 4: Implement `pipeline/git_ops.py`**

Write `pipeline/git_ops.py`:
```python
"""Thin subprocess wrapper around git for commit+push from the pipeline."""
from __future__ import annotations

import subprocess
from pathlib import Path


def stage_and_commit(repo_root: Path, message: str) -> bool:
    """Stage all changes and create a commit. Returns True if a commit was made."""
    subprocess.run(["git", "-C", str(repo_root), "add", "-A"], check=True)
    result = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--cached", "--quiet"],
    )
    if result.returncode == 0:
        return False  # nothing staged
    subprocess.run(
        ["git", "-C", str(repo_root), "commit", "-m", message],
        check=True,
    )
    return True


def push(repo_root: Path, branch: str = "main") -> None:
    subprocess.run(["git", "-C", str(repo_root), "push", "origin", branch], check=True)
```

- [ ] **Step 5: Run orchestrator test**

```bash
uv run pytest tests/test_check.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Run full suite**

```bash
uv run pytest -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add pipeline/check.py pipeline/git_ops.py tests/test_check.py
git commit -m "feat(pipeline): check.py orchestrator + git commit helper"
```

---

## Phase 8: GitHub Actions + sources.yaml + first run

### Task 8.1: `daily-check.yml` workflow

**Files:**
- Create: `.github/workflows/daily-check.yml`

- [ ] **Step 1: Write the workflow**

Write `.github/workflows/daily-check.yml`:
```yaml
name: Daily Check

on:
  schedule:
    - cron: "0 8 * * *"   # 08:00 UTC daily
  workflow_dispatch: {}

permissions:
  contents: write

concurrency:
  group: daily-check
  cancel-in-progress: false

jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: astral-sh/setup-uv@v3
        with:
          version: "latest"

      - name: Install Python
        run: uv python install 3.12

      - name: Sync deps
        run: uv sync --frozen

      - name: Run daily check
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          ALERT_EMAILS: ${{ secrets.ALERT_EMAILS }}
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: uv run python -m pipeline.check

      - name: Commit + push if changed
        run: |
          git config user.name "ai-ecosystem-tracker[bot]"
          git config user.email "bot@users.noreply.github.com"
          git add -A
          if git diff --cached --quiet; then
            echo "No changes to commit."
          else
            git commit -m "daily-check $(date -u +%F): auto-run"
            git push origin HEAD:${{ github.ref_name }}
          fi
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/daily-check.yml
git commit -m "ci: add daily-check workflow (08:00 UTC)"
```

---

### Task 8.2: Write `sources.yaml` with all 28 v1 entries

**Files:**
- Create: `sources.yaml`

- [ ] **Step 1: Write the 28-entry seed file**

Write `sources.yaml`:
```yaml
# AI Ecosystem Tracker — v1 source list (28 entries)
# To add a new source: append an entry below and open a PR.
# First run after merge is "catch-up" mode (records state, emits zero events).

# ─── Pillar 1: Crawler / Bot documentation (HTML diff) ───

- slug: gptbot
  pillar: crawler
  type: html_page
  url: https://platform.openai.com/docs/gptbot
  display_name: OpenAI GPTBot

- slug: claudebot
  pillar: crawler
  type: html_page
  url: https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler
  display_name: Anthropic ClaudeBot

- slug: google-extended
  pillar: crawler
  type: html_page
  url: https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers
  display_name: Google-Extended

- slug: perplexitybot
  pillar: crawler
  type: html_page
  url: https://docs.perplexity.ai/guides/bots
  display_name: PerplexityBot

- slug: applebot-extended
  pillar: crawler
  type: html_page
  url: https://support.apple.com/en-us/119829
  display_name: Applebot-Extended

- slug: meta-externalagent
  pillar: crawler
  type: html_page
  url: https://developers.facebook.com/docs/sharing/bot/
  display_name: Meta-ExternalAgent

- slug: microsoft-bot-docs
  pillar: crawler
  type: html_page
  url: https://www.bing.com/webmasters/help/which-crawlers-does-bing-use-8c184ec0
  display_name: Microsoft Bingbot / Copilot

- slug: amazonbot
  pillar: crawler
  type: html_page
  url: https://developer.amazon.com/amazonbot
  display_name: Amazonbot

- slug: ccbot
  pillar: crawler
  type: html_page
  url: https://commoncrawl.org/faq
  display_name: Common Crawl CCBot

# ─── Pillar 2: Content ecosystem news (RSS + keyword filter + Haiku) ───

- slug: cloudflare-blog
  pillar: ecosystem
  type: rss_feed
  url: https://blog.cloudflare.com/rss/
  keyword_filter: ["AI bot", "crawler", "scraper", "content", "robots.txt", "training", "AI training"]
  display_name: Cloudflare Blog

- slug: fastly-blog
  pillar: ecosystem
  type: rss_feed
  url: https://www.fastly.com/blog/feed.xml
  keyword_filter: ["AI bot", "crawler", "scraper", "training", "content"]
  display_name: Fastly Blog

- slug: akamai-blog
  pillar: ecosystem
  type: rss_feed
  url: https://www.akamai.com/blog/rss.xml
  keyword_filter: ["bot", "AI", "crawler", "scraper", "training"]
  display_name: Akamai Blog

- slug: datadome-blog
  pillar: ecosystem
  type: rss_feed
  url: https://datadome.co/feed/
  keyword_filter: ["AI", "crawler", "scraper", "bot", "LLM"]
  display_name: DataDome Blog

- slug: uk-cma
  pillar: ecosystem
  type: rss_feed
  url: https://www.gov.uk/government/organisations/competition-and-markets-authority.atom
  keyword_filter: ["AI", "artificial intelligence", "foundation model", "generative"]
  display_name: UK CMA

- slug: eu-commission-digital
  pillar: ecosystem
  type: rss_feed
  url: https://ec.europa.eu/commission/presscorner/api/rss?language=EN
  keyword_filter: ["AI", "artificial intelligence", "generative", "AI Act", "DSA", "DMA"]
  display_name: EU Commission Press

- slug: eu-ai-office
  pillar: ecosystem
  type: rss_feed
  url: https://digital-strategy.ec.europa.eu/en/policies/ai-office/rss
  keyword_filter: ["AI", "code of practice", "GPAI", "model"]
  display_name: EU AI Office

- slug: us-ftc
  pillar: ecosystem
  type: rss_feed
  url: https://www.ftc.gov/news-events/news/press-releases/rss
  keyword_filter: ["AI", "artificial intelligence", "generative", "chatbot", "training data", "large language"]
  display_name: US FTC

- slug: us-copyright-office
  pillar: ecosystem
  type: rss_feed
  url: https://www.copyright.gov/rss/news.rss
  keyword_filter: ["AI", "artificial intelligence", "machine learning", "training"]
  display_name: US Copyright Office

- slug: news-media-alliance
  pillar: ecosystem
  type: rss_feed
  url: https://www.newsmediaalliance.org/feed/
  keyword_filter: ["AI", "artificial intelligence", "LLM", "scraper", "training"]
  display_name: News/Media Alliance

- slug: reddit-corporate
  pillar: ecosystem
  type: rss_feed
  url: https://redditinc.com/blog/rss.xml
  keyword_filter: ["AI", "data", "API", "license", "bot"]
  display_name: Reddit Corporate Blog

# ─── Pillar 3: AI Agent ecosystem (mixed) ───

- slug: ietf-web-bot-auth
  pillar: agent
  type: ietf_draft
  draft_name: draft-cloudflare-httpbis-web-bot-auth
  display_name: IETF Web Bot Auth

- slug: web-bot-auth-repo
  pillar: agent
  type: github_repo
  repo: cloudflareresearch/web-bot-auth
  display_name: Web Bot Auth (spec repo)

- slug: mcp-spec
  pillar: agent
  type: github_repo
  repo: modelcontextprotocol/specification
  pr_labels: ["spec", "rfc"]
  display_name: Model Context Protocol (spec)

- slug: browserbase-blog
  pillar: agent
  type: rss_feed
  url: https://www.browserbase.com/blog/rss.xml
  keyword_filter: ["agent", "bot", "browser", "auth", "MCP"]
  display_name: Browserbase Blog

- slug: cloudflare-research
  pillar: agent
  type: rss_feed
  url: https://blog.cloudflare.com/tag/research/rss/
  keyword_filter: ["bot", "agent", "auth", "identity", "scraper"]
  display_name: Cloudflare Research Blog

- slug: anthropic-news
  pillar: agent
  type: rss_feed
  url: https://www.anthropic.com/news/rss.xml
  keyword_filter: ["agent", "operator", "bot", "crawler", "MCP", "Computer Use", "Claude Code"]
  display_name: Anthropic News

- slug: openai-blog
  pillar: agent
  type: rss_feed
  url: https://openai.com/blog/rss.xml
  keyword_filter: ["agent", "operator", "bot", "crawler", "Assistants", "ChatGPT agents"]
  display_name: OpenAI Blog

- slug: langchain-blog
  pillar: agent
  type: rss_feed
  url: https://blog.langchain.dev/rss/
  keyword_filter: ["agent", "bot", "MCP", "tool use"]
  display_name: LangChain Blog
```

- [ ] **Step 2: Validate yaml loads cleanly**

```bash
uv run python -c "from pipeline.sources import load_sources; import sys; ss=load_sources('sources.yaml'); print(f'{len(ss)} sources'); [print(f'{s.pillar.value} {s.slug}') for s in ss]"
```

Expected: `28 sources` followed by a listing, no errors.

- [ ] **Step 3: Commit**

```bash
git add sources.yaml
git commit -m "feat: seed sources.yaml with 28 v1 tracked sources"
```

---

### Task 8.3: Smoke test — local dry-run

**Files:** (no new files)

- [ ] **Step 1: Export a test API key and run dry-run**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # user provides
uv run python -m pipeline.check --dry-run --only gptbot
```

Expected: fetches the GPTBot doc, reports "first_seen" catch-up, writes nothing (dry-run).

- [ ] **Step 2: Run full dry-run across all sources**

```bash
uv run python -m pipeline.check --dry-run
```

Expected: every source either reports `ok` (caught up) or a specific error for sources whose URLs need revision. Note any failures.

- [ ] **Step 3: Fix broken source URLs inline**

For any source that errors (404, redirect loop, RSS unavailable), update `sources.yaml` with the corrected URL (or fall back to `html_page` on a listings page if the RSS is genuinely unavailable). Commit each fix separately for auditability:

```bash
git add sources.yaml
git commit -m "fix(sources): correct URL for {slug}"
```

- [ ] **Step 4: Run first live pass (no dry-run) locally**

```bash
uv run python -m pipeline.check
```

Expected: 28 snapshots / states written, zero events (catch-up), `data/opt-out-matrix.json` generated.

- [ ] **Step 5: Commit the catch-up baseline**

```bash
git add content/ data/ state/
git commit -m "chore: seed catch-up baseline for 28 sources"
```

- [ ] **Step 6: Push to GitHub**

```bash
git remote add origin git@github.com:<your-user>/ai-ecosystem-tracker.git
git push -u origin main
```

- [ ] **Step 7: Configure GitHub repo secrets**

In GitHub repo settings → Secrets and variables → Actions, add:
- `ANTHROPIC_API_KEY`
- `ALERT_EMAILS` (placeholder — Plan 3 will use it)
- `RESEND_API_KEY` (placeholder — Plan 3 will use it)

- [ ] **Step 8: Manually trigger the workflow**

In the GitHub UI: Actions → Daily Check → Run workflow.

Expected: workflow succeeds. Check the commit log — one new commit titled `daily-check YYYY-MM-DD: auto-run` may appear if any sources changed since the local baseline; otherwise the step reports "No changes to commit."

- [ ] **Step 9: Done — Plan 1 complete**

```bash
git log --oneline
```

Expected: a clean history of commits from Task 0.1 through Task 8.3.

---

## Self-Review Checklist (for the plan author)

Spec coverage:

- § 1–2 (overview, audience) — non-implementable; informational.
- § 3 (28 sources) — covered by Task 8.2.
- § 4 (architecture) — pipeline side realized by Tasks 0–8; site (Plan 2) and distribution (Plan 3) out of scope of this plan.
- § 5 (data layout) — directory scaffolding (0.1), snapshots (7.1), events (5.2), state (1.2), data/*.json (6.1), health.json (7.2).
- § 6.1 (check.py flow, per-type dispatch) — Task 7.2.
- § 6.2 (error handling) — Task 7.2 covers per-source isolation + consecutive_failures; fallback-on-LLM-error is **intentionally left to implementation** inside `analyze_change` retries (iterated with real traffic).
- § 6.3 (relevance funnel) — Tasks 4.1 + 4.2, wired in Task 7.2.
- § 6.4 (LLM usage / caching) — Task 5.1 (prompt caching), Task 6.1 (Haiku extractor).
- § 6.5 (pillar-specific prompt behavior) — Task 5.1 (`_CRAWLER_ADDON` vs `_NEWS_ADDON`).
- § 6.6 (digest.py) — **Plan 3**.
- § 6.7 (adding a new source) — Task 8.2 yaml layout + `--dry-run --only` flags in `check.py` Task 7.2.
- § 7 (frontend) — **Plan 2**.
- § 8 (distribution: crawler alert, digest, RSS) — **Plan 3** (alert wiring hooks into `check.py` but is implemented in Plan 3).
- § 9 (operations) — workflow secrets in Task 8.1; `data/health.json` in Task 7.2.

Placeholder scan: ✓ no TBDs in any step. Every step has runnable commands or complete code.

Type consistency: ✓ `Source`, `SourceType`, `Pillar`, `FetchResult`, `ResultMode`, `CandidateItem`, `AnalysisResult`, `SourceState` names are consistent across all tasks.

---

**Plan complete and saved to `docs/superpowers/plans/2026-04-18-plan-1-pipeline.md`. Plans 2 (static site) and 3 (distribution) will be written after Plan 1 is implemented, so Plan 2 can read the real output shape and Plan 3 can hook into the concrete `check.py`.**
