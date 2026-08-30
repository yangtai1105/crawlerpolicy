# CLAUDE.md

Product: **Crawler Policy** — Rights, Access & Agentic Web Intelligence

Live site: **https://crawlerpolicy.com**

Repository: `yangtai1105/crawlerpolicy` · Vercel project: `crawlerpolicy`

Current design: `docs/superpowers/specs/2026-08-29-web-intelligence-rearchitecture-design.md`

## Product model

Crawler Policy is a Git-backed intelligence publication. Scheduled pipelines monitor authoritative sources and convert source changes into a traceable chain:

```text
fetch -> durable evidence persisted before analysis -> schema-v2 development -> durable trend -> weekly intelligence
```

Every current development keeps three distinct dates when available:

- `event_date`: when the underlying development occurred
- `published_at`: when the source says it was published
- `detected_at`: when the pipeline observed it

The nine canonical tracks are `policy-regulation`, `litigation-legal`, `search-discovery`, `crawler-controls`, `agentic-web`, `licensing-monetization`, `standards-protocols`, `asset-rights`, and `measurement-economics`.

They roll up to five fronts: `access-discovery`, `agents-identity`, `rights-markets`, `governance-law`, and `measurement-economics`.

## Current architecture

```text
pipeline/
├── check.py                   # daily orchestration and stage-aware health
├── evidence.py                # immutable evidence store and replay queue
├── event_writer.py            # schema-v2 development records
├── trends.py                  # durable trend transitions
├── weekly_intelligence.py     # completed weekly issue generation
└── fetchers/                  # HTML, RSS, GitHub, IETF, Gemini, CF Browser

content/
├── evidence/                  # replayable evidence records
├── events/                    # current schema-v2 developments only
├── legacy-events/             # frozen schema-v1 records
├── snapshots/                 # source snapshots
└── raw/                       # discovery corpus

data/
├── health.json                # healthy/degraded/critical/unknown
├── trends.json                # persistent trend state
└── intelligence/YYYY-Www.json

sources.yaml                   # source tier, role, track, and fetch configuration
site/                          # Astro static publication
.github/workflows/
├── daily-check.yml            # 08:00 UTC daily
└── weekly-reading.yml         # historical filename; current Weekly Intelligence job
```

The site architecture is `/`, `/intelligence`, `/intelligence/{week}`, `/fronts/{front}`, `/developments`, `/sources`, `/sources/{slug}`, `/about`, and `/archive`. Current event detail pages use `/events/{slug}`. The archive also preserves old `/reading` dispatches and schema-v1 event pages, but neither feeds current intelligence.

## Source and evidence rules

- Primary and official sources are the basis for factual claims and trend movement.
- `gemini_search` sources are commentary/discovery leads. They cannot independently advance a trend.
- Evidence is written before analysis and remains available if analysis fails. A later run replays pending evidence instead of refetching or losing it.
- HTML and IETF sources establish a silent baseline on first observation. Do not backfill history for newly added canonical sources.
- RSS and GitHub sources retain their bounded catch-up behavior.
- HTML fetching may follow a bounded explicit page relocation; do not add unrestricted crawling.
- Cloudflare-challenged sources use `cf_browser_run` only when ordinary HTML fetches cannot recover the content.

## Health and publication rules

Health is stage-aware:

- `healthy`: required work completed and no material degradation
- `degraded`: enough required work completed for publication, with partial failures recorded
- `critical`: required coverage is insufficient or a blocking stage failed
- `unknown`: health is absent, stale, or uses an unsupported schema

The site footer's timestamp means the last fully successful run. It must never imply that a failed attempt was successful. Weekly Intelligence refuses to publish from critical or stale health; a completed issue is stored under `data/intelligence/` and trend state persists in `data/trends.json`.

## Commands

```bash
uv sync
uv run pytest
uv run ruff check pipeline tests

# Inspect one source without committing pipeline output
uv run python -m pipeline.check --dry-run --only <source-slug>

# Scheduled entry points
uv run python -m pipeline.check
uv run python -m pipeline.weekly_intelligence

# Site verification
cd site
npm ci
npm run check
npm run build
npm run dev
```

The Astro dev server is at `http://localhost:4321`. Restart it after pipeline content changes if a content collection appears stale.

## Secrets and operations

GitHub Actions supplies secrets at runtime:

- `ANTHROPIC_API_KEY` — event analysis and weekly synthesis
- `GEMINI_API_KEY` — grounded discovery sources
- `GITHUB_TOKEN` — higher-rate authenticated GitHub source fetching
- `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_EMAIL`, `CLOUDFLARE_CRAWLER_API_KEY` — Browser Rendering sources
- `ALERT_EMAILS`, `RESEND_API_KEY` — reserved workflow placeholders; no current alerter consumes them

Manual workflow triggers:

```bash
gh workflow run daily-check.yml
gh workflow run weekly-reading.yml
```

Both workflows commit generated artifacts back to the active branch. The daily workflow preserves partial results even when the overall run is critical, then exits non-zero so the failure remains visible.

## Editing invariants

- Add sources through `sources.yaml`; assign canonical track, source tier, and source role.
- Preserve legacy records as read-only archive material. Do not mix `content/legacy-events` into current loaders or counts.
- Old compatibility modules and data may remain while the archive still needs them, but the current site must consume schema-v2 events, stage-aware health, trends, and completed intelligence issues.
- Run Python tests and Ruff plus Astro check/build before pushing. Check staged changes for secrets.
