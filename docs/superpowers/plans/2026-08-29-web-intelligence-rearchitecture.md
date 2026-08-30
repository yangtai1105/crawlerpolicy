# Web Intelligence Rearchitecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the three-pillar crawlerpolicy experience with an evidence-first, nine-track Web Content & Agentic Web intelligence product while preserving all existing content in a Legacy Archive.

**Architecture:** Keep the current Python fetchers, Git-as-DB storage, and Astro static deployment. Introduce canonical track/source metadata, replayable evidence, stage-aware health, schema-v2 events, persistent trends, and repository-native weekly intelligence; then rebuild the Astro information architecture around five public fronts and move all schema-v1 material into legacy collections.

**Tech Stack:** Python 3.12, Pydantic, pytest, Anthropic SDK, YAML/JSON/Markdown storage, Astro 5, TypeScript, Zod, CSS, GitHub Actions, Vercel static hosting.

**Spec:** `docs/superpowers/specs/2026-08-29-web-intelligence-rearchitecture-design.md`

## Global Constraints

- Do not connect to or import output from the ChatGPT scheduled task.
- Do not re-fetch or reclassify historical events.
- Preserve existing event content and old Dispatch JSON as a Legacy Archive.
- New material events use one `primary_track` and a non-empty `tracks` array drawn from the nine canonical track keys.
- Separate `event_date`, `published_at`, and `detected_at`; never present detection time as the event date.
- Primary or measurement evidence is required for legal, standards, official-control, and trend-status claims.
- Preserve Git-as-DB and static Astro deployment; add no database or server backend.
- The pipeline must retain fetched evidence when analysis fails and must report truthful `healthy`, `degraded`, or `critical` status.
- A critical daily run exits non-zero; a degraded run remains publishable with a visible warning.
- Use TDD for every Python behavior change and run the Astro build after each site-facing task.
- Work directly on `main` as explicitly requested by the user; use small, independently reviewable commits.

---

## File Map

### Python domain and pipeline

- Create `pipeline/taxonomy.py` — canonical tracks, fronts, source tiers, source roles, and validation helpers.
- Modify `pipeline/sources.py` — remove required editorial pillar and add source metadata.
- Create `pipeline/evidence.py` — evidence IDs, records, persistence, replay queue, and stage transitions.
- Create `pipeline/health.py` — run/source health models, threshold calculation, and workflow exit policy.
- Modify `pipeline/analyzer.py` — schema-v2 materiality/track/actor/trend analysis.
- Modify `pipeline/event_writer.py` — write schema-v2 event frontmatter and evidence-oriented body sections.
- Modify `pipeline/check.py` — explicit fetch/evidence/analyze/publish stages and replay-safe state advancement.
- Modify `pipeline/state_of_play.py` — select crawler-control sources by track instead of pillar.
- Modify `pipeline/trend_context.py` — read schema-v2 dates/tracks and ignore legacy content.
- Remove `pipeline/pillar_digest.py` — superseded by track-grouped weekly intelligence.
- Create `pipeline/trends.py` — persistent trend state and evidence-tier rules.
- Create `pipeline/weekly_intelligence.py` — seven-day synthesis with previous-week comparisons.
- Modify `pipeline/config.py` — evidence, legacy, trends, and intelligence paths.
- Modify `.github/workflows/daily-check.yml` — secrets preflight and critical/degraded outcome handling.
- Modify `.github/workflows/weekly-reading.yml` — run repository-native weekly intelligence after the completed window.
- Modify `sources.yaml` — new source metadata and initial coverage lanes.

### Content and data

- Move `content/events/*.md` to `content/legacy-events/` — preserve schema-v1 history without reclassification.
- Create `content/events/.gitkeep` — schema-v2 event destination.
- Create `content/evidence/.gitkeep` — normalized evidence destination.
- Create `data/intelligence/.gitkeep` — weekly issue destination.
- Create `data/trends.json` — empty durable trend registry with schema version.

### Astro site

- Modify `site/src/content.config.ts` — separate schema-v2 and legacy collections.
- Create `site/src/lib/taxonomy.ts` — front/track labels and mappings matching Python keys.
- Create `site/src/lib/health.ts` — typed stage-aware health loader.
- Create `site/src/lib/intelligence.ts` — latest/archive intelligence loaders.
- Create `site/src/lib/trends.ts` — typed trend loader and delta ordering.
- Modify `site/src/lib/sources.ts` — new source metadata.
- Modify `site/src/layouts/Base.astro` — new brand, navigation, truthful footer health.
- Create `site/src/components/HealthStrip.astro` — health/coverage state.
- Create `site/src/components/EvidenceRail.astro` — thesis-to-evidence signature element.
- Create `site/src/components/FrontCard.astro` — five-front operating view.
- Create `site/src/components/TrackTag.astro` — canonical track label.
- Create `site/src/components/TrendTable.astro` — changed-first trend presentation.
- Create `site/src/components/DevelopmentCard.astro` — schema-v2 event summary.
- Rewrite `site/src/pages/index.astro` — intelligence-first homepage.
- Create `site/src/pages/intelligence/index.astro` and `site/src/pages/intelligence/[week].astro`.
- Create `site/src/pages/fronts/[front].astro`.
- Create `site/src/pages/developments/index.astro`.
- Create `site/src/pages/archive/index.astro`.
- Modify `site/src/pages/events/[slug].astro` — resolve current and legacy events.
- Rewrite `site/src/pages/sources/index.astro` and update `site/src/pages/sources/[slug].astro`.
- Modify `site/src/pages/about.astro` and `site/src/styles/global.css`.
- Remove `site/src/pages/pillars/[pillar].astro`, `site/src/lib/pillar_digests.ts`, `site/src/components/PillarDigestCard.astro`, and `site/src/components/PillarTag.astro` after their replacements are live.
- Modify `site/src/components/EventCard.astro` and `site/src/components/HeroBlock.astro` so no current UI imports the retired pillar components.

---

### Task 1: Canonical Taxonomy and Source Schema

**Files:**
- Create: `pipeline/taxonomy.py`
- Modify: `pipeline/sources.py`
- Modify: `pipeline/analyzer.py`
- Modify: `pipeline/check.py`
- Modify: `pipeline/state_of_play.py`
- Modify: `sources.yaml`
- Test: `tests/test_taxonomy.py`
- Test: `tests/test_sources.py`
- Test: `tests/test_state_of_play.py`
- Test: `tests/test_fetchers/test_html_page.py`
- Test: `tests/test_fetchers/test_github_repo.py`
- Test: `tests/test_fetchers/test_rss_feed.py`
- Test: `tests/test_fetchers/test_ietf_draft.py`

**Interfaces:**
- Produces: `Track`, `Front`, `SourceTier`, `SourceRole`, `FRONT_TRACKS`, `validate_tracks()`.
- Produces: `Source.default_tracks: list[Track]`, `Source.tier: SourceTier`, `Source.role: SourceRole`, `Source.required_for_coverage: bool`.
- Removes: required `Source.pillar`; runtime code and tests select source behavior from type, role, tier, or `default_tracks` instead.

- [x] **Step 1: Write failing taxonomy tests**

```python
from pipeline.taxonomy import FRONT_TRACKS, Front, Track, validate_tracks


def test_every_track_belongs_to_exactly_one_public_front():
    flattened = [track for tracks in FRONT_TRACKS.values() for track in tracks]
    assert set(flattened) == set(Track)
    assert len(flattened) == len(set(flattened))


def test_validate_tracks_requires_primary_in_tracks():
    validate_tracks(Track.SEARCH_DISCOVERY, [Track.SEARCH_DISCOVERY, Track.CRAWLER_CONTROLS])
    with pytest.raises(ValueError, match="primary_track must appear in tracks"):
        validate_tracks(Track.SEARCH_DISCOVERY, [Track.CRAWLER_CONTROLS])
```

- [x] **Step 2: Write failing source-schema tests**

```python
def test_source_uses_track_tier_and_role_without_pillar():
    source = Source(
        slug="google-search-central",
        type=SourceType.RSS_FEED,
        url="https://developers.google.com/search/blog/rss.xml",
        display_name="Google Search Central",
        default_tracks=[Track.SEARCH_DISCOVERY, Track.CRAWLER_CONTROLS],
        tier=SourceTier.PRIMARY,
        role=SourceRole.PLATFORM_DOCS,
        required_for_coverage=True,
    )
    assert source.default_tracks[0] is Track.SEARCH_DISCOVERY
    assert source.required_for_coverage is True
```

- [x] **Step 3: Run tests and confirm the old schema fails**

Run: `uv run pytest tests/test_taxonomy.py tests/test_sources.py -v`

Expected: import failures for `pipeline.taxonomy` and validation failures because `pillar` is still required.

- [x] **Step 4: Implement taxonomy enums and mappings**

```python
class Track(str, Enum):
    POLICY_REGULATION = "policy-regulation"
    LITIGATION_LEGAL = "litigation-legal"
    SEARCH_DISCOVERY = "search-discovery"
    CRAWLER_CONTROLS = "crawler-controls"
    AGENTIC_WEB = "agentic-web"
    LICENSING_MONETIZATION = "licensing-monetization"
    STANDARDS_PROTOCOLS = "standards-protocols"
    ASSET_RIGHTS = "asset-rights"
    MEASUREMENT_ECONOMICS = "measurement-economics"


class Front(str, Enum):
    ACCESS_DISCOVERY = "access-discovery"
    AGENTS_IDENTITY = "agents-identity"
    RIGHTS_MARKETS = "rights-markets"
    GOVERNANCE_LAW = "governance-law"
    MEASUREMENT_ECONOMICS = "measurement-economics"
```

Define all `FRONT_TRACKS`, `SourceTier`, and `SourceRole` values exactly as specified in the design document. `validate_tracks(primary, tracks)` rejects an empty list, duplicates, and a missing primary.

- [x] **Step 5: Update `Source` and migrate every current source entry**

Remove `pillar` from the Pydantic model. Add non-empty `default_tracks`, required `tier`, required `role`, and default `required_for_coverage=False`. Assign current crawler documentation to `crawler-controls`, Web Bot Auth to `standards-protocols` plus `agentic-web`, licensing searches to `licensing-monetization`, and regulator sources to `policy-regulation`.

- [x] **Step 6: Migrate all runtime and test consumers off `Source.pillar`**

Use `Track.CRAWLER_CONTROLS in source.default_tracks` for state-of-play selection, source role/type for analyzer prompt choice, and source tier/default tracks for model routing. Update all fetcher/analyzer/event-writer fixtures to construct the new source shape. Keep the standalone `Pillar` enum only until Task 5 removes the legacy digest module; no `Source` instance exposes it.

- [x] **Step 7: Run focused and full tests**

Run: `uv run pytest tests/test_taxonomy.py tests/test_sources.py tests/test_state_of_play.py tests/test_fetchers -v && uv run pytest`

Expected: PASS.

- [x] **Step 8: Commit**

```bash
git add pipeline/taxonomy.py pipeline/sources.py pipeline/analyzer.py pipeline/check.py pipeline/state_of_play.py sources.yaml tests/test_taxonomy.py tests/test_sources.py tests/test_state_of_play.py tests/test_analyzer.py tests/test_event_writer.py tests/test_fetchers
git commit -m "refactor: introduce web intelligence taxonomy"
```

---

### Task 2: Replayable Evidence Store

**Files:**
- Create: `pipeline/evidence.py`
- Modify: `pipeline/config.py`
- Test: `tests/test_evidence.py`

**Interfaces:**
- Produces: `EvidenceStage = fetched | analyzed | published | failed_analysis`.
- Produces: `EvidenceRecord` Pydantic model.
- Produces: `make_evidence_id(source_slug: str, external_id: str) -> str`.
- Produces: `save_evidence(root: Path, record: EvidenceRecord) -> Path`.
- Produces: `load_evidence(path: Path) -> EvidenceRecord`.
- Produces: `pending_analysis(root: Path) -> list[tuple[Path, EvidenceRecord]]`.

- [x] **Step 1: Write failing evidence lifecycle tests**

```python
def test_failed_analysis_remains_replayable(tmp_path):
    record = EvidenceRecord(
        evidence_id="cloudflare-blog--abc123",
        source="cloudflare-blog",
        source_url="https://example.test/post",
        detected_at=datetime(2026, 8, 29, tzinfo=timezone.utc),
        stage=EvidenceStage.FAILED_ANALYSIS,
        content_path="content/raw/cloudflare-blog/2026-08.jsonl",
        analysis_attempts=1,
        last_error="provider unavailable",
    )
    save_evidence(tmp_path, record)
    queued = pending_analysis(tmp_path)
    assert [item[1].evidence_id for item in queued] == [record.evidence_id]
```

- [x] **Step 2: Run the test to verify failure**

Run: `uv run pytest tests/test_evidence.py -v`

Expected: FAIL because `pipeline.evidence` does not exist.

- [x] **Step 3: Implement evidence persistence**

Use deterministic SHA-256 IDs derived from `source_slug + NUL + external_id`, JSON files at `content/evidence/<source>/<evidence_id>.json`, atomic temp-file replacement, and UTC ISO timestamps. `pending_analysis()` returns `fetched` and `failed_analysis` records ordered by `detected_at`.

- [x] **Step 4: Add `Config.evidence_dir` and run tests**

Run: `uv run pytest tests/test_evidence.py tests/test_config.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add pipeline/evidence.py pipeline/config.py tests/test_evidence.py tests/test_config.py
git commit -m "feat: preserve replayable evidence records"
```

---

### Task 3: Schema-v2 Analysis and Event Writer

**Files:**
- Modify: `pipeline/analyzer.py`
- Modify: `pipeline/event_writer.py`
- Modify: `pipeline/trend_context.py`
- Test: `tests/test_analyzer.py`
- Test: `tests/test_event_writer.py`
- Test: `tests/test_trend_context.py`

**Interfaces:**
- Produces: `Confidence = low | medium | high`.
- Extends: `AnalysisResult(primary_track, tracks, actors, trend_signals, confidence)`.
- Changes: `write_event(..., event_date, published_at, detected_at, evidence_ids) -> Path`.
- Consumes: Task 1 `Track`, `SourceTier`; Task 2 evidence IDs.

- [x] **Step 1: Extend the analyzer fixture and write a failing multi-track test**

```python
async def test_analyzer_returns_tracks_actors_and_confidence(fake_client, primary_source):
    fake_client.messages.create.return_value = _tool_response({
        "change_kind": "material",
        "importance": 0.86,
        "title": "Google adds AI Search publisher control",
        "what_changed": "Google documented a separate control.",
        "implication": "Search and training controls are diverging.",
        "primary_track": "search-discovery",
        "tracks": ["search-discovery", "crawler-controls"],
        "actors": ["Google", "publishers"],
        "trend_signals": ["training-search-separation"],
        "confidence": "high",
    })
    result = await analyze_change(...)
    assert result.primary_track is Track.SEARCH_DISCOVERY
    assert Track.CRAWLER_CONTROLS in result.tracks
    assert result.confidence == "high"
```

- [x] **Step 2: Write failing schema-v2 writer assertions**

```python
assert "schema_version: 2" in text
assert "primary_track: search-discovery" in text
assert "tracks:\n  - search-discovery\n  - crawler-controls" in text
assert "event_date: 2026-08-27T00:00:00+00:00" in text
assert "published_at: 2026-08-27T00:00:00+00:00" in text
assert "detected_at: 2026-08-27T08:00:00+00:00" in text
assert "## Development" in text
assert "## Why it matters" in text
assert "## Trend impact" in text
```

- [x] **Step 3: Run tests and confirm schema mismatch**

Run: `uv run pytest tests/test_analyzer.py tests/test_event_writer.py -v`

Expected: FAIL because the current result and frontmatter only know `pillar` and `detected_at`.

- [x] **Step 4: Expand the analyzer tool schema and prompts**

Require `primary_track`, `tracks`, `actors`, `trend_signals`, and `confidence`. Give the model source tier, source default tracks, publication date, and allowed track values. Validate tool output through `validate_tracks`; invalid output falls back to the source's first default track and records `confidence="low"` rather than inventing a category.

- [x] **Step 5: Replace event frontmatter/body with schema v2**

Write canonical YAML lists without adding a YAML dependency. Preserve raw diff only for diffable evidence. Use `Development`, `Why it matters`, `Trend impact`, and `Evidence` headings for all source types.

- [x] **Step 6: Make trend context schema-v2-only**

Load current events only from `content/events`, order by `event_date`, and match by source/track without reading `content/legacy-events`. Add a regression test proving a recently detected legacy event cannot enter current trend context.

- [x] **Step 7: Run focused and full Python tests**

Run: `uv run pytest tests/test_analyzer.py tests/test_event_writer.py tests/test_trend_context.py -v && uv run pytest`

Expected: PASS.

- [x] **Step 8: Commit**

```bash
git add pipeline/analyzer.py pipeline/event_writer.py pipeline/trend_context.py tests/test_analyzer.py tests/test_event_writer.py tests/test_trend_context.py
git commit -m "feat: emit track-aware evidence-backed events"
```

---

### Task 4: Stage-Aware Health and Daily Orchestration

**Files:**
- Create: `pipeline/health.py`
- Modify: `pipeline/check.py`
- Modify: `pipeline/state.py`
- Modify: `.github/workflows/daily-check.yml`
- Test: `tests/test_health.py`
- Test: `tests/test_check.py`

**Interfaces:**
- Produces: `HealthStatus = healthy | degraded | critical`.
- Produces: `SourceRunStatus(fetch, evidence, analysis, publish, error)`.
- Produces: `build_run_health(sources, per_source, now, last_full_success) -> RunHealth`.
- Changes: `run_check(...) -> dict` with `status`, `coverage`, `stages`, and `per_source`.
- Adds CLI exit code `2` for critical and `0` for healthy/degraded.

- [x] **Step 1: Write failing health-threshold tests**

```python
def test_required_source_failure_is_critical():
    health = build_run_health(
        sources=[required_source, optional_source],
        per_source={
            required_source.slug: SourceRunStatus(fetch="failed"),
            optional_source.slug: SourceRunStatus(fetch="ok", evidence="ok", analysis="ok", publish="ok"),
        },
        now=NOW,
        last_full_success=None,
    )
    assert health.status is HealthStatus.CRITICAL
    assert health.coverage.required_failed == 1


def test_optional_failure_with_high_coverage_is_degraded():
    assert health.status is HealthStatus.DEGRADED
```

- [x] **Step 2: Write a failing orchestration replay test**

```python
async def test_analysis_failure_saves_evidence_without_advancing_completion(repo):
    analyze = AsyncMock(side_effect=RuntimeError("provider down"))
    health = await run_check(...)
    queued = pending_analysis(repo / "content" / "evidence")
    assert len(queued) == 1
    assert queued[0][1].stage is EvidenceStage.FAILED_ANALYSIS
    assert health["status"] in {"degraded", "critical"}
```

- [x] **Step 3: Run focused tests to confirm failure**

Run: `uv run pytest tests/test_health.py tests/test_check.py -v`

Expected: FAIL because current orchestration treats the source as one opaque `ok/error` result.

- [x] **Step 4: Implement health models and calculations**

Calculate completion as sources whose required stages all equal `ok`. Persist `last_fully_successful_at` only for a healthy run. Include stage totals and required failures. Keep full per-source errors in `data/health.json`.

- [x] **Step 5: Refactor `run_check` into explicit stage helpers**

Add focused internal functions `_fetch_source`, `_record_evidence`, `_analyze_evidence`, and `_publish_analysis`. A per-item guid is appended to completed state only after evidence persistence; failed analysis remains replayable. At run start, process pending analysis records before fetching new items.

- [x] **Step 6: Add CLI preflight and exit policy**

Before processing, map missing `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, and Cloudflare credentials to affected source stages. Emit a JSON workflow summary. Exit `2` only when the computed status is critical.

- [x] **Step 7: Wire all secrets in the daily workflow**

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
  CLOUDFLARE_EMAIL: ${{ secrets.CLOUDFLARE_EMAIL }}
  CLOUDFLARE_CRAWLER_API_KEY: ${{ secrets.CLOUDFLARE_CRAWLER_API_KEY }}
```

Keep commit/push running under `if: always()` so health data is committed even when the pipeline exits critical; preserve the pipeline exit outcome in a later explicit failure step.

- [x] **Step 8: Run tests**

Run: `uv run pytest tests/test_health.py tests/test_check.py -v && uv run pytest`

Expected: PASS.

- [x] **Step 9: Commit**

```bash
git add pipeline/health.py pipeline/check.py pipeline/state.py .github/workflows/daily-check.yml tests/test_health.py tests/test_check.py
git commit -m "feat: make pipeline health stage-aware and truthful"
```

---

### Task 5: Persistent Trends and Weekly Intelligence

**Files:**
- Create: `pipeline/trends.py`
- Create: `pipeline/weekly_intelligence.py`
- Remove: `pipeline/pillar_digest.py`
- Modify: `pipeline/config.py`
- Modify: `pipeline/check.py`
- Modify: `.github/workflows/weekly-reading.yml`
- Create: `data/trends.json`
- Create: `data/intelligence/.gitkeep`
- Test: `tests/test_trends.py`
- Test: `tests/test_weekly_intelligence.py`

**Interfaces:**
- Produces: `TrendStatus`, `Trend`, `TrendDelta`, `load_trends()`, `save_trends()`.
- Produces: `WeeklyIssue` Pydantic model and `build_weekly_issue(...) -> WeeklyIssue`.
- Consumes: schema-v2 event metadata, previous weekly issue, and stage-aware health.

- [x] **Step 1: Write failing trend evidence-rule tests**

```python
def test_commentary_alone_cannot_change_trend_status():
    trend = Trend(key="agent-traffic", title="Agent traffic", status=TrendStatus.EMERGING)
    event = event_fixture(source_tier=SourceTier.COMMENTARY)
    delta = propose_delta(trend, [event], proposed=TrendStatus.ACCELERATING)
    assert delta.accepted is False
    assert delta.reason == "status changes require primary or measurement evidence"
```

- [x] **Step 2: Write failing weekly comparison tests**

```python
def test_weekly_issue_compares_against_previous_status():
    issue = build_weekly_issue(events=[primary_event], trends=[trend], previous_issue=previous, health=health)
    assert issue.trend_deltas[0].previous_status == "emerging"
    assert issue.trend_deltas[0].current_status == "accelerating"


def test_quiet_tracks_are_explicit():
    issue = build_weekly_issue(events=[primary_event], trends=[], previous_issue=None, health=health)
    quiet = next(group for group in issue.material_developments if group.track == "asset-rights")
    assert quiet.material_change is False
```

- [x] **Step 3: Run tests and verify missing modules**

Run: `uv run pytest tests/test_trends.py tests/test_weekly_intelligence.py -v`

Expected: FAIL because both modules are new.

- [x] **Step 4: Implement trend models and deterministic evidence gating**

Seed `data/trends.json` with schema version 1 and an empty `trends` array. Status changes require at least one schema-v2 material event from `primary` or `measurement`; every evidence ID must resolve.

- [x] **Step 5: Implement weekly issue collection and model synthesis**

The deterministic layer selects the completed ISO week, loads schema-v2 events by `event_date`, creates all nine track buckets, loads the prior issue, and prepares allowed evidence. The model may write prose and propose trend changes only within those IDs. Validate the response with `WeeklyIssue`; reject invented source/event IDs.

- [x] **Step 6: Retire pillar digests and replace the weekly workflow entrypoint**

Run the daily pipeline first or require a healthy/degraded health file from the completed window, then execute:

```bash
uv run python -m pipeline.weekly_intelligence
```

Commit `data/intelligence/YYYY-Www.json` and `data/trends.json`. Preserve old `data/critical-reading/*.json` unchanged for Legacy Archive.

Remove `build_pillar_digests()` from the daily check, delete `pipeline/pillar_digest.py`, and remove its generated-data write path. Keep `pipeline/critical_reading.py` read-only for historical reproducibility, but do not invoke it from either workflow.

- [x] **Step 7: Run focused and full tests**

Run: `uv run pytest tests/test_trends.py tests/test_weekly_intelligence.py -v && uv run pytest`

Expected: PASS.

- [x] **Step 8: Commit**

```bash
git add pipeline/trends.py pipeline/weekly_intelligence.py pipeline/config.py pipeline/check.py .github/workflows/weekly-reading.yml data/trends.json data/intelligence/.gitkeep tests/test_trends.py tests/test_weekly_intelligence.py
git rm pipeline/pillar_digest.py
git commit -m "feat: generate persistent weekly intelligence"
```

---

### Task 6: Legacy Archive and Astro Data Layer

**Files:**
- Move: `content/events/*.md` to `content/legacy-events/`
- Create: `content/events/.gitkeep`
- Create: `content/evidence/.gitkeep`
- Modify: `site/src/content.config.ts`
- Create: `site/src/lib/taxonomy.ts`
- Create: `site/src/lib/health.ts`
- Create: `site/src/lib/intelligence.ts`
- Create: `site/src/lib/trends.ts`
- Modify: `site/src/lib/sources.ts`
- Modify: `site/src/pages/events/[slug].astro`
- Create: `site/src/pages/archive/index.astro`
- Defer to Task 8: replace `EventCard.astro` and `HeroBlock.astro`, then remove the old pillar route, digest loader, and pillar components.

**Interfaces:**
- Produces Astro collections `events` (schema v2) and `legacyEvents` (schema v1).
- Produces `loadHealth()`, `loadLatestIntelligence()`, `loadIntelligenceArchive()`, and `loadTrends()`.
- Preserves `/events/<existing-slug>` for legacy entries.

- [x] **Step 1: Add schema-v2 fixture and failing Astro build validation**

Create a temporary test fixture under `content/events/` with schema-v2 frontmatter and change the collection schema first. Run `npm run build` from `site`; expect failure until the legacy collection and route resolver are defined.

- [x] **Step 2: Move legacy content mechanically**

```bash
mkdir -p content/legacy-events content/events content/evidence data/intelligence
git mv content/events/*.md content/legacy-events/
```

Create the three `.gitkeep` files with `apply_patch`; do not rewrite moved Markdown.

Do not edit legacy Markdown or historical Dispatch JSON.

- [x] **Step 3: Define both Astro collections**

The new `events` Zod schema requires `schema_version: z.literal(2)`, source tier, primary track, tracks, three dates, confidence and importance. `legacyEvents` retains the current pillar schema.

- [x] **Step 4: Implement typed loaders and identical taxonomy keys**

Define `TRACKS`, `FRONTS`, and `FRONT_TRACKS` with `as const`. Add a build-time invariant that every track appears in exactly one front. Health loader accepts missing data and returns an explicit `unknown` state, never `healthy`.

- [x] **Step 5: Preserve event URLs and add Legacy Archive**

`events/[slug].astro` resolves schema-v2 first and legacy second. Legacy pages receive a visible `Legacy record` label and link to `/archive`; current pages render the new evidence sections. `/archive` lists legacy events and old `/reading` issues separately.

Keep the old pillar UI only as a transitional compatibility layer in this commit. Task 8 replaces `EventCard` and `HeroBlock` with track/front metadata, then deletes `/pillars/*` generation and the old pillar digest/tag modules. Do not redirect legacy pillar URLs into a misleading new category; link the new five fronts from the archive and 404 retired pillar routes.

- [x] **Step 6: Remove the temporary fixture and run the build**

Run: `npm run build` from `site`.

Expected: all existing event URLs plus `/archive` build successfully; no legacy item appears in the schema-v2 collection.

- [x] **Step 7: Commit**

```bash
git add content data/intelligence site/src/content.config.ts site/src/lib site/src/pages/events site/src/pages/archive
git commit -m "refactor: separate current intelligence from legacy archive"
```

---

### Task 7: Visual System and Core Intelligence Components

**Files:**
- Modify: `site/src/styles/global.css`
- Modify: `site/src/layouts/Base.astro`
- Create: `site/src/components/HealthStrip.astro`
- Create: `site/src/components/EvidenceRail.astro`
- Create: `site/src/components/FrontCard.astro`
- Create: `site/src/components/TrackTag.astro`
- Create: `site/src/components/TrendTable.astro`
- Create: `site/src/components/DevelopmentCard.astro`

**Interfaces:**
- Consumes: Task 6 typed data and taxonomy.
- Produces: reusable components used by all new pages.

- [x] **Step 1: Write the compact design token plan at the top of `global.css`**

Use the frontend-design skill before editing. Define 4–6 named colors, display/body/utility font roles, layout grid, and the evidence-rail signature. The chosen system must not use the generic cream/serif/terracotta, black/acid, or broadsheet defaults called out by the skill.

- [x] **Step 2: Add component fixtures to a temporary `/component-preview` page**

Render all three health states, five fronts, changed/stable trends, track tags, development cards, and an evidence rail using fixed data. This page is a visual test fixture and is removed after final QA.

- [x] **Step 3: Implement semantic, accessible components**

`HealthStrip` exposes text labels and counts in addition to color. `TrackTag` uses the canonical label map. `TrendTable` sorts changed statuses before unchanged themes. `EvidenceRail` uses list semantics and direct source links. All interactive controls have visible keyboard focus.

- [x] **Step 4: Implement the new brand shell**

Change the product name to **Crawler Policy** with the descriptor **Rights, Access & Agentic Web Intelligence**. Navigation becomes Intelligence, Developments, Fronts, Sources, Legacy Archive, About. The footer displays last fully successful run and current coverage status.

- [x] **Step 5: Run Astro build and launch the preview**

Run: `npm run build && npm run dev -- --host 127.0.0.1` from `site`.

Expected: build passes and the preview exposes all components without console errors.

- [x] **Step 6: Inspect desktop and mobile screenshots**

Use the Browser skill at 1440×1000 and 390×844. Verify information hierarchy, overflow, focus visibility, contrast, and reduced-motion behavior. Record concrete corrections before editing.

- [x] **Step 7: Apply one visual critique pass and rebuild**

Remove any decorative element that does not encode source, status, track, or evidence. Confirm the evidence rail remains the only signature flourish.

- [x] **Step 8: Commit**

```bash
git add site/src/styles/global.css site/src/layouts/Base.astro site/src/components site/src/pages/component-preview.astro
git commit -m "feat: establish web intelligence visual system"
```

---

### Task 8: Intelligence-First Pages

**Files:**
- Rewrite: `site/src/pages/index.astro`
- Create: `site/src/pages/intelligence/index.astro`
- Create: `site/src/pages/intelligence/[week].astro`
- Create: `site/src/pages/fronts/[front].astro`
- Create: `site/src/pages/developments/index.astro`
- Rewrite: `site/src/pages/sources/index.astro`
- Modify: `site/src/pages/sources/[slug].astro`
- Rewrite: `site/src/pages/about.astro`
- Remove after QA: `site/src/pages/component-preview.astro`

**Interfaces:**
- Consumes: Tasks 6–7 loaders/components.
- Produces: the public information architecture from the approved spec.

- [x] **Step 1: Add data fixtures for an empty first launch**

Use empty `data/intelligence/`, empty schema-v2 events, empty trends, and the real health file. Every page must render a useful empty/degraded state without substituting legacy events.

- [x] **Step 2: Rewrite the homepage in the specified order**

Render weekly thesis, HealthStrip, executive shifts, five FrontCards, TrendTable, latest verified developments, and watchlist. With no current weekly issue, lead with `New intelligence cycle starting` and explain that verified post-refactor evidence will appear here; link Legacy Archive separately.

- [x] **Step 3: Implement current and archived intelligence routes**

`/intelligence` renders the latest verified issue or the empty launch state. `/intelligence/[week]` builds one route per JSON issue. Each claim uses EvidenceRail and shows coverage for that week.

- [x] **Step 4: Implement five static front routes**

Generate exactly the five `Front` keys. Each page shows its mapped tracks, current trend theses, latest material events by `event_date`, required source coverage, and explicit no-change language when empty.

- [x] **Step 5: Implement developments filtering**

Render server-built data attributes for track, front, actor, tier, and date. Client JavaScript updates visible cards and URL query parameters. With JavaScript disabled, all current developments remain readable.

- [x] **Step 6: Rewrite Sources and About**

Sources group by role and tier, show default tracks and stage health, and separate required coverage. About explains evidence → event → trend → weekly intelligence, model disclosure, health semantics, and Legacy Archive boundaries.

- [x] **Step 7: Build and inspect every route**

Run: `npm run build` from `site`.

Expected: new homepage, five fronts, developments, sources, intelligence, archive, existing legacy events, old reading pages and about all build.

- [x] **Step 8: Browser QA**

Open homepage, one front, Sources, Legacy Archive, and one legacy event at desktop/mobile widths. Verify route links, empty states, filters, health truthfulness and absence of old events from current counts.

- [x] **Step 9: Remove the component preview and commit**

```bash
git rm site/src/pages/component-preview.astro
git add site/src/pages site/src/components site/src/styles
git commit -m "feat: launch intelligence-first site architecture"
```

---

### Task 9: Initial Coverage Expansion by Intelligence Lane

**Files:**
- Modify: `sources.yaml`
- Modify only if needed: `pipeline/fetchers/html_page.py`
- Test: `tests/test_source_coverage.py`
- Test only if needed: `tests/test_fetchers/test_html_page.py`

**Interfaces:**
- Adds a deliberately small first-party/measurement source batch after the schema migration.
- Verifies all nine tracks have configured coverage and every front has at least one required primary or measurement source.
- Does not backfill, re-fetch, or classify historical material.

- [x] **Step 1: Write failing coverage-invariant tests**

```python
def test_all_tracks_have_configured_coverage():
    sources = load_sources(Path("sources.yaml"))
    covered = {track for source in sources for track in source.default_tracks}
    assert covered == set(Track)


def test_every_front_has_required_authoritative_coverage():
    sources = load_sources(Path("sources.yaml"))
    for front, tracks in FRONT_TRACKS.items():
        assert any(
            source.required_for_coverage
            and source.tier in {SourceTier.PRIMARY, SourceTier.MEASUREMENT}
            and set(source.default_tracks).intersection(tracks)
            for source in sources
        ), front
```

- [x] **Step 2: Add the verified canonical source batch**

Add these exact endpoints with explicit tier, role, default tracks, and coverage requirement:

| Slug | Endpoint | Type | Tier / role | Default tracks |
|---|---|---|---|---|
| `google-search-central-blog` | `https://developers.google.com/search/blog` | `html_page` | primary / platform-docs | search-discovery, crawler-controls |
| `ietf-webbotauth-wg` | `https://datatracker.ietf.org/group/webbotauth/` | `html_page` | primary / standards | standards-protocols, agentic-web |
| `c2pa-specifications` | `https://spec.c2pa.org/` | `html_page` | primary / standards | asset-rights, standards-protocols |
| `w3c-tdmrep` | `https://w3c.github.io/tdm-reservation-protocol/spec/` | `html_page` | primary / standards | asset-rights, licensing-monetization, standards-protocols |
| `rsl-standard` | `https://rslstandard.org/rsl` | `html_page` | primary / standards | licensing-monetization, asset-rights, crawler-controls |
| `iab-comp` | `https://iabtechlab.com/standards/comp-content-monetization-protocols-initiative/` | `html_page` | primary / standards | licensing-monetization, standards-protocols |
| `us-copyright-office-ai` | `https://www.copyright.gov/ai/` | `html_page` | primary / regulator | policy-regulation, litigation-legal, asset-rights |
| `cloudflare-radar-ai-insights` | `https://radar.cloudflare.com/ai-insights` | `html_page` or the smallest existing supported browser-backed type proven by a fetch test | measurement / measurement | measurement-economics, crawler-controls, agentic-web |

Keep discovery searches as commentary-tier leads. They may surface candidates, but they do not satisfy authoritative coverage invariants and cannot independently change trend status.

- [x] **Step 3: Mark a minimal required coverage set**

Select required sources by lane, not by vendor count: platform crawler controls, search/discovery, agent identity/standards, rights/licensing, governance/legal, and measurement/economics. Do not mark every source required; one vendor outage must not make unrelated fronts critical.

- [x] **Step 4: Prove every endpoint is fetchable through its configured adapter**

Add parametrized mocked adapter tests for the source types, then run one non-mutating live smoke fetch per new endpoint with a short timeout. If a dynamic endpoint cannot be normalized by `html_page`, use the existing browser-backed fetcher and document why in `sources.yaml`; do not add scraping bypasses.

- [x] **Step 5: Run coverage and full test suites**

Run: `uv run pytest tests/test_source_coverage.py tests/test_fetchers -v && uv run pytest`

Expected: PASS, with exactly nine canonical tracks covered and all five fronts backed by required authoritative evidence.

- [x] **Step 6: Commit**

```bash
git add sources.yaml pipeline/fetchers/html_page.py tests/test_source_coverage.py tests/test_fetchers/test_html_page.py
git commit -m "feat: expand authoritative intelligence coverage"
```

---

### Task 10: End-to-End Fixtures, Documentation, and Final Verification

**Files:**
- Create: `tests/fixtures/intelligence_repo/` fixture tree.
- Create: `tests/test_intelligence_e2e.py`
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `site/README.md`

**Interfaces:**
- Verifies all preceding tasks as one product.

- [ ] **Step 1: Create a three-source fixture repository**

Include:

- Required primary source with a successful schema-v2 event.
- Optional specialist source whose fetch fails.
- Measurement source whose fetch succeeds but analysis fails and remains replayable.
- Previous weekly issue with an `emerging` trend.

- [ ] **Step 2: Write the failing end-to-end test**

```python
async def test_pipeline_preserves_partial_success_and_weekly_delta(fixture_repo):
    health = await run_check(...)
    assert health["status"] == "degraded"
    assert len(list((fixture_repo / "content/events").glob("*.md"))) == 1
    assert len(pending_analysis(fixture_repo / "content/evidence")) == 1

    issue = await generate_weekly_intelligence(repo_root=fixture_repo, now=WEEK_END, client=fake_client)
    assert issue.trend_deltas[0].previous_status == "emerging"
    assert issue.trend_deltas[0].current_status == "accelerating"
```

- [ ] **Step 3: Run the end-to-end test and fix only integration defects**

Run: `uv run pytest tests/test_intelligence_e2e.py -v`

Expected: PASS after resolving interface mismatches; do not add new product behavior here.

- [ ] **Step 4: Update project documentation**

Document nine tracks, five fronts, evidence replay, health statuses, weekly commands, new file layout, Legacy Archive, secret requirements, and manual verification commands. Remove statements claiming the site still has three pillars or that the footer timestamp proves a successful run.

- [ ] **Step 5: Run all verification commands from a clean process**

```bash
uv run pytest
uv run ruff check pipeline tests
cd site && npm run build
```

Expected: 0 test failures, 0 Ruff errors, successful Astro build.

- [ ] **Step 6: Run final browser verification**

Start the static preview and inspect homepage, intelligence empty/current states, all five fronts, developments filters, sources health, archive, one new event fixture and one legacy event. Check browser console errors and broken internal links.

- [ ] **Step 7: Review git state and commit**

```bash
git status --short
git diff --check
git add README.md CLAUDE.md site/README.md tests/fixtures tests/test_intelligence_e2e.py
git commit -m "test: verify web intelligence rearchitecture"
```

- [ ] **Step 8: Run final verification after the commit**

Run: `uv run pytest && uv run ruff check pipeline tests && (cd site && npm run build)`

Expected: all commands exit 0.
