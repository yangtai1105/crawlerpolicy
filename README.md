# Crawler Policy

[crawlerpolicy.com](https://crawlerpolicy.com) is a public intelligence product for rights, access, and the agentic web. It turns monitored source changes into replayable evidence, structured developments, durable trends, and a completed weekly intelligence record.

The current taxonomy has nine tracks:

- Policy & Regulation
- Litigation & Legal
- Search & Discovery
- Crawler Controls
- Agentic Web
- Licensing & Monetization
- Standards & Protocols
- Asset Rights
- Measurement & Economics

Those tracks roll up into five fronts: Access & Discovery, Agents & Identity, Rights & Markets, Governance & Law, and Measurement & Economics.

## How it works

```text
source fetch
  -> durable, replayable evidence persisted before analysis
  -> schema-v2 development with event/published/detected dates
  -> durable trend state
  -> completed weekly intelligence issue
```

Discovery-search sources are commentary leads. They may help find primary evidence, but they cannot independently move a trend. The site distinguishes pipeline status as `healthy`, `degraded`, `critical`, or `unknown`; weekly generation refuses critical or stale health. The footer reports the last fully successful run, not merely the most recent attempt.

This rearchitecture intentionally does not backfill history for newly added canonical sources. Their first successful HTML fetch establishes a silent baseline.

## Repository layout

- `pipeline/` — source fetching, evidence persistence, analysis, health, trends, and weekly generation
- `sources.yaml` — monitored-source registry and source roles
- `content/evidence/` — immutable evidence records and replay state
- `content/events/` — current schema-v2 developments
- `content/legacy-events/` — preserved schema-v1 records, excluded from current intelligence
- `content/snapshots/` and `content/raw/` — source snapshots and discovery corpus
- `data/health.json` — stage-aware pipeline health
- `data/trends.json` — durable trend state
- `data/intelligence/` — completed weekly issues
- `site/` — Astro static publication

Older `/reading` dispatches and schema-v1 events remain available through the Legacy Archive. They do not affect current counts, trends, fronts, or weekly intelligence.

## Development

```bash
uv sync
uv run pytest
uv run ruff check pipeline tests
uv run python -m pipeline.check --dry-run --only <source-slug>
uv run python -m pipeline.check
uv run python -m pipeline.weekly_intelligence

cd site
npm ci
npm run check
npm run build
```

The scheduled workflows are `.github/workflows/daily-check.yml` and `.github/workflows/weekly-reading.yml`. The latter keeps its historical filename, but its job and command now build Weekly Intelligence.

Runtime secrets depend on enabled source types. Daily checks use `ANTHROPIC_API_KEY`; grounded discovery needs `GEMINI_API_KEY`; GitHub sources can use `GITHUB_TOKEN`; Cloudflare Browser Rendering sources need `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_EMAIL`, and `CLOUDFLARE_CRAWLER_API_KEY`. `ALERT_EMAILS` and `RESEND_API_KEY` are injected by the daily workflow as reserved placeholders; the current pipeline does not send alerts.
