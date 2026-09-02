# Crawler Policy

[crawlerpolicy.com](https://crawlerpolicy.com) is an English-language intelligence publication about the relationship between AI systems and the open web. It turns source changes into a readable daily feed while preserving the evidence needed to distinguish verified developments, reported stories, and early signals.

The public taxonomy has five themes — Access & Discovery, Agents & Identity, Rights & Markets, Governance & Law, and Measurement & Economics — backed by nine internal tracks.

## What the pipeline publishes

Every daily feed item contains four editorial layers:

- **Summary** — what happened.
- **Insight** — the new pattern or mechanism in the evidence.
- **Implication** — what is likely to change for relevant actors.
- **Why it matters** — why the reader should care now.

Publication status is deterministic, not assigned by the model:

- `verified` uses primary or measurement evidence;
- `reported` comes from configured specialist or publisher sources;
- `signal` is an early, concrete observation from a commentary source.

Only a `verified` and `material` item can enter `content/events/`, move a durable trend, or support a weekly conclusion. Reported items and signals remain readable in the daily feed without being promoted into stronger evidence.

## How it works

```text
configured direct sources
  -> fetch and normalize
  -> persist immutable evidence before analysis
  -> enforce the 2026-08-30 publication cutoff
  -> Gemini 3.7 structured analysis
  -> deterministic publication status
  -> content/feed daily item
  -> optional verified development
  -> trends and completed weekly intelligence
  -> Astro build and Vercel deployment
```

Ordinary HTML, RSS, GitHub, IETF, and browser-rendered sources are fetched without an LLM. Gemini receives the already-fetched evidence and returns structured analysis. If authentication, quota, or billing fails, the provider circuit stops additional model calls; fetched evidence remains pending and can be replayed on a later run.

The daily publication cutoff is `2026-08-30T00:00:00Z`. Earlier underlying items are never presented as current news. A separate, explicitly labeled backfill can publish preserved direct-source evidence with its original date and processing provenance. The first successful fetch of a stable HTML source establishes a baseline instead of inventing a change.

Google Search grounding is not part of the active publication pipeline. `gemini_search` entries remain in `sources.yaml` with `enabled: false` while their retention and product-use constraints are reviewed.

## Repository layout

- `pipeline/` — fetching, evidence, Gemini analysis, publication rules, health, trends, and weekly generation
- `sources.yaml` — monitored-source registry, source roles, and enabled state
- `content/evidence/` — immutable evidence records and replay state
- `content/feed/` — canonical public daily-feed records
- `content/events/` — verified material developments only
- `content/legacy-events/` — preserved schema-v1 records, excluded from current intelligence
- `content/snapshots/` and `content/raw/` — source snapshots and raw discovery corpus
- `data/health.json` — stage-aware pipeline health
- `data/trends.json` — durable trend state
- `data/intelligence/` — completed weekly issues
- `site/` — Astro static publication

Older `/reading` dispatches and schema-v1 events remain available through the Legacy Archive. They never seed the new feed, trends, themes, or weekly intelligence.

## Required APIs and secrets

The analysis layer uses one model provider:

- `GEMINI_API_KEY` — required for daily relevance, four-layer analysis, state of play, and weekly synthesis.
- `GEMINI_ANALYSIS_MODEL` — optional; defaults to `gemini-3.7-flash`.
- `GITHUB_TOKEN` — supplied automatically in GitHub Actions and used for GitHub source fetching and commits.
- `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_EMAIL`, and `CLOUDFLARE_CRAWLER_API_KEY` — required only for enabled `cf_browser_run` sources.
- `PUBLICATION_CUTOFF` — optional ISO timestamp; production pins it to `2026-08-30T00:00:00Z`.

An Anthropic API key is not required. The legacy `ALERT_EMAILS` and `RESEND_API_KEY` workflow values are reserved for future notifications; the current pipeline does not send email.

## Local development

```bash
uv sync
uv run ruff check pipeline tests
uv run pytest -q

# Validates a source path without writing publication files.
GEMINI_API_KEY=... uv run python -m pipeline.check --dry-run --only gptbot

# Runs all enabled sources and writes replayable content.
GEMINI_API_KEY=... uv run python -m pipeline.check

# Builds a weekly issue from a completed verified window.
GEMINI_API_KEY=... uv run python -m pipeline.weekly_intelligence

# Count eligible direct-source records without model calls or writes.
uv run python -m pipeline.backfill_feed \
  --since 2026-06-01T00:00:00Z \
  --until 2026-09-01T23:59:59Z \
  --limit 15 --direct-only --dry-run

# Process one resumable local backfill batch.
GEMINI_API_KEY=... uv run python -m pipeline.backfill_feed \
  --since 2026-06-01T00:00:00Z \
  --until 2026-09-01T23:59:59Z \
  --limit 15 --direct-only

cd site
npm ci
npm run check
npm run build
npm run dev
```

The scheduled workflows are `.github/workflows/daily-check.yml` and `.github/workflows/weekly-reading.yml`. Daily Check runs at 08:00 UTC, commits newly fetched evidence and publication records, and lets Vercel deploy the static site from `main`. Weekly Intelligence runs on Mondays at 13:00 UTC and refuses critical or stale evidence windows.

## Failure behavior

The site continues serving the last successful publication when a run fails. A degraded or critical run shows a restrained “Updates delayed” notice instead of replacing editorial content with pipeline diagnostics. Evidence fetched before a model failure stays pending for replay, and repeated replay never creates duplicate feed items.
