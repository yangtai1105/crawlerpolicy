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
