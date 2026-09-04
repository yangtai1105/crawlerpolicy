# Daily X Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a metered xAI X Search discovery lane, publish a date-led Daily Brief from the highest-value feed items, and expose persistent evidence-backed insight threads.

**Architecture:** Model five narrow X searches as optional commentary sources in the existing fetch/evidence/analyze/publish pipeline. The xAI boundary returns validated per-post candidates and usage metadata; Gemini remains the only editorial model. Daily editions and insight threads are deterministic derived data built from published feed records, while verified development and weekly-intelligence invariants remain unchanged.

**Tech Stack:** Python 3.12, Pydantic 2, httpx, pytest/respx, Gemini structured generation, xAI Responses API `x_search`, Astro 6, TypeScript, Node test runner.

**Spec:** `docs/superpowers/specs/2026-09-03-daily-x-intelligence-design.md`

## Global Constraints

- Public editorial language is English.
- A Daily Brief contains zero to five items and never fills a quota with generic AI news.
- xAI is discovery only; Gemini remains the editorial analysis provider.
- X-only material is `signal` and cannot create developments, update durable trends, or support Weekly Intelligence.
- Only official xAI/X interfaces are used; X is never scraped or browser-automated.
- X discovery is optional and defaults to shadow mode for its seven-window trial.
- The default hard cap is six successful X Search calls per day and the monthly soft budget is USD 10.
- Missing or failed xAI access degrades only the discovery lane and never blocks direct-source publication.
- Existing direct-source, backfill, event, trend, weekly, and RSS behavior must remain compatible.

---

### Task 1: Configure optional X discovery sources and runtime limits

**Files:**
- Modify: `pipeline/config.py`
- Modify: `pipeline/sources.py`
- Modify: `sources.yaml`
- Modify: `tests/test_config.py`
- Modify: `tests/test_sources.py`

**Interfaces:**
- Produces: `SourceType.XAI_SEARCH`
- Produces: `Source.x_handles: list[str]`, `Source.lookback_hours: int`, `Source.shadow: bool`
- Produces: `Config.xai_api_key`, `Config.xai_discovery_model`, `Config.xai_max_daily_search_calls`, `Config.xai_monthly_soft_budget_usd`
- Consumes: existing `Source.default_tracks`, `SourceTier.COMMENTARY`, and `SourceRole.REPORTING`

- [x] **Step 1: Write failing configuration and source-schema tests**

```python
def test_config_reads_xai_discovery_limits(monkeypatch, tmp_path):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    monkeypatch.setenv("XAI_DISCOVERY_MODEL", "grok-4.6")
    monkeypatch.setenv("XAI_MAX_DAILY_SEARCH_CALLS", "4")
    monkeypatch.setenv("XAI_MONTHLY_SOFT_BUDGET_USD", "7.5")

    cfg = Config.from_env()

    assert cfg.xai_api_key == "xai-test"
    assert cfg.xai_discovery_model == "grok-4.6"
    assert cfg.xai_max_daily_search_calls == 4
    assert cfg.xai_monthly_soft_budget_usd == 7.5


def test_xai_search_requires_query_and_commentary_tier():
    with pytest.raises(ValidationError):
        Source(
            slug="x-access",
            type=SourceType.XAI_SEARCH,
            display_name="X access signals",
            default_tracks=[Track.CRAWLER_CONTROLS],
            tier=SourceTier.PRIMARY,
            role=SourceRole.REPORTING,
            query="crawler policy",
        )
```

- [x] **Step 2: Run the focused tests and verify RED**

Run: `uv run pytest tests/test_config.py tests/test_sources.py -q`

Expected: failures because `XAI_SEARCH` and the xAI configuration fields do not exist.

- [x] **Step 3: Add the minimal schema and environment parsing**

```python
class SourceType(StrEnum):
    XAI_SEARCH = "xai_search"


class Source(BaseModel):
    x_handles: list[str] = Field(default_factory=list, max_length=20)
    lookback_hours: int = Field(default=36, ge=1, le=72)
    shadow: bool = True

    @model_validator(mode="after")
    def _validate_xai_search(self) -> Self:
        if self.type is SourceType.XAI_SEARCH:
            if not self.query:
                raise ValueError(f"source {self.slug}: xai_search requires `query`")
            if self.tier is not SourceTier.COMMENTARY:
                raise ValueError(f"source {self.slug}: xai_search must use commentary tier")
        return self
```

Add five enabled, optional `xai_search` entries to `sources.yaml`, one per public front. Use this exact initial account set; shadow-run evidence will determine later additions and removals:

```yaml
- slug: x-access-discovery
  type: xai_search
  query: >-
    Find consequential changes to AI crawler policies, robots directives,
    AI search visibility, citations, referrals, or web indexing.
  x_handles: [Cloudflare, GoogleSearchC, OpenAI, AnthropicAI, perplexity_ai, CommonCrawl, sengineland]
  lookback_hours: 36
  shadow: true
  display_name: X — Access & Discovery
  default_tracks: [crawler-controls, search-discovery]
  tier: commentary
  role: reporting

- slug: x-agents-discovery
  type: xai_search
  query: >-
    Find consequential changes to AI agent traffic, Web Bot Auth,
    authentication, delegation, MCP, or agent identity standards.
  x_handles: [Cloudflare, IETF, W3C, OpenAI, AnthropicAI, arstechnica]
  lookback_hours: 36
  shadow: true
  display_name: X — Agents & Identity
  default_tracks: [agentic-web, standards-protocols]
  tier: commentary
  role: reporting

- slug: x-rights-discovery
  type: xai_search
  query: >-
    Find consequential content licensing, training-rights, pay-per-use,
    publisher compensation, or machine-readable rights developments.
  x_handles: [Cloudflare, Reddit, TechCrunch, WIRED, NiemanLab, Digiday, pressgazette]
  lookback_hours: 36
  shadow: true
  display_name: X — Rights & Markets
  default_tracks: [licensing-monetization, asset-rights]
  tier: commentary
  role: reporting

- slug: x-governance-discovery
  type: xai_search
  query: >-
    Find consequential regulator action, litigation, competition remedies,
    copyright decisions, or disclosure rules affecting AI and web content.
  x_handles: [FTC, EU_Commission, CMAgovUK, TechCrunch, verge, WIRED, 404mediaco]
  lookback_hours: 36
  shadow: true
  display_name: X — Governance & Law
  default_tracks: [policy-regulation, litigation-legal]
  tier: commentary
  role: reporting

- slug: x-measurement-discovery
  type: xai_search
  query: >-
    Find new measurements of AI crawler volume, referral ratios,
    bot identity, publisher traffic, conversion, or compensation.
  x_handles: [Cloudflare, CommonCrawl, Digiday, NiemanLab, sengineland, ppcland]
  lookback_hours: 36
  shadow: true
  display_name: X — Measurement & Economics
  default_tracks: [measurement-economics]
  tier: commentary
  role: reporting
```

- [x] **Step 4: Run focused tests and verify GREEN**

Run: `uv run pytest tests/test_config.py tests/test_sources.py -q`

Expected: all focused tests pass.

- [x] **Step 5: Commit the configuration boundary**

```bash
git add pipeline/config.py pipeline/sources.py sources.yaml tests/test_config.py tests/test_sources.py
git commit -m "feat: configure x discovery sources"
```

---

### Task 2: Implement the metered xAI X Search fetcher

**Files:**
- Create: `pipeline/fetchers/xai_search.py`
- Create: `tests/test_fetchers/test_xai_search.py`
- Modify: `pipeline/fetchers/base.py`

**Interfaces:**
- Consumes: `Source` with `type == SourceType.XAI_SEARCH`
- Produces: `fetch_xai_search(source: Source, *, api_key: str, model: str, now: datetime, client: httpx.AsyncClient | None = None) -> FetchResult`
- Produces: `CandidateItem.metadata` containing `author_handle`, `post_url`, `linked_urls`, and provider citations
- Produces: `FetchResult.metadata` containing `x_search_calls`, `estimated_tool_cost_usd`, and `model`

- [ ] **Step 1: Write failing parser and HTTP-boundary tests**

```python
@respx.mock
async def test_xai_search_returns_deduplicated_per_post_candidates(x_source):
    route = respx.post("https://api.x.ai/v1/responses").mock(
        return_value=Response(200, json=XAI_RESPONSE)
    )

    result = await fetch_xai_search(
        x_source,
        api_key="xai-test",
        model="grok-4.6",
        now=datetime(2026, 9, 3, 8, tzinfo=UTC),
    )

    assert route.called
    assert result.mode is ResultMode.PER_ITEM
    assert [item.guid for item in result.items] == ["2031535503443374365"]
    assert result.metadata["x_search_calls"] == 1
    assert result.metadata["estimated_tool_cost_usd"] == 0.005


async def test_xai_search_rejects_post_outside_requested_window(x_source):
    result = await fetch_xai_search(
        x_source,
        api_key="xai-test",
        model="grok-4.6",
        now=datetime(2026, 9, 3, 8, tzinfo=UTC),
        client=FakeXaiClient(response=STALE_XAI_RESPONSE),
    )

    assert result.items == []
```

The response fixture must mirror a real Responses API result with `output`, `citations`, `usage`, and `server_side_tool_usage` fields.

- [ ] **Step 2: Run the fetcher tests and verify RED**

Run: `uv run pytest tests/test_fetchers/test_xai_search.py -q`

Expected: collection failure because `pipeline.fetchers.xai_search` does not exist.

- [ ] **Step 3: Implement validated candidate parsing and the API call**

```python
class XSearchCandidate(BaseModel):
    post_id: str
    post_url: AnyHttpUrl
    author_handle: str
    published_at: datetime
    title: str
    synopsis: str
    linked_urls: list[AnyHttpUrl] = Field(default_factory=list)


class XSearchEnvelope(BaseModel):
    candidates: list[XSearchCandidate] = Field(default_factory=list)


async def fetch_xai_search(
    source: Source,
    *,
    api_key: str,
    model: str,
    now: datetime,
    client: httpx.AsyncClient | None = None,
) -> FetchResult:
    window_start = now - timedelta(hours=source.lookback_hours)
    payload = build_x_search_payload(source, model, window_start, now)
    response = await post_xai_response(client, api_key, payload)
    envelope = parse_x_search_envelope(response)
    items = candidates_to_items(envelope.candidates, window_start, now)
    calls = int(response.get("server_side_tool_usage", {}).get("SERVER_SIDE_TOOL_X_SEARCH", 0))
    return FetchResult(
        mode=ResultMode.PER_ITEM,
        items=items,
        metadata={
            "x_search_calls": calls,
            "estimated_tool_cost_usd": round(calls * 0.005, 6),
            "model": model,
        },
    )
```

The request payload must set `tools: [{"type": "x_search", "from_date": "2026-09-02", "to_date": "2026-09-03"}]` for the example window, derive those dates from the runtime window in production, add `allowed_x_handles` only when configured, cap `max_turns` at two, and demand one JSON object matching `XSearchEnvelope`.

- [ ] **Step 4: Run fetcher tests and verify GREEN**

Run: `uv run pytest tests/test_fetchers/test_xai_search.py -q`

Expected: all xAI fetcher tests pass without a real network call.

- [ ] **Step 5: Commit the fetcher**

```bash
git add pipeline/fetchers/base.py pipeline/fetchers/xai_search.py tests/test_fetchers/test_xai_search.py
git commit -m "feat: fetch metered x search candidates"
```

---

### Task 3: Integrate X discovery with evidence, shadow mode, and health

**Files:**
- Modify: `pipeline/check.py`
- Modify: `pipeline/evidence.py`
- Modify: `pipeline/health.py`
- Modify: `tests/test_check.py`
- Modify: `tests/test_evidence.py`
- Modify: `.github/workflows/daily-check.yml`

**Interfaces:**
- Consumes: `fetch_xai_search` and its `FetchResult.metadata`
- Produces: `EvidenceRecord.supporting_urls`, `EvidenceRecord.discovery_metadata`
- Produces: health payload key `discovery` with status, calls, estimated cost, candidate count, and shadow state
- Preserves: `publication_status(SourceTier.COMMENTARY) == PublicationStatus.SIGNAL`

- [ ] **Step 1: Write failing orchestration tests**

```python
async def test_missing_xai_key_degrades_only_x_source(repo):
    _write_direct_and_x_sources(repo)
    blockers = preflight_dependency_errors(
        load_sources(repo / "sources.yaml"),
        {"GEMINI_API_KEY": "gemini-test", "XAI_API_KEY": ""},
    )

    assert blockers["x-access"].stage == "fetch"
    assert blockers["x-access"].critical is False
    assert "direct-source" not in blockers


async def test_shadow_candidate_is_saved_but_not_published(repo):
    health = await run_check(
        repo_root=repo,
        now=datetime(2026, 9, 3, 8, tzinfo=UTC),
        fetch_dispatch=AsyncMock(return_value=X_FETCH_RESULT),
        analyze_change=AsyncMock(return_value=_material_analysis()),
    )

    assert len(list((repo / "content/evidence/x-access").glob("*.json"))) == 1
    assert list((repo / "content/feed").glob("*.md")) == []
    assert health["discovery"]["candidate_count"] == 1
    assert health["status"] == "healthy"
```

- [ ] **Step 2: Run the focused orchestration tests and verify RED**

Run: `uv run pytest tests/test_check.py tests/test_evidence.py -q`

Expected: failures because xAI preflight, discovery metadata, and shadow publication behavior do not exist.

- [ ] **Step 3: Add optional-blocker and shadow semantics**

```python
@dataclass(frozen=True)
class DependencyBlocker:
    stage: str
    message: str
    critical: bool = True


if source.type is SourceType.XAI_SEARCH and not present("XAI_API_KEY"):
    blockers[source.slug] = DependencyBlocker(
        stage="fetch",
        message="XAI_API_KEY is missing",
        critical=False,
    )
```

Dispatch xAI sources with runtime configuration, aggregate successful calls and candidates, save candidate evidence before any Gemini call, and mark shadow evidence `ANALYZED` with `discovery_metadata["shadow"] == True`. When `shadow` is false, let the existing analysis path publish the commentary-tier item as `signal`; `should_promote` already prevents event and trend promotion.

After `build_run_health`, downgrade an otherwise critical result caused exclusively by optional xAI sources to `degraded`. Preserve critical status for any required direct-source failure.

- [ ] **Step 4: Add the production secret and defaults**

```yaml
XAI_API_KEY: ${{ secrets.XAI_API_KEY }}
XAI_DISCOVERY_MODEL: grok-4.6
XAI_MAX_DAILY_SEARCH_CALLS: "6"
XAI_MONTHLY_SOFT_BUDGET_USD: "10"
```

- [ ] **Step 5: Run orchestration tests and verify GREEN**

Run: `uv run pytest tests/test_check.py tests/test_evidence.py tests/test_health.py -q`

Expected: all focused orchestration tests pass.

- [ ] **Step 6: Commit the optional discovery lane**

```bash
git add pipeline/check.py pipeline/evidence.py pipeline/health.py tests/test_check.py tests/test_evidence.py .github/workflows/daily-check.yml
git commit -m "feat: integrate optional x discovery lane"
```

---

### Task 4: Generate one deterministic Daily Brief edition per run date

**Files:**
- Create: `pipeline/daily_brief.py`
- Create: `tests/test_daily_brief.py`
- Modify: `pipeline/config.py`
- Modify: `pipeline/check.py`

**Interfaces:**
- Produces: `DailyBrief`, `DailyBriefItem`, `build_daily_brief(feed_dir: Path, edition_date: date, generated_at: datetime) -> DailyBrief`
- Produces: `save_daily_brief(path: Path, brief: DailyBrief) -> None`
- Produces: `Config.daily_dir`
- Consumes: feed frontmatter fields `slug`, `detected_at`, `published_at`, `importance`, `status`, and `backfilled`

- [ ] **Step 1: Write failing daily-selection tests**

```python
def test_daily_brief_uses_detection_date_and_caps_at_five(tmp_path):
    write_feed_fixtures(tmp_path, detected_on=date(2026, 9, 3), count=7)

    brief = build_daily_brief(
        feed_dir=tmp_path,
        edition_date=date(2026, 9, 3),
        generated_at=datetime(2026, 9, 3, 8, tzinfo=UTC),
    )

    assert brief.status == "published"
    assert len(brief.items) == 5
    assert [item.importance for item in brief.items] == [0.95, 0.90, 0.85, 0.80, 0.75]


def test_daily_brief_writes_truthful_quiet_edition(tmp_path):
    brief = build_daily_brief(
        feed_dir=tmp_path,
        edition_date=date(2026, 9, 3),
        generated_at=datetime(2026, 9, 3, 8, tzinfo=UTC),
    )

    assert brief.status == "quiet"
    assert brief.items == []
    assert brief.note == "No material ecosystem developments were published in this daily window."
```

- [ ] **Step 2: Run daily-brief tests and verify RED**

Run: `uv run pytest tests/test_daily_brief.py -q`

Expected: collection failure because `pipeline.daily_brief` does not exist.

- [ ] **Step 3: Implement the deterministic edition builder**

```python
class DailyBriefItem(BaseModel):
    slug: str
    status: PublicationStatus
    importance: float = Field(ge=0, le=1)
    published_at: datetime


class DailyBrief(BaseModel):
    schema_version: int = 1
    edition_date: date
    generated_at: datetime
    status: Literal["published", "quiet"]
    note: str
    items: list[DailyBriefItem] = Field(default_factory=list, max_length=5)


def build_daily_brief(*, feed_dir: Path, edition_date: date, generated_at: datetime) -> DailyBrief:
    candidates = [item for item in load_feed_records(feed_dir) if item.detected_at.date() == edition_date and not item.backfilled]
    ordered = sorted(candidates, key=lambda item: (item.importance, item.published_at), reverse=True)[:5]
    return DailyBrief(
        edition_date=edition_date,
        generated_at=generated_at,
        status="published" if ordered else "quiet",
        note="Highest-consequence developments detected in this daily window." if ordered else "No material ecosystem developments were published in this daily window.",
        items=[DailyBriefItem.model_validate(item.model_dump()) for item in ordered],
    )
```

Call and atomically save the edition after source processing, including degraded runs. A rerun replaces only the same date's derived JSON and remains idempotent.

- [ ] **Step 4: Run daily-brief and orchestration tests and verify GREEN**

Run: `uv run pytest tests/test_daily_brief.py tests/test_check.py -q`

Expected: all focused tests pass and a run writes `data/daily/YYYY-MM-DD.json`.

- [ ] **Step 5: Commit daily editions**

```bash
git add pipeline/daily_brief.py pipeline/config.py pipeline/check.py tests/test_daily_brief.py tests/test_check.py
git commit -m "feat: publish dated daily brief editions"
```

---

### Task 5: Build persistent insight threads from feed trend signals

**Files:**
- Create: `pipeline/insight_threads.py`
- Create: `tests/test_insight_threads.py`
- Modify: `pipeline/feed_writer.py`
- Modify: `pipeline/config.py`
- Modify: `pipeline/check.py`
- Modify: `site/src/content.config.ts`
- Modify: `tests/test_feed_writer.py`

**Interfaces:**
- Produces: feed frontmatter `trend_signals: list[str]`
- Produces: `InsightThreadRegistry`, `update_insight_threads(feed_dir: Path, path: Path, now: datetime) -> InsightThreadRegistry`
- Produces: `Config.insight_threads_file`
- Consumes: feed `status`, `development_slug`, `trend_signals`, Insight body section, and `detected_at`

- [ ] **Step 1: Write failing persistence and evidence-gating tests**

```python
def test_signal_adds_context_without_verified_evidence(tmp_path):
    write_feed_record(
        tmp_path / "feed",
        slug="x-signal",
        status="signal",
        trend_signals=["verifiable-agent-identity"],
        development_slug=None,
    )

    registry = update_insight_threads(
        feed_dir=tmp_path / "feed",
        path=tmp_path / "insight-threads.json",
        now=datetime(2026, 9, 3, 8, tzinfo=UTC),
    )

    thread = registry.threads[0]
    assert thread.related_feed_slugs == ["x-signal"]
    assert thread.verified_development_slugs == []
    assert thread.confidence == "low"


def test_verified_item_adds_durable_thread_evidence(tmp_path):
    write_feed_record(
        tmp_path / "feed",
        slug="verified-change",
        status="verified",
        trend_signals=["verifiable-agent-identity"],
        development_slug="signed-agents-enforced",
    )

    registry = update_insight_threads(
        feed_dir=tmp_path / "feed",
        path=tmp_path / "insight-threads.json",
        now=datetime(2026, 9, 3, 8, tzinfo=UTC),
    )

    assert registry.threads[0].verified_development_slugs == ["signed-agents-enforced"]
    assert registry.threads[0].confidence == "high"
```

- [ ] **Step 2: Run insight-thread tests and verify RED**

Run: `uv run pytest tests/test_insight_threads.py tests/test_feed_writer.py -q`

Expected: failure because trend signals are not persisted and the registry does not exist.

- [ ] **Step 3: Persist trend signals and derive stable threads**

```python
class InsightThread(BaseModel):
    key: str
    title: str
    thesis: str
    direction: Literal["emerging", "developing"]
    confidence: Literal["low", "medium", "high"]
    first_observed_at: datetime
    last_updated_at: datetime
    related_feed_slugs: list[str] = Field(default_factory=list)
    verified_development_slugs: list[str] = Field(default_factory=list)


def confidence_for_thread(verified_count: int, reported_count: int) -> str:
    if verified_count:
        return "high"
    if reported_count:
        return "medium"
    return "low"
```

Normalize each trend signal to a stable lowercase hyphenated key. Use the newest item's Insight paragraph as the current thesis, deduplicate references, and update timestamps only when a new feed slug is attached. Reprocessing the same feed set must leave the JSON byte-stable.

- [ ] **Step 4: Run insight and feed tests and verify GREEN**

Run: `uv run pytest tests/test_insight_threads.py tests/test_feed_writer.py -q`

Expected: all focused tests pass.

- [ ] **Step 5: Commit persistent insight threads**

```bash
git add pipeline/insight_threads.py pipeline/feed_writer.py pipeline/config.py pipeline/check.py site/src/content.config.ts tests/test_insight_threads.py tests/test_feed_writer.py
git commit -m "feat: track persistent ecosystem insights"
```

---

### Task 6: Make the home page a Daily Brief with developing insights

**Files:**
- Create: `site/src/lib/daily.ts`
- Create: `site/src/lib/insight-threads.ts`
- Create: `site/src/components/InsightThreadCard.astro`
- Modify: `site/src/pages/index.astro`
- Modify: `site/src/components/FeedCard.astro`
- Modify: `site/src/styles/global.css`
- Modify: `site/test/feed-publication.test.mjs`
- Create: `site/test/fixtures/daily-brief.json`
- Create: `site/test/fixtures/insight-threads.json`

**Interfaces:**
- Consumes: `data/daily/*.json`, `data/insight-threads.json`, and the feed collection
- Produces: `loadLatestDailyBrief()` and `loadInsightThreads()`
- Produces: home-page sections `Today's Brief`, `Developing insights`, `Latest from the field`, and `Weekly synthesis`

- [ ] **Step 1: Write failing built-output assertions**

```javascript
test("home page leads with the dated brief and durable insight context", async () => {
  const home = await readFile(resolve(siteRoot, "dist/index.html"), "utf8");

  assert.match(home, /Today(?:'|’)s Brief/);
  assert.match(home, /September 3, 2026/);
  assert.match(home, /Developing insights/);
  assert.match(home, /Verifiable Agent Identity/);
  assert.match(home, /1 verified development/);
  assert.ok(home.indexOf("Today’s Brief") < home.indexOf("Latest from the field"));
});
```

- [ ] **Step 2: Run the site test and verify RED**

Run: `cd site && node --test test/feed-publication.test.mjs`

Expected: failure because the dated-edition and developing-insight sections are absent.

- [ ] **Step 3: Implement the date-led reading hierarchy**

Use the existing Field Ledger palette and typography. The page's signature element becomes a vertical “evidence seam” connecting each Daily Brief item to its status and source; it encodes provenance rather than adding decoration.

```astro
<header class="daily-heading">
  <p class="utility-label">Today’s Brief</p>
  <h1>{editionDate}</h1>
  <p>{brief.note}</p>
</header>

<section class="developing-insights" aria-labelledby="developing-title">
  <div class="section-heading">
    <div><p class="utility-label">Over time</p><h2 id="developing-title">Developing insights</h2></div>
    <p>Persistent reads supported by accumulating evidence.</p>
  </div>
  <div class="insight-grid">
    {threads.slice(0, 6).map((thread) => <InsightThreadCard thread={thread} />)}
  </div>
</section>
```

Daily Brief item order must come from the edition JSON, not from a 48-hour heuristic. Older feed items remain under “Latest from the field.” Backfilled content never becomes today's lead.

- [ ] **Step 4: Run Astro checks and built-output tests and verify GREEN**

Run: `cd site && npm run check && node --test test/feed-publication.test.mjs`

Expected: zero Astro errors and all Node tests pass.

- [ ] **Step 5: Commit the reading experience**

```bash
git add site/src/lib/daily.ts site/src/lib/insight-threads.ts site/src/components/InsightThreadCard.astro site/src/pages/index.astro site/src/components/FeedCard.astro site/src/styles/global.css site/test
git commit -m "feat: present daily brief and developing insights"
```

---

### Task 7: Verify the full pipeline, document setup, and inspect the rendered site

**Files:**
- Modify: `README.md`
- Modify: `site/README.md`
- Modify: `docs/superpowers/plans/2026-09-03-daily-x-intelligence.md`

**Interfaces:**
- Documents: `XAI_API_KEY`, cost controls, shadow mode, the seven-window promotion criterion, local dry runs, and GitHub Secrets setup
- Verifies: all Python tests, lint, Astro type checks, production build, and desktop/mobile visual behavior

- [ ] **Step 1: Document exact setup and operating commands**

```bash
export XAI_API_KEY="xai-your-key"
export GEMINI_API_KEY="your-gemini-key"
uv run python -m pipeline.check --only x-access-discovery
uv run python -m pipeline.check
```

Explain that the xAI sources initially save candidates in shadow mode and how to inspect health `discovery` metrics before setting their `shadow` fields to `false` after seven acceptable windows.

- [ ] **Step 2: Run the complete Python verification suite**

Run: `uv run pytest -q && uv run ruff check pipeline tests`

Expected: every Python test passes and Ruff reports no violations.

- [ ] **Step 3: Run the complete site verification suite**

Run: `cd site && npm run check && npm run build && node --test test/*.test.mjs`

Expected: Astro reports zero errors, the production build succeeds, and all Node tests pass.

- [ ] **Step 4: Run a credential-free production dry run**

Run: `env -u XAI_API_KEY uv run python -m pipeline.check --dry-run`

Expected: direct sources still run, X discovery is reported unavailable/degraded, no files are written, and the process is not critical solely because xAI is missing.

- [ ] **Step 5: Inspect desktop and mobile renders**

Start the site with `cd site && npm run dev -- --host 127.0.0.1`, then inspect `/` at approximately 1440×1000 and 390×844. Verify hierarchy, evidence-seam alignment, readable line length, focus visibility, status text, overflow, quiet state, and reduced-motion behavior.

- [ ] **Step 6: Mark completed checklist items and commit documentation**

```bash
git add README.md site/README.md docs/superpowers/plans/2026-09-03-daily-x-intelligence.md
git commit -m "docs: explain daily x intelligence operations"
```

- [ ] **Step 7: Push `main` after final verification**

```bash
git push origin main
```

Expected: `origin/main` advances to the verified implementation commit.
