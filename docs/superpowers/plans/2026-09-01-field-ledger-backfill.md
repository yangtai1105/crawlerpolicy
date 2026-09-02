# Field Ledger and Direct-Evidence Backfill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Signal Prism with the readable Field Ledger interface and publish a resumable, direct-source-only feed backfill covering June 1 through September 1, 2026.

**Architecture:** A standalone backfill selector reads immutable evidence, joins source policy, excludes search-grounded sources, and writes progress to an atomic manifest. A bounded runner reuses Gemini relevance, structured analysis, deterministic publication status, feed writing, and verified-development promotion without changing Daily Check's launch cutoff. Astro validates and presents explicit backfill metadata through the Field Ledger visual system.

**Tech Stack:** Python 3.12, Pydantic 2, PyYAML, google-genai, pytest, GitHub Actions, Astro 6, TypeScript, Fontsource, CSS

**Spec:** `docs/superpowers/specs/2026-09-01-field-ledger-backfill-design.md`

## Global Constraints

- The approved production window is inclusive: `2026-06-01T00:00:00Z` through `2026-09-01T23:59:59Z`.
- Evidence comes only from existing `content/evidence/` records; the backfill performs no historical fetches.
- Every `gemini_search` source is excluded regardless of its evidence stage or enabled state.
- Legacy schema-v1 prose is not an analysis input.
- Backfilled records preserve the evidence `published_at`, falling back to `detected_at`, as both public `published_at` and `event_date`.
- Gemini may classify relevance and generate analysis but cannot assign publication status.
- The normal Daily Check cutoff remains `2026-08-30T00:00:00Z`.
- Re-running a batch never overwrites or duplicates a successfully published feed record.
- Production processes at most 15 previously unfinished eligible records per workflow invocation.
- Field Ledger uses Field Paper `#E8EEEA`, Ledger Ink `#192820`, Forest Block `#203A30`, Clay Marker `#D16B50`, Evidence Mint `#7BB497`, and Quiet Rule `#AEBDB4`.
- Backfilled status and original date are always expressed in text, never color alone.
- Public editorial copy remains English.

---

### Task 1: Backfill metadata in feed records

**Files:**
- Modify: `pipeline/feed_writer.py`
- Modify: `tests/test_feed_writer.py`
- Modify: `site/src/content.config.ts`
- Modify: `site/test/fixtures/reported-feed-item.md`

**Interfaces:**
- Extends: `write_feed_item(..., backfilled: bool = False, processed_at: datetime | None = None, backfill_batch: str | None = None) -> Path`.
- Produces frontmatter: `backfilled`, `processed_at`, and `backfill_batch`.
- Preserves: existing live-call behavior when `backfilled=False`.

- [ ] **Step 1: Write failing feed-writer tests for backfill metadata and validation**

Add to `tests/test_feed_writer.py`:

```python
import pytest


def test_backfilled_feed_item_records_processing_metadata(tmp_path, source, analysis):
    published = datetime(2026, 7, 28, 16, 47, tzinfo=UTC)
    processed = datetime(2026, 9, 1, 18, tzinfo=UTC)
    path = write_feed_item(
        feed_dir=tmp_path,
        source=source,
        analysis=analysis,
        status=PublicationStatus.VERIFIED,
        event_date=published,
        published_at=published,
        detected_at=processed,
        evidence_ids=["mcp-spec--abc123"],
        source_urls=["https://example.test/release"],
        unified_diff="",
        backfilled=True,
        processed_at=processed,
        backfill_batch="direct-evidence_2026-06-01_2026-09-01",
    )
    data = yaml.safe_load(path.read_text().split("---", 2)[1])
    assert data["backfilled"] is True
    assert data["processed_at"] == processed
    assert data["backfill_batch"] == "direct-evidence_2026-06-01_2026-09-01"
    assert data["published_at"] == published


def test_backfilled_feed_item_requires_batch_metadata(tmp_path, source, analysis):
    with pytest.raises(ValueError, match="processed_at and backfill_batch"):
        write_feed_item(
            feed_dir=tmp_path,
            source=source,
            analysis=analysis,
            status=PublicationStatus.VERIFIED,
            event_date=datetime(2026, 7, 1, tzinfo=UTC),
            published_at=datetime(2026, 7, 1, tzinfo=UTC),
            detected_at=datetime(2026, 9, 1, tzinfo=UTC),
            evidence_ids=["source--abc"],
            source_urls=["https://example.test/item"],
            unified_diff="",
            backfilled=True,
        )
```

Factor the existing source and analysis construction into local pytest fixtures so both existing and new tests use the same valid objects.

- [ ] **Step 2: Run the writer tests and confirm RED**

Run: `uv run pytest tests/test_feed_writer.py -q`  
Expected: failures because `write_feed_item` does not accept backfill arguments.

- [ ] **Step 3: Implement optional metadata and Astro validation**

In `pipeline/feed_writer.py`, extend both `write_feed_item` and `_compose` with the three arguments. Before creating the file:

```python
if backfilled and (processed_at is None or not backfill_batch):
    raise ValueError("backfilled feed items require processed_at and backfill_batch")
```

Write frontmatter exactly as:

```python
frontmatter += f"backfilled: {str(backfilled).lower()}\n"
if backfilled:
    frontmatter += f"processed_at: {processed_at.isoformat()}\n"
    frontmatter += f"backfill_batch: {backfill_batch}\n"
```

Extend the Astro feed schema with:

```ts
backfilled: z.boolean().default(false),
processed_at: z.coerce.date().optional(),
backfill_batch: z.string().optional(),
```

Add a schema refinement that requires both optional values when `backfilled` is true. Update the test fixture with `backfilled: true`, `processed_at: 2026-09-01T18:00:00Z`, and the approved batch ID.

- [ ] **Step 4: Run focused Python and Astro integration tests**

Run: `uv run pytest tests/test_feed_writer.py -q && cd site && node --test test/feed-publication.test.mjs`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/feed_writer.py tests/test_feed_writer.py site/src/content.config.ts site/test/fixtures/reported-feed-item.md
git commit -m "feat: record feed backfill provenance"
```

---

### Task 2: Shared provider circuit and backfill selection

**Files:**
- Modify: `pipeline/model_provider.py`
- Modify: `pipeline/check.py`
- Modify: `tests/test_model_provider.py`
- Create: `pipeline/backfill.py`
- Create: `tests/test_backfill.py`

**Interfaces:**
- Moves: `ProviderCircuit` from `pipeline.check` to `pipeline.model_provider` without changing `is_open` or `open(failure)` behavior.
- Produces: `BackfillCandidate(path: Path, record: EvidenceRecord, source: Source, item_date: datetime)`.
- Produces: `load_published_evidence_ids(feed_dir: Path) -> set[str]`.
- Produces: `BackfillSelection(candidates, excluded_search_ids, unknown_source_ids, outside_window_ids, duplicate_ids, invalid_paths)` with a derived `counts` property.
- Produces: `select_candidates(evidence_dir, feed_dir, sources, since, until) -> BackfillSelection` ordered newest first, then evidence ID.

- [ ] **Step 1: Write failing circuit-location and selection tests**

Add to `tests/test_model_provider.py`:

```python
def test_provider_circuit_opens_only_for_blocking_failures():
    circuit = ProviderCircuit()
    circuit.open(ProviderFailure("transient", "temporary"))
    assert circuit.is_open is False
    circuit.open(ProviderFailure("quota", "exhausted"))
    assert circuit.is_open is True
```

Create `tests/test_backfill.py` with fixtures for a primary RSS source, a disabled Gemini Search source, in-window direct evidence, out-of-window evidence, and one feed Markdown file containing an existing evidence ID. Assert:

```python
def test_selection_uses_only_unpublished_direct_evidence(repo):
    selection = select_candidates(
        evidence_dir=repo / "content/evidence",
        feed_dir=repo / "content/feed",
        sources=load_sources(repo / "sources.yaml"),
        since=datetime(2026, 6, 1, tzinfo=UTC),
        until=datetime(2026, 9, 1, 23, 59, 59, tzinfo=UTC),
    )
    assert [candidate.record.evidence_id for candidate in selection.candidates] == [
        "direct--newest",
        "direct--older",
    ]
    assert selection.excluded_search_ids == ["search--excluded"]
    assert selection.outside_window_ids == ["direct--old"]
    assert selection.duplicate_ids == ["direct--published"]
    assert selection.counts.eligible == 2
```

- [ ] **Step 2: Run focused tests and confirm RED**

Run: `uv run pytest tests/test_model_provider.py tests/test_backfill.py -q`  
Expected: import failures for `ProviderCircuit`, `BackfillCandidate`, and `select_candidates`.

- [ ] **Step 3: Move the circuit and implement pure selection**

Place this dataclass in `pipeline/model_provider.py` and import it from `pipeline.check`:

```python
@dataclass
class ProviderCircuit:
    failure: ProviderFailure | None = None

    @property
    def is_open(self) -> bool:
        return self.failure is not None

    def open(self, failure: ProviderFailure) -> None:
        if failure.blocks_run and self.failure is None:
            self.failure = failure
```

In `pipeline/backfill.py`, parse existing feed frontmatter with `yaml.safe_load`, union all `evidence_ids`, load every evidence JSON with `load_evidence`, and classify exclusion counts. Use `record.published_at or record.detected_at` as `item_date`. Never filter by evidence stage.

```python
@dataclass(frozen=True)
class BackfillCandidate:
    path: Path
    record: EvidenceRecord
    source: Source
    item_date: datetime


class BackfillSelectionCounts(BaseModel):
    total_evidence: int = 0
    eligible: int = 0
    excluded_search: int = 0
    unknown_source: int = 0
    outside_window: int = 0
    duplicate: int = 0
    invalid: int = 0


class BackfillSelection(BaseModel):
    candidates: list[BackfillCandidate]
    excluded_search_ids: list[str] = Field(default_factory=list)
    unknown_source_ids: list[str] = Field(default_factory=list)
    outside_window_ids: list[str] = Field(default_factory=list)
    duplicate_ids: list[str] = Field(default_factory=list)
    invalid_paths: list[str] = Field(default_factory=list)

    @property
    def counts(self) -> BackfillSelectionCounts:
        return BackfillSelectionCounts(
            total_evidence=(len(self.candidates) + len(self.excluded_search_ids)
                + len(self.unknown_source_ids) + len(self.outside_window_ids)
                + len(self.duplicate_ids) + len(self.invalid_paths)),
            eligible=len(self.candidates),
            excluded_search=len(self.excluded_search_ids),
            unknown_source=len(self.unknown_source_ids),
            outside_window=len(self.outside_window_ids),
            duplicate=len(self.duplicate_ids),
            invalid=len(self.invalid_paths),
        )
```

- [ ] **Step 4: Run circuit, selection, and Daily Check regression tests**

Run: `uv run pytest tests/test_model_provider.py tests/test_backfill.py tests/test_check.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/model_provider.py pipeline/check.py pipeline/backfill.py tests/test_model_provider.py tests/test_backfill.py
git commit -m "feat: select direct evidence for backfill"
```

---

### Task 3: Atomic backfill manifest

**Files:**
- Modify: `pipeline/backfill.py`
- Modify: `tests/test_backfill.py`

**Interfaces:**
- Produces: `BackfillOutcome(StrEnum)` values `published`, `irrelevant`, `duplicate`, `failed`, `excluded_source`, and `outside_window`.
- Produces: `BackfillEntry(evidence_id, outcome, updated_at, feed_path=None, development_path=None, reason=None)`.
- Produces: `BackfillManifest(batch_id, since, until, entries={}, summary={})`.
- Produces: `batch_id(since, until) -> str`, `load_manifest(path, since, until)`, and atomic `save_manifest(path, manifest)`.

- [ ] **Step 1: Write failing manifest identity, atomic-save, and resume tests**

Add to `tests/test_backfill.py`:

```python
def test_manifest_batch_id_and_round_trip(tmp_path):
    since = datetime(2026, 6, 1, tzinfo=UTC)
    until = datetime(2026, 9, 1, 23, 59, 59, tzinfo=UTC)
    manifest = BackfillManifest(
        batch_id=batch_id(since, until),
        since=since,
        until=until,
        entries={
            "source--abc": BackfillEntry(
                evidence_id="source--abc",
                outcome=BackfillOutcome.PUBLISHED,
                updated_at=until,
                feed_path="content/feed/item.md",
            )
        },
        summary={"published": 1, "remaining": 0},
    )
    path = tmp_path / "manifest.json"
    save_manifest(path, manifest)
    assert load_manifest(path, since=since, until=until) == manifest
    assert not list(tmp_path.glob("*.tmp"))


def test_manifest_rejects_a_different_window(tmp_path):
    path = tmp_path / "manifest.json"
    save_manifest(path, BackfillManifest(
        batch_id="direct-evidence_2026-06-01_2026-09-01",
        since=datetime(2026, 6, 1, tzinfo=UTC),
        until=datetime(2026, 9, 1, 23, 59, 59, tzinfo=UTC),
    ))
    with pytest.raises(ValueError, match="window does not match"):
        load_manifest(
            path,
            since=datetime(2026, 7, 1, tzinfo=UTC),
            until=datetime(2026, 9, 1, 23, 59, 59, tzinfo=UTC),
        )
```

- [ ] **Step 2: Run the manifest tests and confirm RED**

Run: `uv run pytest tests/test_backfill.py -q`  
Expected: imports fail for manifest types and functions.

- [ ] **Step 3: Implement Pydantic manifest types and atomic persistence**

Use the same `NamedTemporaryFile` plus `os.replace` pattern as `pipeline.evidence.save_evidence`. Define:

```python
def batch_id(since: datetime, until: datetime) -> str:
    return f"direct-evidence_{since.date().isoformat()}_{until.date().isoformat()}"


def manifest_path(data_dir: Path, since: datetime, until: datetime) -> Path:
    return data_dir / "backfills" / f"{batch_id(since, until)}.json"
```

`load_manifest` creates an empty manifest if the path does not exist and rejects an existing manifest whose ID or exact timestamps do not match the requested window.

Manifest entries use `published`, `irrelevant`, `duplicate`, `excluded_source`, and `outside_window` as terminal outcomes. `failed` is retryable: a later invocation may replace it with a terminal outcome. `summary` stores the last `BackfillSummary` as JSON-compatible scalar values so the workflow operator can inspect `remaining` without rerunning the CLI.

- [ ] **Step 4: Run all backfill unit tests**

Run: `uv run pytest tests/test_backfill.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/backfill.py tests/test_backfill.py
git commit -m "feat: persist resumable backfill progress"
```

---

### Task 4: Bounded Gemini backfill runner and CLI

**Files:**
- Create: `pipeline/backfill_feed.py`
- Create: `tests/test_backfill_feed.py`
- Modify: `README.md`

**Interfaces:**
- Produces: `BackfillSummary(batch_id, eligible, attempted, remaining, published, irrelevant, duplicate, excluded, failed, provider_status)`.
- Produces: `async run_backfill(*, repo_root: Path, since: datetime, until: datetime, limit: int, model: StructuredModel | None, now: datetime, dry_run: bool = False, analyze=analyze_change, relevance=model_relevance) -> BackfillSummary`.
- Produces CLI flags: `--since`, `--until`, `--limit`, `--direct-only`, and `--dry-run`.

- [ ] **Step 1: Write failing runner tests with injected structured-model behavior**

Create `tests/test_backfill_feed.py`. Build a temporary repository containing direct primary, specialist, and Gemini Search sources plus evidence inside and outside the window. Inject async relevance and analysis functions. Cover these behaviors:

```python
async def test_backfill_publishes_material_direct_evidence_with_original_date(repo):
    summary = await run_backfill(
        repo_root=repo,
        since=datetime(2026, 6, 1, tzinfo=UTC),
        until=datetime(2026, 9, 1, 23, 59, 59, tzinfo=UTC),
        limit=15,
        model=AsyncMock(),
        now=datetime(2026, 9, 2, 1, tzinfo=UTC),
        relevance=AsyncMock(return_value=RelevanceVerdict(is_relevant=True, reason="in scope")),
        analyze=AsyncMock(return_value=material_analysis()),
    )
    assert summary.published == 1
    feed = next((repo / "content/feed").glob("*.md")).read_text()
    assert "published_at: 2026-07-28T16:47:49+00:00" in feed
    assert "backfilled: true" in feed


async def test_backfill_excludes_search_and_is_idempotent(repo):
    first = await run_backfill(**runner_args(repo))
    second = await run_backfill(**runner_args(repo))
    assert first.published == 1
    assert second.published == 0
    assert len(list((repo / "content/feed").glob("*.md"))) == 1


async def test_reported_backfill_does_not_create_development(specialist_repo):
    summary = await run_backfill(**runner_args(specialist_repo))
    assert summary.published == 1
    assert list((specialist_repo / "content/events").glob("*.md")) == []


async def test_blocking_provider_failure_stops_remaining_calls(repo):
    analyze = AsyncMock(side_effect=ProviderFailure("quota", "resource exhausted"))
    summary = await run_backfill(**runner_args(repo, analyze=analyze))
    assert analyze.await_count == 1
    assert summary.provider_status == "blocked"
    assert summary.remaining > 0
```

Also assert `limit=1` attempts one unfinished candidate, an irrelevant verdict writes `irrelevant` to the manifest without an analysis call, and `dry_run=True` writes no manifest/feed/event files and requires no model.

- [ ] **Step 2: Run runner tests and confirm RED**

Run: `uv run pytest tests/test_backfill_feed.py -q`  
Expected: import failure for `pipeline.backfill_feed`.

- [ ] **Step 3: Implement the runner and JSON CLI output**

Before limiting candidates, copy `excluded_search_ids`, `unknown_source_ids`, `outside_window_ids`, and `duplicate_ids` from selection into terminal manifest entries. Skip candidates with terminal manifest entries; include candidates with no entry or a `failed` entry. Apply `limit` to that unfinished list. Runner sequence per attempted candidate:

```python
if record.title is not None:
    if not keyword_match(f"{record.title}\n{record.content}", source.keyword_filter or []):
        record_outcome(BackfillOutcome.IRRELEVANT, "keyword filter")
        continue
    verdict = await relevance(model, record.title, record.content)
    if not verdict.is_relevant:
        record_outcome(BackfillOutcome.IRRELEVANT, verdict.reason)
        continue

analysis = await analyze(
    model=model,
    source=source,
    prev_content=record.previous_content,
    curr_content=record.content,
    unified_diff=record.unified_diff,
    item_url=record.source_url,
    published_at=record.published_at,
)
if analysis.change_kind != "material":
    record_outcome(BackfillOutcome.IRRELEVANT, analysis.change_kind)
    continue
```

For material analysis, compute `status = publication_status(source)`. If `should_promote(status, analysis)`, call `write_event` first and pass `event_slug(analysis.title)` into `write_feed_item`. Both writers receive `item_date` for event and publication dates and `record.detected_at` for detection time; the feed writer receives `backfilled=True`, `processed_at=now`, and the batch ID. Save the manifest after every attempted candidate and write the returned summary into `manifest.summary` before the final save.

The CLI parses ISO strings with `datetime.fromisoformat(value.replace("Z", "+00:00"))`, rejects naive timestamps and non-positive limits, constructs `GeminiStructuredModel` only outside dry-run, prints `summary.model_dump_json(indent=2)`, and exits nonzero only for invalid arguments or a blocked provider.

- [ ] **Step 4: Run runner, writer, and Daily Check regression tests**

Run: `uv run pytest tests/test_backfill_feed.py tests/test_backfill.py tests/test_feed_writer.py tests/test_check.py -q`  
Expected: PASS.

- [ ] **Step 5: Document the exact operator commands and commit**

Add to `README.md`:

```bash
# Count eligible records without model calls or writes.
uv run python -m pipeline.backfill_feed \
  --since 2026-06-01T00:00:00Z \
  --until 2026-09-01T23:59:59Z \
  --limit 15 --direct-only --dry-run

# Process one resumable local batch.
GEMINI_API_KEY=... uv run python -m pipeline.backfill_feed \
  --since 2026-06-01T00:00:00Z \
  --until 2026-09-01T23:59:59Z \
  --limit 15 --direct-only
```

```bash
git add pipeline/backfill_feed.py tests/test_backfill_feed.py README.md
git commit -m "feat: backfill feed from direct evidence"
```

---

### Task 5: Bounded backfill GitHub workflow

**Files:**
- Create: `.github/workflows/backfill-feed.yml`
- Create: `tests/test_backfill_workflow.py`

**Interfaces:**
- Consumes: `GEMINI_API_KEY`, `GEMINI_ANALYSIS_MODEL`, and manual inputs `since`, `until`, `limit`.
- Produces: one manifest/feed/development commit per successful bounded run.
- Preserves: Daily Check and Weekly Intelligence schedules unchanged.

- [ ] **Step 1: Write a failing workflow contract test**

Create `tests/test_backfill_workflow.py`:

```python
from pathlib import Path
import yaml


def test_backfill_workflow_is_manual_bounded_and_gemini_only():
    raw = Path(".github/workflows/backfill-feed.yml").read_text()
    data = yaml.safe_load(raw)
    assert "workflow_dispatch" in data["on"]
    inputs = data["on"]["workflow_dispatch"]["inputs"]
    assert inputs["limit"]["default"] == "15"
    assert "GEMINI_API_KEY" in raw
    assert "ANTHROPIC_API_KEY" not in raw
    assert "pipeline.backfill_feed" in raw
    assert "npm run build" in raw
```

Use a custom PyYAML loader or inspect the raw top-level mapping so YAML 1.1 does not coerce the key `on` to `True`.

- [ ] **Step 2: Run the contract test and confirm RED**

Run: `uv run pytest tests/test_backfill_workflow.py -q`  
Expected: `FileNotFoundError` for the new workflow.

- [ ] **Step 3: Create the manual workflow**

The workflow must contain:

```yaml
name: Backfill Feed

on:
  workflow_dispatch:
    inputs:
      since:
        default: "2026-06-01T00:00:00Z"
        required: true
      until:
        default: "2026-09-01T23:59:59Z"
        required: true
      limit:
        default: "15"
        required: true

permissions:
  contents: write

concurrency:
  group: backfill-feed
  cancel-in-progress: false
```

Checkout with full history, install Python 3.12 and uv, run `uv sync --frozen`, execute the backfill CLI with the three inputs and `--direct-only`, set up Node 24, run `npm ci && npm run check && npm run build` from `site`, then commit only `content/feed`, `content/events`, and `data/backfills` using `git add` on those exact paths. Push `HEAD:${{ github.ref_name }}` without force.

- [ ] **Step 4: Run workflow and regression tests**

Run: `uv run pytest tests/test_backfill_workflow.py tests/test_config.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/backfill-feed.yml tests/test_backfill_workflow.py
git commit -m "ci: add resumable feed backfill workflow"
```

---

### Task 6: Field Ledger reading experience and backfill labels

**Files:**
- Modify: `site/package.json`
- Modify: `site/package-lock.json`
- Modify: `site/src/styles/global.css`
- Modify: `site/src/layouts/Base.astro`
- Modify: `site/src/pages/index.astro`
- Modify: `site/src/components/FeedCard.astro`
- Modify: `site/src/components/FrontCard.astro`
- Modify: `site/src/components/HealthStrip.astro`
- Modify: `site/src/components/TrackTag.astro`
- Modify: `site/src/pages/events/[slug].astro`
- Modify: `site/src/pages/feed.xml.ts`
- Modify: `site/test/feed-publication.test.mjs`
- Create: `site/test/fixtures/verified-backfilled-item.md`

**Interfaces:**
- Consumes: feed `backfilled`, `processed_at`, and `backfill_batch` fields from Task 1.
- Produces: `FeedCard` prop `backfilled: boolean`.
- Produces: newest-window lead selection; an older high-importance record cannot outrank a materially newer record.
- Produces: `[Backfilled]` RSS title prefix for historical imports.

- [ ] **Step 1: Extend the build integration test and add a second fixture**

The verified fixture uses an original publication date of `2026-07-28`, `backfilled: true`, high importance, and all five Markdown sections. Keep the reported fixture dated `2026-08-30` with lower importance. Extend setup/cleanup to copy both fixtures.

Assert built HTML behavior rather than source strings:

```js
assert.match(home, /Field Ledger/);
assert.match(home, /Original publication/);
assert.match(home, /Backfilled/);
assert.match(home, /Agent access develops a market layer/);
assert.ok(
  home.indexOf("Agent access develops a market layer") <
  home.indexOf("Older verified protocol release"),
  "newer reported item must appear before an older high-importance item",
);
assert.match(detail, /Backfilled/);
assert.match(detail, /July 28, 2026/);
assert.match(rss, /\[Backfilled\] Older verified protocol release/);
```

- [ ] **Step 2: Run the integration test and confirm RED**

Run: `cd site && node --test test/feed-publication.test.mjs`  
Expected: failures for Field Ledger identity and backfill labels.

- [ ] **Step 3: Install IBM Plex fonts and implement the Field Ledger system**

Replace Syne and Manrope with local Fontsource IBM Plex packages and keep a mono face for utility text. Define these root tokens exactly:

```css
:root {
  --field-paper: #e8eeea;
  --ledger-ink: #192820;
  --forest-block: #203a30;
  --clay-marker: #d16b50;
  --evidence-mint: #7bb497;
  --quiet-rule: #aebdb4;
  --paper-high: #f7faf7;
  --ink-muted: #52675b;
}
```

Remove radial glows, translucent dark cards, and gradient decoration. Use a cool light page, dark text, flat rules, and one forest lead block with a clay offset edge. Place `Field Ledger` in a compact utility descriptor, not the main headline. Keep normal body copy at 16–18px, about 1.7 line height, and a maximum 72-character measure.

Home lead selection groups feed items into the most recent 48-hour publication window and chooses the highest-importance verified item within that window, falling back to the newest item. It never searches older windows for a higher score. Feed rows use a narrow status/date column and a wider reading column. Pass `backfilled={item.data.backfilled}` into every FeedCard.

On story pages, add `Backfilled · Original publication <date>` beside status. Style the `Evidence` section as the only forest-tinted terminal block; Summary, Insight, Implication, and Why it matters remain dark text on field paper.

In RSS choose the prefix with:

```ts
const label = e.data.backfilled
  ? "Backfilled"
  : e.data.status[0].toUpperCase() + e.data.status.slice(1);
```

- [ ] **Step 4: Run integration, type, and production build checks**

Run: `cd site && node --test test/*.test.mjs && npm run check && npm run build`  
Expected: tests pass, Astro reports zero errors, and the build completes.

- [ ] **Step 5: Commit**

```bash
git add site/package.json site/package-lock.json site/src/styles/global.css site/src/layouts/Base.astro site/src/pages/index.astro site/src/components/FeedCard.astro site/src/components/FrontCard.astro site/src/components/HealthStrip.astro site/src/components/TrackTag.astro 'site/src/pages/events/[slug].astro' site/src/pages/feed.xml.ts site/test
git commit -m "feat: apply Field Ledger reading experience"
```

---

### Task 7: Full verification and production backfill

**Files:**
- Modify only files required by verification findings.
- Runtime output: `content/feed/*.md`, eligible `content/events/*.md`, and `data/backfills/direct-evidence_2026-06-01_2026-09-01.json`.

**Interfaces:**
- Verifies all prior tasks together.
- Publishes bounded, resumable production batches to `main`.

- [ ] **Step 1: Run complete local verification**

Run:

```bash
uv run ruff check pipeline tests
uv run pytest -q
cd site
node --test test/*.test.mjs
npm run check
npm run build
```

Expected: all commands exit zero. Return to the repository root before subsequent commands.

- [ ] **Step 2: Verify the production selection without writes or model calls**

Run:

```bash
uv run python -m pipeline.backfill_feed \
  --since 2026-06-01T00:00:00Z \
  --until 2026-09-01T23:59:59Z \
  --limit 15 --direct-only --dry-run
```

Expected: `eligible` is nonzero, `excluded` includes all 12 Gemini Search evidence records, `attempted` and filesystem writes are zero, and no API credential is required.

- [ ] **Step 3: Perform browser QA with two feed fixtures**

Build with both fixture files, serve the static site, and inspect `/`, one backfilled `/events/[slug]`, `/fronts`, `/developments`, `/intelligence`, `/sources`, `/archive`, and `/feed.xml`. At 1440×900, confirm the lead headline and Summary are both visible. At widths 768, 390, and 320, confirm `document.documentElement.scrollWidth === innerWidth`, readable body text, visible original date, textual status, keyboard focus, and no console errors.

- [ ] **Step 4: Review the final diff and push implementation to main**

Run:

```bash
git diff --check
git status --short
git log --oneline -12
git fetch origin main
git rev-list --left-right --count origin/main...HEAD
git push origin main
```

Expected: a clean worktree before fetch, zero remote-only commits, and a normal non-force push.

- [ ] **Step 5: Run bounded production batches until complete**

Dispatch:

```bash
gh workflow run backfill-feed.yml \
  --repo yangtai1105/crawlerpolicy \
  --ref main \
  -f since=2026-06-01T00:00:00Z \
  -f until=2026-09-01T23:59:59Z \
  -f limit=15
```

Watch each run with `gh run watch <run-id> --exit-status`. After success, fetch and inspect the manifest summary from `origin/main`. Repeat only while `remaining > 0`; stop immediately on provider failure. Never run two backfill workflows concurrently.

- [ ] **Step 6: Verify the completed public result**

Fast-forward the local main branch, then verify:

```bash
find content/feed -maxdepth 1 -name '*.md' | wc -l
jq '{batch_id, since, until, summary}' data/backfills/direct-evidence_2026-06-01_2026-09-01.json
curl -fsS https://crawlerpolicy.com/ | rg 'Backfilled|Original publication|Latest signals'
curl -fsS https://crawlerpolicy.com/feed.xml | rg '\[Backfilled\]'
```

Confirm the live site returns 200 for `/`, `/fronts`, `/developments`, `/intelligence`, `/sources`, `/archive`, and `/feed.xml`; the newest content carries its original date; and the next Daily Check remains healthy with its unchanged August 30 cutoff.
