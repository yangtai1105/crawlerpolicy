# Readable Ecosystem Feed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn Crawler Policy into a Gemini-powered, feed-first English publication with readable daily analysis, deterministic evidence levels, and the approved Signal Prism interface.

**Architecture:** Direct source fetchers continue to persist immutable evidence before analysis. A provider-neutral structured-model interface backed by Gemini 3.7 produces feed analysis; deterministic source-tier rules publish `verified`, `reported`, or `signal` feed records, while only verified material records enter the existing development/trend pipeline. Astro loads the new feed collection for the home page, detail pages, and RSS, while preserving the existing development, weekly, source, and legacy archive records.

**Tech Stack:** Python 3.12, Pydantic 2, google-genai, pytest, Astro, TypeScript, Astro Content Collections, CSS

**Spec:** `docs/superpowers/specs/2026-08-30-readable-ecosystem-feed-design.md`

## Global Constraints

- Public editorial content is English.
- Publication cutoff is exactly `2026-08-30T00:00:00Z` unless overridden by `PUBLICATION_CUTOFF`.
- Gemini analysis defaults to model ID `gemini-3.7-flash` and uses `GEMINI_API_KEY`.
- Anthropic is not a runtime or workflow dependency.
- Evidence is persisted before any model call and survives failed analysis.
- Only `verified` plus `material` items may update developments, trends, or weekly intelligence.
- `reported` and `signal` items may appear in the daily feed but never independently update trends.
- Existing schema-v1 records remain isolated in the Legacy Archive.
- The home page must retain the last published feed during provider failures.
- Status must always be expressed in text as well as color.
- Responsive support extends to 320 CSS pixels and respects reduced motion.

---

### Task 1: Provider-neutral Gemini structured model

**Files:**
- Create: `pipeline/model_provider.py`
- Modify: `pipeline/config.py`
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Test: `tests/test_model_provider.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Produces: `StructuredModel.generate(response_model, system_instruction, prompt)`.
- Produces: `GeminiStructuredModel(api_key: str, model: str)`.
- Produces: `ProviderFailure(kind, message)` with kinds `authentication`, `quota`, `billing`, and `transient`.
- Produces: `Config.gemini_api_key`, `Config.gemini_analysis_model`, and `Config.publication_cutoff`.

- [ ] **Step 1: Write failing provider and configuration tests**

```python
async def test_gemini_provider_parses_structured_json():
    client = MagicMock()
    client.aio.models.generate_content = AsyncMock(
        return_value=MagicMock(text='{"is_relevant":true,"reason":"Crawler policy"}')
    )
    provider = GeminiStructuredModel(api_key="key", model="gemini-3.7-flash", client=client)
    result = await provider.generate(
        response_model=RelevanceVerdict,
        system_instruction="Classify.",
        prompt="A crawler policy changed.",
    )
    assert result.is_relevant is True
    assert client.aio.models.generate_content.await_args.kwargs["model"] == "gemini-3.7-flash"


def test_config_defaults_to_gemini_and_publication_cutoff(monkeypatch, tmp_path):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    cfg = Config.from_env()
    assert cfg.gemini_api_key == "gemini-key"
    assert cfg.gemini_analysis_model == "gemini-3.7-flash"
    assert cfg.publication_cutoff.isoformat() == "2026-08-30T00:00:00+00:00"
```

- [ ] **Step 2: Run the new tests and confirm they fail because the interfaces do not exist**

Run: `uv run pytest tests/test_model_provider.py tests/test_config.py -q`  
Expected: import or attribute failures for `GeminiStructuredModel` and Gemini configuration fields.

- [ ] **Step 3: Implement the structured model and failure classification**

```python
T = TypeVar("T", bound=BaseModel)


class StructuredModel(Protocol):
    async def generate(
        self,
        *,
        response_model: type[T],
        system_instruction: str,
        prompt: str,
    ) -> T:
        raise NotImplementedError


class GeminiStructuredModel:
    async def generate(self, *, response_model, system_instruction, prompt):
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_model,
                    temperature=0.2,
                ),
            )
            return response_model.model_validate_json(response.text)
        except Exception as error:
            raise classify_provider_failure(error) from error
```

Remove `anthropic` from `pyproject.toml`, add the three Gemini configuration fields, and regenerate the lock with `uv lock`.

- [ ] **Step 4: Run provider/config tests**

Run: `uv run pytest tests/test_model_provider.py tests/test_config.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/model_provider.py pipeline/config.py pyproject.toml uv.lock tests/test_model_provider.py tests/test_config.py
git commit -m "refactor: add Gemini structured model provider"
```

### Task 2: Feed analysis and deterministic publication model

**Files:**
- Modify: `pipeline/analyzer.py`
- Modify: `pipeline/relevance.py`
- Create: `pipeline/feed.py`
- Create: `pipeline/feed_writer.py`
- Modify: `pipeline/event_writer.py`
- Test: `tests/test_analyzer.py`
- Create: `tests/test_feed.py`
- Create: `tests/test_feed_writer.py`
- Modify: `tests/test_relevance.py`

**Interfaces:**
- Consumes: `StructuredModel.generate(response_model, system_instruction, prompt)` from Task 1.
- Produces: `AnalysisResult` fields `summary`, `insight`, `implication`, and `why_it_matters` alongside the existing materiality fields.
- Produces: `PublicationStatus(StrEnum)` values `verified`, `reported`, and `signal`.
- Produces: `publication_status(source: Source) -> PublicationStatus`.
- Produces: `write_feed_item(root, source, analysis, status, evidence_ids, source_urls, event_date, detected_at, unified_diff, development_slug=None) -> Path` in `content/feed/`.
- Produces: `should_promote(status, analysis) -> bool`.

- [ ] **Step 1: Write failing editorial-schema and publication-rule tests**

```python
def test_source_tier_determines_publication_status():
    assert publication_status(source_for(SourceTier.PRIMARY)) is PublicationStatus.VERIFIED
    assert publication_status(source_for(SourceTier.MEASUREMENT)) is PublicationStatus.VERIFIED
    assert publication_status(source_for(SourceTier.SPECIALIST)) is PublicationStatus.REPORTED
    assert publication_status(source_for(SourceTier.COMMENTARY)) is PublicationStatus.SIGNAL


def test_only_verified_material_analysis_promotes():
    analysis = analysis_result(change_kind="material")
    assert should_promote(PublicationStatus.VERIFIED, analysis) is True
    assert should_promote(PublicationStatus.REPORTED, analysis) is False
    assert should_promote(PublicationStatus.SIGNAL, analysis) is False


async def test_analyzer_generates_four_editorial_layers(fake_model, crawler_source):
    fake_model.generate.return_value = AnalysisResult(
        change_kind="material",
        importance=0.8,
        title="Signed agents become enforceable at the edge",
        summary="Cloudflare documented a signed-agent control.",
        insight="Identity is becoming infrastructure.",
        implication="Sites can distinguish accountable clients.",
        why_it_matters="Crawler policy can become enforceable and auditable.",
        primary_track=Track.AGENTIC_WEB,
        tracks=[Track.AGENTIC_WEB, Track.CRAWLER_CONTROLS],
        actors=["Cloudflare"],
        trend_signals=["verifiable-agent-identity"],
        confidence="high",
    )
    result = await analyze_change(model=fake_model, source=crawler_source, prev_content="old", curr_content="new", unified_diff="+signed")
    assert result.insight == "Identity is becoming infrastructure."
    assert result.why_it_matters.startswith("Crawler policy")
```

- [ ] **Step 2: Run the tests and confirm RED**

Run: `uv run pytest tests/test_analyzer.py tests/test_relevance.py tests/test_feed.py tests/test_feed_writer.py -q`  
Expected: failures for missing editorial fields, feed module, and writer.

- [ ] **Step 3: Implement Pydantic structured analysis and feed writer**

Make `AnalysisResult` a Pydantic model and call `StructuredModel.generate` directly. Write feed Markdown with frontmatter followed by exactly these sections:

```markdown
## Summary

Cloudflare documented a signed-agent control.

## Insight

Identity is becoming infrastructure rather than a naming convention.

## Implication

Sites can distinguish accountable clients from anonymous automation.

## Why it matters

Crawler policy can become enforceable and auditable.

## Evidence

- [Primary source](https://developers.cloudflare.com/example)
- Evidence ID: `cloudflare-example--abc123`
```

The writer stores `schema_version: 1`, textual status, confidence, tracks, timestamps, source URLs, evidence IDs, `change_kind`, and optional `development_slug`. Update `event_writer.py` to use `summary` as Development and `why_it_matters` as Why it matters while retaining trend signals and raw diff.

- [ ] **Step 4: Run the editorial tests**

Run: `uv run pytest tests/test_analyzer.py tests/test_relevance.py tests/test_feed.py tests/test_feed_writer.py tests/test_event_writer.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/analyzer.py pipeline/relevance.py pipeline/feed.py pipeline/feed_writer.py pipeline/event_writer.py tests/test_analyzer.py tests/test_relevance.py tests/test_feed.py tests/test_feed_writer.py tests/test_event_writer.py
git commit -m "feat: add layered ecosystem feed records"
```

### Task 3: Cutoff, replay, promotion, and provider circuit breaker

**Files:**
- Modify: `pipeline/check.py`
- Modify: `pipeline/evidence.py`
- Modify: `pipeline/health.py`
- Modify: `tests/test_check.py`
- Modify: `tests/test_evidence.py`
- Modify: `tests/test_health.py`

**Interfaces:**
- Consumes: Gemini model, feed writer, and publication rules from Tasks 1–2.
- Produces: `ProviderCircuit` with `open_failure`, `is_open`, and `raise_if_open()`.
- Produces: `is_publishable_after_cutoff(published_at, detected_at, cutoff) -> bool`.
- Produces: `EvidenceStage.SKIPPED_CUTOFF` for historical RSS/GitHub evidence.
- Updates: `run_check(repo_root, now, fetch_dispatch=None, analyze_change=_default_analyze_change, extract_sop=None, model=None, only=None, dry_run=False, dependency_blockers=None)` and returns feed paths in run health.

- [ ] **Step 1: Write failing cutoff, promotion, replay, and circuit tests**

```python
async def test_pre_cutoff_item_is_not_analyzed_or_published(repo):
    item = CandidateItem(guid="old", title="Old", published_at=datetime(2026, 8, 29, tzinfo=UTC), url="https://example.test/old", summary="old", body="old")
    analyze = AsyncMock()
    await run_check(repo_root=repo, now=datetime(2026, 8, 30, 8, tzinfo=UTC), fetch_dispatch=per_item_fetch(item), analyze_change=analyze)
    analyze.assert_not_called()
    assert list((repo / "content" / "feed").glob("*.md")) == []


async def test_reported_item_writes_feed_without_development(reported_repo):
    await run_check(
        repo_root=reported_repo,
        now=datetime(2026, 8, 30, 8, tzinfo=UTC),
        fetch_dispatch=per_item_fetch(current_item()),
        analyze_change=AsyncMock(return_value=analysis_result(change_kind="material")),
    )
    assert len(list((reported_repo / "content" / "feed").glob("*.md"))) == 1
    assert list((reported_repo / "content" / "events").glob("*.md")) == []


async def test_fatal_provider_failure_opens_circuit_and_preserves_pending(repo):
    analyze = AsyncMock(side_effect=ProviderFailure("billing", "quota exhausted"))
    health = await run_check(
        repo_root=repo,
        now=datetime(2026, 8, 30, 8, tzinfo=UTC),
        fetch_dispatch=per_item_fetch(current_item()),
        analyze_change=analyze,
    )
    assert analyze.await_count == 1
    assert len(pending_analysis(repo / "content" / "evidence")) >= 1
    assert health["provider"]["status"] == "blocked"
```

- [ ] **Step 2: Run orchestration tests and confirm RED**

Run: `uv run pytest tests/test_check.py tests/test_evidence.py tests/test_health.py -q`  
Expected: failures for pre-cutoff analysis, absent feed output, and repeated model calls.

- [ ] **Step 3: Implement cutoff, feed publication, promotion, and circuit behavior**

Apply the cutoff before relevance or analysis for per-item sources. For every analyzed non-noise result, write a feed item. Call `write_event` only when `should_promote(status, analysis)` is true, then update the feed record with its `development_slug`. When a `ProviderFailure` has kind `authentication`, `quota`, or `billing`, open the shared circuit; later evidence remains `fetched` or `failed_analysis` without invoking Gemini again.

Extend health JSON with:

```json
{
  "provider": {
    "name": "gemini",
    "status": "ok | blocked | unavailable",
    "error": null
  },
  "feed_items_written": []
}
```

- [ ] **Step 4: Run orchestration and end-to-end tests**

Run: `uv run pytest tests/test_check.py tests/test_evidence.py tests/test_health.py tests/test_intelligence_e2e.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/check.py pipeline/evidence.py pipeline/health.py tests/test_check.py tests/test_evidence.py tests/test_health.py tests/test_intelligence_e2e.py
git commit -m "feat: publish replayable daily ecosystem feed"
```

### Task 4: Move state-of-play and weekly synthesis to Gemini

**Files:**
- Modify: `pipeline/state_of_play.py`
- Modify: `pipeline/weekly_intelligence.py`
- Modify: `tests/test_state_of_play.py`
- Modify: `tests/test_weekly_intelligence.py`

**Interfaces:**
- Consumes: `StructuredModel` from Task 1.
- Updates: `build_opt_out_matrix(model, crawler_sources, load_latest_snapshot, out_path, now)`.
- Updates: `generate_weekly_intelligence(repo_root, now, model: StructuredModel | None)`.
- Preserves: deterministic weekly issue creation when `model is None`.

- [ ] **Step 1: Rewrite state-of-play and weekly tests around a fake structured model**

```python
fake_model.generate.side_effect = [
    CrawlerFacts(supports_robots_txt=True, supports_user_agent_opt_out=True, policy_url="https://x/docs"),
    CrawlerFacts(supports_robots_txt=True, supports_user_agent_opt_out=True, policy_url="https://y/docs"),
]
await build_opt_out_matrix(
    model=fake_model,
    crawler_sources=crawler_sources,
    load_latest_snapshot=load_latest_snapshot,
    out_path=tmp_path / "opt-out-matrix.json",
    now=datetime(2026, 8, 30, tzinfo=UTC),
)
assert fake_model.generate.await_count == 2
```

Add a weekly synthesis test returning `WeeklySynthesis` through the same interface and asserting all evidence IDs are retained.

- [ ] **Step 2: Run focused tests and confirm RED**

Run: `uv run pytest tests/test_state_of_play.py tests/test_weekly_intelligence.py -q`  
Expected: signature mismatch because production still accepts Anthropic clients.

- [ ] **Step 3: Replace tool-use parsing with Pydantic structured responses**

Remove all Anthropic imports and model constants from the active state-of-play and weekly modules. Keep deterministic weekly construction, evidence validation, and the isolated legacy critical-reading archive unchanged.

- [ ] **Step 4: Run weekly and state-of-play tests**

Run: `uv run pytest tests/test_state_of_play.py tests/test_weekly_intelligence.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/state_of_play.py pipeline/weekly_intelligence.py tests/test_state_of_play.py tests/test_weekly_intelligence.py
git commit -m "refactor: use Gemini for derived intelligence"
```

### Task 5: Add Astro feed collection and reader-facing routes

**Files:**
- Modify: `site/src/content.config.ts`
- Create: `site/src/lib/feed.ts`
- Create: `site/src/components/FeedCard.astro`
- Modify: `site/src/pages/events/[slug].astro`
- Modify: `site/src/pages/developments/index.astro`
- Modify: `site/src/pages/feed.xml.ts`
- Modify: `site/src/layouts/Base.astro`
- Create: `site/src/pages/fronts/index.astro`
- Create: `site/test/feed-content.test.mjs`

**Interfaces:**
- Produces: Astro collection `feed` rooted at `../content/feed`.
- Produces: `loadFeedItems(): Promise<CollectionEntry<"feed">[]>`.
- Produces: `FeedCard` props matching the feed frontmatter plus body excerpts.
- Updates: `/events/[slug]` resolves feed first, then current development, then legacy event.

- [ ] **Step 1: Write a failing Astro content test using a feed fixture**

```javascript
test("feed loader sorts public items newest first", async () => {
  const items = sortFeedItems([
    { data: { published_at: new Date("2026-08-30T08:00:00Z") } },
    { data: { published_at: new Date("2026-08-30T10:00:00Z") } },
  ]);
  assert.equal(items[0].data.published_at.toISOString(), "2026-08-30T10:00:00.000Z");
});
```

The collection schema must require all four editorial sections through frontmatter excerpts or validated Markdown section parsing, textual status, at least one source URL, and at least one evidence ID.

- [ ] **Step 2: Run the site test/build and confirm RED**

Run: `cd site && npm test -- --runInBand` if a test script exists; otherwise `node --test test/feed-content.test.mjs`  
Expected: module or collection failures because feed support does not exist.

- [ ] **Step 3: Implement collection, loader, feed cards, detail resolution, developments filter, themes index, and RSS**

RSS item titles must prefix the visible status, for example `[Reported] Publishers test access-for-value models`, and descriptions must include Summary plus Why it matters. The detail page renders the four named sections and evidence without pipeline jargon.

- [ ] **Step 4: Run site tests and Astro build**

Run: `cd site && node --test test/feed-content.test.mjs && npm run build`  
Expected: PASS and a successful static build.

- [ ] **Step 5: Commit**

```bash
git add site/src/content.config.ts site/src/lib/feed.ts site/src/components/FeedCard.astro site/src/pages/events/'[slug]'.astro site/src/pages/developments/index.astro site/src/pages/feed.xml.ts site/src/layouts/Base.astro site/src/pages/fronts/index.astro site/test/feed-content.test.mjs
git commit -m "feat: expose the public ecosystem feed"
```

### Task 6: Build the Signal Prism layered-feed interface

**Files:**
- Modify: `site/package.json`
- Modify: `site/package-lock.json`
- Modify: `site/src/styles/global.css`
- Modify: `site/src/pages/index.astro`
- Modify: `site/src/components/HealthStrip.astro`
- Modify: `site/src/components/FrontCard.astro`
- Modify: `site/src/components/TrackTag.astro`
- Modify: `site/src/pages/about.astro`

**Interfaces:**
- Consumes: `loadFeedItems()` and `FeedCard` from Task 5.
- Preserves: the existing health, trend, intelligence, and source loaders.
- Produces: lead item selection as newest highest-importance verified item, falling back to newest public item.

- [ ] **Step 1: Add a failing static markup assertion for the new home hierarchy**

```javascript
test("home page leads with reader language", () => {
  const source = readFileSync(new URL("../src/pages/index.astro", import.meta.url), "utf8");
  assert.match(source, /Today in the ecosystem/);
  assert.match(source, /Latest signals/);
  assert.doesNotMatch(source, /The control plane/);
});
```

- [ ] **Step 2: Run the assertion and confirm RED**

Run: `cd site && node --test test/home-structure.test.mjs`  
Expected: FAIL because the current home page leads with pipeline-oriented intelligence language.

- [ ] **Step 3: Implement the approved visual tokens and home layout**

Use this compact token system:

```css
:root {
  --void: #100b20;
  --night: #17122c;
  --surface: #21183a;
  --paper: #f8f5ff;
  --muted: #b7aec9;
  --cyan: #58defd;
  --violet: #8b6dff;
  --pink: #ff4eaa;
  --amber: #ffb36b;
  --spectrum: linear-gradient(90deg, var(--cyan), var(--violet) 52%, var(--pink));
}
```

Use `Syne` for restrained display roles, `Manrope` for reading text, and `DM Mono` for evidence/status utility text. Load local Fontsource packages rather than remote CSS. The lead item receives the single luminous gradient surface; ordinary cards use quiet translucent borders. Remove the light/dark toggle because Signal Prism is the product identity, not an optional theme.

- [ ] **Step 4: Run the home assertion and production build**

Run: `cd site && node --test test/home-structure.test.mjs && npm run build`  
Expected: PASS with no Astro warnings.

- [ ] **Step 5: Commit**

```bash
git add site/package.json site/package-lock.json site/src/styles/global.css site/src/pages/index.astro site/src/components/HealthStrip.astro site/src/components/FrontCard.astro site/src/components/TrackTag.astro site/src/pages/about.astro site/test/home-structure.test.mjs
git commit -m "feat: apply Signal Prism reading experience"
```

### Task 7: Workflows, source policy, and operator documentation

**Files:**
- Modify: `.github/workflows/daily-check.yml`
- Modify: `.github/workflows/weekly-reading.yml`
- Modify: `pipeline/sources.py`
- Modify: `sources.yaml`
- Modify: `README.md`
- Modify: `tests/test_source_coverage.py`

**Interfaces:**
- Consumes: `GEMINI_API_KEY` and optional `GEMINI_ANALYSIS_MODEL`.
- Removes: `ANTHROPIC_API_KEY` from both workflows.
- Disables: `gemini_search` sources from automatic publication by setting `enabled: false` after adding `Source.enabled: bool = True`, or by removing those entries while preserving the direct-source registry.

- [ ] **Step 1: Write a failing source-policy test**

```python
def test_publication_sources_do_not_enable_gemini_search():
    enabled = [source for source in load_sources(Path("sources.yaml")) if source.enabled]
    assert all(source.type is not SourceType.GEMINI_SEARCH for source in enabled)
```

- [ ] **Step 2: Run source coverage tests and confirm RED**

Run: `uv run pytest tests/test_source_coverage.py tests/test_sources.py -q`  
Expected: failure because enabled source filtering is not implemented.

- [ ] **Step 3: Update source schema, registry, workflows, and README**

Document required secrets as `GEMINI_API_KEY` and `GITHUB_TOKEN`; document Cloudflare secrets as conditional. Explain the feed statuses, cutoff, replay behavior, local commands, and the fact that Google Search grounding is disabled for public-feed publication.

- [ ] **Step 4: Run source and configuration tests**

Run: `uv run pytest tests/test_source_coverage.py tests/test_sources.py tests/test_config.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/daily-check.yml .github/workflows/weekly-reading.yml sources.yaml README.md pipeline/sources.py tests/test_source_coverage.py tests/test_sources.py
git commit -m "chore: run publication pipeline on Gemini"
```

### Task 8: Full verification, visual QA, and main deployment

**Files:**
- Modify only files required by verification findings.

**Interfaces:**
- Verifies all prior tasks as one production system.

- [ ] **Step 1: Run Python lint and tests**

Run: `uv run ruff check pipeline tests`  
Expected: no lint errors.

Run: `uv run pytest -q`  
Expected: all tests pass.

- [ ] **Step 2: Run Astro tests and production build**

Run: `cd site && node --test test/*.test.mjs && npm run build`  
Expected: all tests pass and build exits zero without warnings.

- [ ] **Step 3: Run a dry pipeline check with no external writes**

Run: `uv run python -m pipeline.check --dry-run --only gptbot`  
Expected: dependency preflight recognizes Gemini; no Anthropic error appears; no repository content changes are written.

- [ ] **Step 4: Perform browser QA**

Start the site with `cd site && npm run dev -- --host 127.0.0.1`, then inspect `/`, one `/events/[slug]` route when a fixture exists, `/developments`, `/intelligence`, `/sources`, `/archive`, and `/feed.xml`. Capture desktop and 390-pixel mobile screenshots. Verify no horizontal overflow, readable contrast, visible textual status, keyboard focus, delayed/empty copy, and no error overlay.

- [ ] **Step 5: Review final diff and commit verification fixes**

Run: `git diff --check && git status --short && git log --oneline -10`  
Expected: no whitespace errors and only intended implementation changes.

```bash
git add -A
git commit -m "test: verify readable ecosystem publication"
```

Skip the commit if verification creates no changes.

- [ ] **Step 6: Push main and verify GitHub Actions/Vercel**

Run: `git push origin main`  
Expected: push succeeds. Trigger or observe Daily Check, confirm the workflow uses Gemini credentials, then verify `https://crawlerpolicy.com/`, `/developments`, `/intelligence`, `/sources`, `/archive`, and `/feed.xml` return successful responses.
