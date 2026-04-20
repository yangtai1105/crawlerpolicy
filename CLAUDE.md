# CLAUDE.md

Site name: **AI Content Ecosystem Insights** · Live at **https://crawlerpolicy.com**
GitHub: `yangtai1105/crawlerpolicy` (public) · Vercel project: `crawlerpolicy`
Design spec: `docs/superpowers/specs/2026-04-18-ai-ecosystem-tracker-design.md`

## What this project does

An automated publication tracking the AI-content-ecosystem across three pillars:

- **Crawler docs** — vendor documentation for AI crawlers (OpenAI, Anthropic, Google, etc.)
- **Ecosystem** — publisher actions, regulators, CDN controls, licensing deals
- **Agent** — AI agent infrastructure, bot-identity standards, protocols

And three distinct output modes:

1. **Feed** (`/`): daily stream of detected material changes from 32 tracked sources. Events have a News section + Why-it-matters with inline markdown citations to primary sources.
2. **Pillar digests** (top of `/`, detail at `/pillars/{pillar}`): LLM-synthesized "state of the pillar" briefings. Window = 30d for ecosystem/agent, **365d for crawler** (crawler changes are rare). Refreshed daily.
3. **Weekly Dispatch** (`/reading`): Mondays. Four topic groups (Crawling & Publisher Controls / Agents / Copyright & Legal / Web Ecosystem & AI Impact), each with a 1-2 sentence TLDR + 5-10 curated items. Sources: investigative journalism, op-eds, policy critique, field reports — NOT vendor announcements.

## Architecture

**Git-as-DB, no backend.** Scheduled pipelines write markdown + JSON to the repo; Vercel rebuilds the static Astro site on every push.

```
pipeline/ (Python, uv)
├── check.py               # daily cron entrypoint
├── critical_reading.py    # weekly (Mon) Gemini dispatch
├── fetchers/
│   ├── html_page.py       # readability+body-fallback extractor
│   ├── rss_feed.py
│   ├── github_repo.py
│   ├── ietf_draft.py
│   ├── gemini_search.py   # Gemini 2.5 Flash + Google Search grounding
│   └── cf_browser_run.py  # for CF-challenged sites (rarely needed)
├── differ.py · relevance.py · analyzer.py · event_writer.py
├── state_of_play.py       # extracts per-crawler UA tables + opt-out matrix
├── pillar_digest.py       # per-pillar synthesis (30d/365d windowed)
├── wayback.py + bootstrap_baseline.py  # seeds 6-month baselines for html_page

content/
├── events/*.md            # one event per material change; frontmatter + body
├── snapshots/{slug}/{date}.{ext}  # per-source history
└── raw/{slug}/{YYYY-MM}.jsonl     # every keyword-matched item (trend analysis corpus)

data/
├── opt-out-matrix.json    # per-vendor user_agents + support flags (sidebar)
├── pillar-digests.json    # daily pillar syntheses
└── critical-reading/YYYY-Www.json  # weekly Dispatch per ISO week

sources.yaml               # 32 active sources
site/                      # Astro SSG; root=site in Vercel config
.github/workflows/
├── daily-check.yml        # 08:00 UTC daily
└── weekly-reading.yml     # Mondays 13:00 UTC
```

## Source types

| Type | Use | Gotchas |
|---|---|---|
| `html_page` | Vendor crawler docs, regulator pages | Readability fails on Intercom-style; html_page.py has body-fallback when readability < 1500 chars |
| `rss_feed` | Blogs, press releases, CF changelogs | `keyword_filter` optional (product-specific feeds skip it) |
| `github_repo` | Spec repos | Unauthenticated = 60 req/hr, 403 is handled gracefully as non-fatal |
| `ietf_draft` | Specific IETF drafts | Revision-based diffs |
| `gemini_search` | Topic queries (news discovery) | DIFFABLE mode — one digest per query, diff'd over time; retry up to 5x on empty grounded responses |
| `cf_browser_run` | CF-challenged vendor docs only | Slow (3-7 min); legacy auth (X-Auth-Email + X-Auth-Key, NOT Bearer) |

`baseline_url` field on a Source: if a URL was rebranded recently, bootstrap_baseline uses this alternate URL to seed ~6-month Wayback history. Used for `gptbot` (tracked at developers.openai.com, baseline from platform.openai.com).

## Models + cost routing

| Task | Model | Rationale |
|---|---|---|
| Crawler pillar analyzer | `claude-sonnet-4-6` | Rare events, big diffs, quality matters |
| News pillars analyzer | `claude-haiku-4-5-20251001` | High volume, simpler per-item — ~4× cheaper |
| Relevance filter (haiku_relevance) | Haiku | Tool-use verdicts |
| State of Play per-UA extraction | Haiku | Simple factual extraction; max_tokens=2500 (was 300 — too small) |
| Pillar digests | Haiku | 3 calls/day |
| Gemini search sources | `gemini-2.5-flash` + Google Search grounding | Web discovery |
| Weekly Dispatch | gemini-2.5-flash (4 parallel calls) | `max_output_tokens=32768` — reasoning tokens eat the budget otherwise |

Override per source via `model: sonnet|haiku|opus|claude-<exact-id>` in sources.yaml.

**Steady-state cost: ~$3/month** (~$2.35 LLM + ~$1 domain).

## Key invariants + gotchas learned the hard way

- **Gemini grounding-redirect URLs (`vertexaisearch.cloud.google.com/grounding-api-redirect/...`) expire fast and 404 for non-Gemini clients.** critical_reading.py drops items with those URLs rather than trying to resolve; gemini_search.py does follow them (they're still fresh at that moment). Prompt explicitly forbids returning redirect URLs.
- **Gemini grounded responses are occasionally empty** (finish_reason STOP, 0 chars). Retry up to 5x with slightly varied temperature.
- **Tool-use responses from Haiku occasionally drop required fields** under long prompts. `analyzer.py` defensively fills defaults rather than crashing the run.
- **Readability-lxml extraction fails silently** on some vendor docs (Claude support, Amazon developer docs); falls back to full body text (scripts/nav/header/footer stripped) when output < 1500 chars.
- **Astro `build.format: "directory"` is required for Vercel routing.** `"file"` produces flat `/foo.html` files that Vercel 404s on `/foo`.
- **`last_hash` semantics** in check.py: for html_page sources, if the hash matches we skip early; otherwise we load_latest **before** saving today's snapshot (otherwise prev = today, no diff).
- **First-seen behavior** differs by type:
  - `html_page`, `ietf_draft`: silent baseline (save snapshot, no event)
  - `rss_feed`, `github_repo`: backfill items from last 30 days (`BACKFILL_DAYS=30`), record older guids as seen
  - `gemini_search`: the first run IS the event (digest is valid content)

## Common task patterns

### Add a new source
Edit `sources.yaml`, append an entry, commit. First daily run catch-up handles the rest. No migration. For RSS/GitHub, ~30d of items get analyzed. For html_page, consider running `uv run python -m pipeline.bootstrap_baseline` to seed a Wayback baseline.

### Add a new Gemini search query
Same — one `gemini_search` entry with `query` + `lookback_days`. Cost: ~$0.18/mo per daily query.

### Rename a source's display
Edit `sources.yaml`. StateOfPlay component resolves names from sources.yaml at render time (not from opt-out-matrix.json) — no regeneration needed.

### Modify the news analyzer prompt
`pipeline/analyzer.py`. Changes take effect on next event. Old events are frozen.

### Change pillar digest window or framing
`pipeline/pillar_digest.py`. `PILLAR_WINDOW_DAYS` dict + `_SYSTEM_NEWS` / `_SYSTEM_CRAWLER` prompts.

### Tighten the Dispatch quality filter
`pipeline/critical_reading.py`. `_prompt_for()`. Strengthen the EXCLUDE list or add specific preferred outlets.

## Operational notes

- **Secrets** live in GitHub Actions repo secrets (not in `.env.example`): `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `CLOUDFLARE_CRAWLER_API_KEY`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_EMAIL`, `ALERT_EMAILS` (placeholder until Plan 3).
- **Rotating secrets**: add new secret value in GH Actions settings, no code change needed. Next run picks it up.
- **Triggering manually**: `gh workflow run daily-check.yml` or `gh workflow run weekly-reading.yml` (or via GitHub UI).
- **Checking health**: `data/health.json` is updated by each daily run; also surfaced in the site footer.
- **Vercel**: auto-deploys on every push to `main`. The daily-check workflow commits back with `daily-check YYYY-MM-DD: auto-run`.

## What's NOT built (future work)

- **Plan 3**: `/api/subscribe` + `/api/confirm` (Vercel serverless + Vercel KV), weekly email digest via Resend, immediate crawler-alert email to `ALERT_EMAILS`. Design is in the spec doc.
- **Tagger + tier system**: multi-topic tags per event, Flagged/Popular/Other tiers. Would broaden the source net to HN/Reddit/arxiv/Bluesky. Discussed but not started.
- **Snapshot side-by-side diff viewer** on `/sources/[slug]`: deferred to v1.1. Server-side unified diffs are already rendered; the side-by-side UI is the missing piece.

## When you edit this project

- **Python**: `uv sync`, `uv run pytest` (39 tests), `uv run python -m pipeline.check --dry-run --only <slug>` for per-source checking.
- **Astro**: `cd site && npm run dev` → http://localhost:4321. Dev server caches content collections at startup — restart after pipeline runs to see new events.
- **Before pushing**: ensure `uv run pytest` passes and no secrets accidentally staged (`.env` is gitignored).
