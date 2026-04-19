# AI Ecosystem Tracker — Design Spec

**Date**: 2026-04-18
**Status**: Draft for review
**Owner**: internal (公司团队)

---

## 1. Overview

A public-facing website that automatically tracks changes across the AI content ecosystem — AI crawler/bot documentation, content ecosystem news, and AI agent infrastructure news — and presents them with LLM-generated analysis to an audience of internal company readers and external stakeholders.

**Positioning**: a monitoring + alerting publication. The crawler documentation tracker is the core value (rare-but-important changes in OpenAI / Anthropic / Google / Apple / Meta bot policy). Ecosystem and agent news fill the signal stream between crawler changes.

---

## 2. Audience & Success Criteria

- **Primary audience**: internal company team — they need to be the first to know when an AI crawler policy changes, and have a running reference for the state of the ecosystem.
- **Secondary audience**: external industry readers (publishers, policy folks, AI infra researchers) who subscribe to the newsletter or RSS.
- **Success in v1**: the internal team stops manually watching 28+ pages and external subscribers see the site as a serious ecosystem reference. Adding new sources over time is expected to be a routine, zero-code operation (edit `sources.yaml`, open PR).

Not in scope: community, comments, user accounts, personalization.

---

## 3. Tracked Sources (v1)

28 sources across three pillars for v1. `sources.yaml` in repo root is the source of truth; the list below is the v1 seed. Adding sources over time is expected and should be trivial — see § 6.6 "Adding a new source".

### Pillar 1 — Crawler / Bot documentation (HTML diff)

Low-frequency (typically once or twice a year per source), high-signal. Each source is a fixed URL whose rendered content is diffed day-over-day.

| # | Vendor | Page (seed) |
|---|---|---|
| 1 | OpenAI | GPTBot / OAI-SearchBot / ChatGPT-User documentation |
| 2 | Anthropic | ClaudeBot / Claude-User crawler documentation |
| 3 | Google | Google-Extended entry in common crawlers overview |
| 4 | Perplexity | PerplexityBot / Perplexity-User documentation |
| 5 | Apple | Applebot-Extended support article |
| 6 | Meta | Meta-ExternalAgent / FacebookBot documentation |
| 7 | Microsoft | Bingbot / Microsoft AI crawler documentation (docs page covering UA strings, `nocache` / `noarchive` directives, Copilot-related bot guidance) |
| 8 | Amazon | Amazonbot documentation (developer.amazon.com/amazonbot) |
| 9 | Common Crawl | CCBot FAQ |

### Pillar 2 — Content ecosystem news (RSS + keyword filter + Haiku relevance pass)

Medium frequency. Every source goes through the two-stage relevance funnel (§ 6.4) before any expensive analysis. Broad sources (Cloudflare blog ~60 posts/month) typically funnel down to 3–5 events/month.

| # | Source | Type | Filter intent |
|---|---|---|---|
| 10 | Cloudflare Blog | rss_feed | AI bot, crawler, content protection |
| 11 | Fastly Blog | rss_feed | same |
| 12 | Akamai Blog | rss_feed | bot management, AI crawler, CDN defenses |
| 13 | DataDome Blog | rss_feed | bot detection, AI scraper reports |
| 14 | UK CMA press releases | rss_feed | AI + content/market |
| 15 | EU Commission Digital press | rss_feed | AI Act, content, DMA |
| 16 | EU AI Office | rss_feed (fall back to html_page if no RSS) | AI Act enforcement, guidance |
| 17 | US FTC press releases | rss_feed | AI / generative AI enforcement |
| 18 | US Copyright Office | rss_feed | AI and copyright guidance, reports |
| 19 | News/Media Alliance | rss_feed | publisher-side AI ecosystem actions |
| 20 | Reddit Corporate Blog | rss_feed | AI data deals, crawler / API policy |

### Pillar 3 — AI Agent ecosystem (mixed: IETF + GitHub + vendor blogs)

| # | Source | Type | Tracking scope |
|---|---|---|---|
| 21 | IETF datatracker — Web Bot Auth | ietf_draft | revisions of the Web Bot Auth draft |
| 22 | Core spec GitHub repo (e.g. `cloudflareresearch/web-bot-auth`) | github_repo | releases, material merged PRs |
| 23 | `modelcontextprotocol/specification` (MCP) | github_repo | spec repo releases + material PRs |
| 24 | Browserbase Blog | rss_feed | agent infra product + ecosystem posts |
| 25 | Cloudflare Research Blog | rss_feed | bot auth, agent identity research |
| 26 | Anthropic News | rss_feed | Claude Agents / Computer Use / MCP updates |
| 27 | OpenAI Blog | rss_feed | Operator / Agents / Assistants updates |
| 28 | LangChain Blog | rss_feed | agent framework material changes |

Source URLs for pillars 2 and 3 finalized during implementation; seed list replaceable via `sources.yaml`. Where an official RSS feed is unavailable, fall back to `html_page` on the listings page or use a listings-page scraper with stable date anchors.

---

## 4. System Architecture

No custom backend service. Everything is either (a) a scheduled pipeline that writes to git, or (b) the static site that reads from git, or (c) two serverless functions for subscription management.

```
┌─────────────────────────────────────────────────────────────┐
│  GitHub Actions                                              │
│  ────────────────────────────────────────────────────────── │
│  daily-check.yml  (cron: daily 08:00 UTC)                   │
│    └─ python pipeline/check.py                              │
│         ├─ fetch sources in parallel                        │
│         ├─ hash-compare against latest snapshot             │
│         ├─ on change: diff → Claude → markdown event        │
│         ├─ regenerate data/*.json (State of Play)           │
│         ├─ git commit (one commit per run)                  │
│         └─ on crawler material change: Resend alert email   │
│              to ALERT_EMAILS                                 │
│                                                              │
│  weekly-digest.yml (cron: Monday 09:00 UTC)                 │
│    └─ python pipeline/digest.py                             │
│         ├─ read content/events/ last 7 days                 │
│         ├─ group by pillar, crawler section first           │
│         ├─ read confirmed subscribers from Vercel KV        │
│         └─ send via Resend                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │ git push
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Vercel (Hobby plan)                                         │
│  ────────────────────────────────────────────────────────── │
│  Static site build (Astro):                                  │
│    - reads content/events/*.md    → feed + event pages      │
│    - reads content/snapshots/*    → per-source timelines    │
│    - reads data/*.json            → State of Play widget    │
│    - generates feed.xml (RSS)                                │
│                                                              │
│  Serverless functions:                                       │
│    /api/subscribe  (TS) → Vercel KV + Resend confirm email  │
│    /api/confirm    (TS) → double-opt-in token exchange      │
└─────────────────────────────────────────────────────────────┘
```

**Key principles**:
- **No backend service.** Only a scheduled pipeline and a static site.
- **Git is the history.** Every snapshot is a committed file; `git log` is each source's timeline.
- **LLM work happens in the pipeline, not in the site.** Site only renders markdown + JSON; all API costs occur at cron time and are budget-able.
- **Subscriber list in Vercel KV free tier.** No self-hosted DB.

---

## 5. Data Layout (Git-as-DB)

```
ai-ecosystem-tracker/
├── sources.yaml                 # 28 sources (v1); expected to grow over time
├── content/
│   ├── snapshots/
│   │   └── {source_slug}/
│   │       └── {YYYY-MM-DD}.{ext}      # one per content-change day
│   └── events/
│       └── {YYYY-MM-DD}-{source_slug}-{slug}.md
├── data/
│   ├── opt-out-matrix.json      # per crawler: supports robots.txt? UA opt-out? days since change?
│   ├── policy-fronts.json       # active regulator inquiries
│   └── agent-standards.json     # IETF draft state, spec versions
│   └── health.json              # last run timestamp, per-source last-success
├── pipeline/
│   ├── check.py                 # daily cron entrypoint
│   ├── digest.py                # weekly cron entrypoint
│   ├── fetchers/
│   │   ├── html_page.py
│   │   ├── rss_feed.py
│   │   ├── github_repo.py
│   │   └── ietf_draft.py
│   ├── differ.py                # normalize → markdown → line diff
│   ├── analyzer.py              # Claude API call, structured JSON return
│   ├── state_of_play.py         # Haiku extraction → data/*.json
│   ├── alerter.py               # Resend alert for crawler material changes
│   └── emails/
│       ├── alert.html.j2
│       └── digest.html.j2
├── site/                        # Astro static site
│   ├── src/pages/
│   │   ├── index.astro          # hero + feed + State of Play
│   │   ├── events/[slug].astro
│   │   ├── sources/[slug].astro
│   │   ├── archive.astro        # deferred to v1.1
│   │   ├── about.mdx
│   │   ├── subscribe.astro
│   │   └── feed.xml.ts
│   ├── src/components/
│   └── astro.config.mjs
├── api/                         # Vercel serverless (TypeScript)
│   ├── subscribe.ts
│   └── confirm.ts
├── .github/workflows/
│   ├── daily-check.yml
│   └── weekly-digest.yml
├── .env.example
└── README.md
```

### Event file schema

```markdown
---
slug: openai-gptbot-robots-update
title: OpenAI rewrites GPTBot policy — opt-out semantics now tied to robots.txt path specificity
source: gptbot                       # matches sources.yaml key
pillar: crawler                      # crawler | ecosystem | agent
detected_at: 2026-04-18T08:00:00Z
source_url: https://platform.openai.com/docs/gptbot
change_kind: material                # material | cosmetic | noise (only `material` produces events)
importance: 0.82                     # 0–1; crawler baseline 0.75, news LLM-scored
---

## What changed
(LLM 2–3 sentences — for crawler pillar, may be 1 sentence template-heavy)

## Implication
(LLM 3–5 sentences — omitted/short for crawler pillar when nothing substantial to say)

## Raw diff
<details>
<summary>View diff</summary>

```diff
(full diff)
```
</details>
```

### `sources.yaml` schema (sketch)

```yaml
# html_page — pillar 1 crawler docs
- slug: gptbot
  pillar: crawler
  type: html_page
  url: https://platform.openai.com/docs/gptbot
  content_selector: "main article"       # optional; falls back to readability
  model: sonnet                          # optional override; default sonnet
  display_name: OpenAI GPTBot

# rss_feed — pillar 2 ecosystem blog
- slug: cloudflare-blog
  pillar: ecosystem
  type: rss_feed
  url: https://blog.cloudflare.com/rss/
  keyword_filter: ["AI bot", "crawler", "scraper", "content", "robots.txt", "training"]
  display_name: Cloudflare Blog

# rss_feed — pillar 2 regulator press
- slug: us-ftc
  pillar: ecosystem
  type: rss_feed
  url: https://www.ftc.gov/news-events/news/press-releases/rss
  keyword_filter: ["AI", "artificial intelligence", "generative", "chatbot", "training data"]
  display_name: US FTC

# github_repo — pillar 3 agent spec
- slug: mcp-spec
  pillar: agent
  type: github_repo
  repo: modelcontextprotocol/specification
  pr_labels: ["spec", "rfc"]              # optional; PRs not matching are dropped
  pr_path_globs: ["spec/**", "docs/**"]   # optional; alternative to labels
  display_name: Model Context Protocol (spec)

# ietf_draft — pillar 3 standards tracking
- slug: ietf-web-bot-auth
  pillar: agent
  type: ietf_draft
  draft_name: draft-cloudflare-httpbis-web-bot-auth
  display_name: IETF Web Bot Auth
```

### Vercel KV schema

```
subscribers:{email} → JSON {
  status: "pending" | "confirmed" | "unsubscribed",
  confirm_token: string,       # random urlsafe token
  subscribed_at: ISO timestamp,
  confirmed_at: ISO timestamp | null,
  unsub_token: string
}
confirmed_emails → set of email strings (for digest.py fast read)
```

---

## 6. Pipeline Detail

### `check.py` daily flow

1. Load `sources.yaml`.
2. For each source, in parallel (asyncio + httpx), dispatch by `source.type`:

   **`html_page` (pillar 1 crawler docs)** — full-page content diff:
   a. Extract normalized content (`content_selector` or readability).
   b. Compute SHA-256 of normalized content.
   c. Compare with latest snapshot hash in `content/snapshots/{slug}/`.
   d. If identical → skip (no snapshot, no event, no LLM).
   e. If different:
      - Write `content/snapshots/{slug}/{today}.{ext}`.
      - Build semantic diff (HTML → clean markdown → line diff).
      - Call Sonnet analyzer with diff + prev/curr content. Returns `{change_kind, importance, title, what_changed, implication}`.
      - If `change_kind == "material"`: write event file.
      - If `change_kind == "material"` AND `pillar == "crawler"`: trigger `alerter.send_alert(event)` to `ALERT_EMAILS` via Resend.

   **`rss_feed` (most of pillar 2 + agent vendor blogs in pillar 3)** — per-item relevance + analyzer funnel:
   a. Fetch feed; read `state/{slug}.last_checked_at` (or last_seen_guid).
   b. Collect items newer than that timestamp.
   c. For each new item, run the **relevance filter** (see subsection below). Drop irrelevant items entirely — no storage, no analyzer call.
   d. For surviving items, call Sonnet analyzer with item body + title + source context. Returns same structured JSON as above.
   e. If `change_kind == "material"`: write event file (one event per RSS item, not per feed).
   f. Update `last_checked_at`.
   g. No snapshot file for RSS sources — the originating blog post URL is stored in the event frontmatter as the authoritative record.

   **`github_repo` (pillar 3 spec repos)** — releases + material merged PRs:
   a. Via GitHub REST API, list releases and merged PRs since `last_checked_at`.
   b. Each release: auto-relevant (repo is already scoped). Call analyzer on release notes.
   c. Each merged PR: filter by repo-configured labels or paths (e.g., `spec/*`, `RFC/*`); drop low-value PRs (typo fixes, CI changes) via the relevance filter's second pass.
   d. Surviving items → Sonnet analyzer → event.

   **`ietf_draft` (pillar 3 IETF tracking)** — draft revision tracking:
   a. Fetch datatracker metadata for the configured draft name; check current revision number.
   b. If revision > last recorded: save revision text as snapshot, diff against previous, call Sonnet analyzer, emit event.
   c. No relevance filter (we explicitly subscribed to this draft).
3. `state_of_play.py`:
   - For each crawler source, read latest snapshot.
   - Haiku extraction: `{supports_robots_txt, supports_user_agent_opt_out, policy_url, last_changed_days_ago}`.
   - Write `data/opt-out-matrix.json`, `data/policy-fronts.json`, `data/agent-standards.json`.
4. Update `data/health.json` with last-run timestamp and per-source success/failure.
5. `git add -A && git commit -m "daily-check {date}: {n} events, {m} snapshots"` (skip if nothing staged).
6. `git push` → Vercel rebuilds.

### Error handling

- Per-source fetch exception → log, mark source failed in `data/health.json`, continue others.
- LLM API error → exponential backoff 3 retries, then fallback to `{change_kind: "material", title: "{source} content changed (analysis pending)", what_changed: "Automated analysis failed; human review recommended.", implication: ""}`. Next day's run retries analysis on the same diff.
- Whole run unhandled exception → GH Actions native failure notification (emails repo maintainer).
- If same source fails 3 consecutive days → flagged in weekly digest "anomalies" footer.

### Relevance filtering (RSS + GitHub sources)

Broad sources (CDN blogs, regulator press, GitHub repos, vendor blogs) publish far more than is relevant. Two-stage funnel keeps signal high and cost low:

**Stage 1 — keyword filter (regex, zero cost):**
- Each source in `sources.yaml` has a `keyword_filter: [list of terms]`.
- Title and summary are matched case-insensitively against the list.
- No match → discarded immediately. Not stored, not analyzed.
- Typical keyword lists (examples):
  - CDN / bot-mgmt blogs: `["AI bot", "crawler", "scraper", "content protection", "robots.txt", "training data", "agent", "LLM"]`
  - Regulator press: `["AI", "artificial intelligence", "generative", "chatbot", "training data", "large language"]`
  - Agent vendor blogs (OpenAI, Anthropic, LangChain, etc.): `["agent", "operator", "bot", "crawler", "MCP", "auth"]` — used to filter out pure model releases and tutorials

**Stage 2 — Haiku relevance classifier:**
- Items passing stage 1 go through a single Haiku call: "Is this post about AI crawler policy, AI training data / bot behavior, content-ecosystem regulation, or AI agent infrastructure? Return yes/no with a one-line reason."
- "no" items discarded. "yes" items proceed to Sonnet analyzer.
- Haiku call ≈ $0.0001 per item; cheap enough to run on every candidate.

**Never-filtered sources** (relevance guaranteed by source scope):
- All pillar 1 `html_page` sources (explicit URLs of AI crawler docs).
- All `ietf_draft` sources (explicit draft tracking).
- GitHub releases (repo itself is in-scope).

**Result**: only items that pass both stages become events. A typical broad source (e.g., Cloudflare blog at ~60 posts/month) funnels down to 3–5 events/month; noise ratio stays manageable.

### LLM usage

- **Analyzer (primary)**: Claude Sonnet 4.6 by default. Per-source override via `model: opus` in `sources.yaml` for high-priority sources. Structured output via tool use (returns typed JSON, not markdown).
- **State of Play extractor**: Claude Haiku 4.5. Cheap, factual extraction from latest snapshot text.
- **Prompt caching**: enabled on all calls. System prompt + source-specific context cached 5-minute TTL. In practice most cache hits come from `state_of_play.py` batch run right after `check.py`.

### Pillar-specific behavior

| Pillar | LLM prompt | Baseline importance | Alert behavior |
|---|---|---|---|
| crawler | Classify `change_kind`; write ≤2-sentence title and ≤3-sentence `what_changed`; `implication` optional (omit if nothing substantial) | 0.75 | immediate email to `ALERT_EMAILS` if material |
| ecosystem | Classify; full `what_changed` and `implication` | LLM-scored 0–1 | weekly digest only |
| agent | Classify; full `what_changed` and `implication` | LLM-scored 0–1 | weekly digest only |

Importance scoring rubric (in the analyzer prompt, for news pillars): 0.9+ reserved for ecosystem-reshaping events (new major regulator action, a top-5 AI lab announcing a new bot, a widely-adopted standard finalized); 0.6–0.8 for notable-but-bounded news (new tool launch, non-binding consultation); 0.3–0.5 for incremental commentary; below 0.3 flagged as cosmetic/noise candidates for the classifier's reconsideration.

### `digest.py` weekly flow

1. Read `content/events/*.md` with `detected_at` in last 7 days where `change_kind == "material"`.
2. Group by pillar: crawler section first if any crawler events present (even a single one) else skip section; then ecosystem, then agent. If all three sections are empty, skip the send entirely (don't email an empty digest).
3. Render `emails/digest.html.j2` with the grouped events.
4. Read `confirmed_emails` from Vercel KV.
5. Send via Resend API (per-email `unsub_token` in List-Unsubscribe header).
6. Log send status; no git commit.

### Adding a new source (operational workflow)

A first-class design goal: the team is expected to add sources continuously, so adding must be **zero-code** for the four supported source types.

**The four supported types cover the vast majority of expected additions:**

| type | Expected use | Minimum config in `sources.yaml` |
|---|---|---|
| `html_page` | A fixed URL whose rendered content should be diffed day-over-day | `slug`, `pillar`, `url`, `display_name` (+ optional `content_selector`, `model`) |
| `rss_feed` | A blog or press-release feed; per-item candidates go through the relevance funnel | `slug`, `pillar`, `url`, `display_name`, `keyword_filter` |
| `github_repo` | A repo whose releases and material PRs are in-scope | `slug`, `pillar`, `repo` (`owner/name`), `display_name` (+ optional `pr_labels`, `pr_path_globs`) |
| `ietf_draft` | A specific IETF draft to follow across revisions | `slug`, `pillar`, `draft_name`, `display_name` |

**To add a new source of a supported type:**

1. Open a PR that appends a new entry to `sources.yaml`.
2. Run `python pipeline/check.py --dry-run --only {new_slug}` locally — fetches once, shows what would happen, makes no commits.
3. Merge the PR. The next daily run auto-initializes state (first run creates the initial snapshot / records current last-seen item without emitting events — avoids flooding with "all old items look new").
4. No code change required. No migration. No redeploy (site picks up new source on its first event).

**If a new source needs a new `type`** (e.g., a Mastodon account, a podcast RSS with audio transcripts, a Discord announcement channel): implementing a new fetcher is the only path. Contract:

- Input: source config dict from `sources.yaml`.
- Output: either `(normalized_content, mime_type)` for diff-style sources, or `list[candidate_item]` for per-item sources. The rest of the pipeline (relevance funnel, analyzer, event writer) is type-agnostic.
- Each fetcher is a file in `pipeline/fetchers/` named after the type; the dispatcher in `check.py` finds it by convention.

**Guardrails that make adding sources safe:**

- `--dry-run` mode in `check.py` and per-source `--only` flag for targeted validation.
- A new source's first run is "catch-up" mode: records current state as baseline, emits zero events. This is so that adding e.g. a blog RSS doesn't spam the feed with 100 historical posts.
- `keyword_filter` changes are hot-reloaded every run; tune noise without redeploy.
- Broken sources (fetch errors for 3 days) auto-surface in the digest anomalies footer — no source ever fails silently.

---

## 7. Frontend Pages

Astro SSG build; Vercel auto-deploy on git push.

| Route | Purpose | Data source |
|---|---|---|
| `/` | Homepage: hero (top-importance 48h event) + filter chips + reverse-chron feed + right-sidebar State of Play | Latest 20 events + `data/*.json` |
| `/events/[slug]` | Single event permanent page: title, source badge, detected_at, what/implication, collapsed raw diff, LLM disclosure footer | `content/events/*.md` |
| `/sources/[slug]` | Single-source timeline: header with "last changed N days ago / M historical changes"; event list; snapshot version list | `content/snapshots/{slug}/*` + events filtered by source |
| `/about` | Methodology, tracked sources list, LLM disclosure, feedback email | static `.mdx` |
| `/subscribe` | Email signup form posting to `/api/subscribe` | static |
| `/feed.xml` | RSS, full-text, latest 100 events, ordered by `detected_at` | events |
| `/archive` | **Deferred to v1.1** | — |

### Homepage layout (A + C hybrid, approved)

- Top nav: site title, links to Feed / Sources / Subscribe / RSS, light/dark toggle.
- Hero block (dark background): today's top-importance event within last 48 hours — title + 1-paragraph implication + timestamp + "LLM analysis" tag. If no event in last 48h, hero falls back to the most recent `material` event.
- Filter chips: All / Crawler / Ecosystem / Agent (counts shown).
- Main grid: left column (feed of cards, reverse-chron), right sidebar (State of Play: opt-out matrix with "days since last change" column; policy fronts; agent standards).
- Footer: last check timestamp from `data/health.json`, "LLM-generated analysis" disclosure, feedback email.

### Aesthetic direction

Editorial, not SaaS dashboard. References: *The Information*, *Stratechery*, *Platformer*.

- Dark theme default, light toggle.
- Serif display font for titles (distinctive, not Playfair-cliché); sans for body; monospace for diffs and code.
- Information-dense (this is a tracker; whitespace is the enemy of signal density).

Final typography, color, and micro-interaction decisions deferred to implementation phase using `frontend-design` skill.

### Snapshot diff viewer on `/sources/[slug]`

Client-side diff2html between any two selected snapshot dates. Zero server cost (static JSON index + client render). **Deferred to v1.1** — v1 ships with just the event list and snapshot file list.

### LLM disclosure

Every event page footer: "What changed and Implication sections generated by Claude Sonnet 4.6 from the raw diff shown above. Diff is authoritative." `/about` page details methodology.

---

## 8. Distribution

| Channel | Trigger | Audience | Content |
|---|---|---|---|
| Website | `git push` → Vercel build | public | permanent, linkable |
| RSS (`/feed.xml`) | build time | RSS subscribers | full-text events, reverse-chron, up to 100 |
| Weekly email digest | Monday 09:00 UTC GH Actions | confirmed Vercel KV subscribers | past 7 days' events grouped by pillar (crawler first) |
| Crawler alert email | `check.py` on detecting `crawler && material` | `ALERT_EMAILS` env (internal fixed list) | single event snapshot + link to event page |

Email template: single shared Jinja2 HTML template with inline CSS for Gmail/Outlook compatibility; plain-text fallback; `List-Unsubscribe` header on digest emails (one-click Gmail unsubscribe compliant).

### Subscription flow

1. User submits email on `/subscribe`.
2. `/api/subscribe` writes `subscribers:{email}` with `status: pending`, generates `confirm_token`, sends confirmation email via Resend with link `https://.../api/confirm?token=...`.
3. User clicks link. `/api/confirm` validates token, sets `status: confirmed`, adds email to `confirmed_emails` set, redirects to `/subscribe?confirmed=1` success page.
4. Unsubscribe: any digest email `List-Unsubscribe` link hits `/api/confirm?unsub_token=...` which removes from `confirmed_emails` and sets `status: unsubscribed`.

---

## 9. Operations

### Cost estimate (monthly)

| Item | Cost |
|---|---|
| Vercel Hobby | $0 |
| GitHub Actions (public repo) | $0 |
| Vercel KV free tier (256 MB, 30k commands) | $0 |
| Resend free tier (3k emails/mo, 100/day) | $0 |
| Claude API — Haiku relevance filter (~700 items/mo across broad feeds) | <$0.10 |
| Claude API — Sonnet analyzer (~40–60 surviving events/mo) | ~$2–4 |
| Claude API — Haiku SoP extraction (9 crawler sources × daily) | ~$0.10 |
| Domain | ~$1 |
| **Total** | **~$5/mo** |

### Secrets / env (Vercel project settings + GH Actions secrets)

- `ANTHROPIC_API_KEY`
- `RESEND_API_KEY`
- `KV_REST_API_URL`, `KV_REST_API_TOKEN` (Vercel KV)
- `ALERT_EMAILS` (comma-separated internal addresses)
- `GITHUB_TOKEN` (auto-provided in Actions)
- `SITE_URL` (e.g. `https://tracker.example.com`)

### Monitoring

- GitHub Actions run history is the primary log.
- `data/health.json` rendered in site footer: "Last check: Xh ago" — publicly visible system pulse.
- Failure alerts via GH Actions native email on workflow failure.

---

## 10. v1 Scope

### In v1 (MVP launch)

- 28-source `sources.yaml` populated with verified URLs.
- Fetchers for 4 types: `html_page`, `rss_feed`, `github_repo`, `ietf_draft`.
- `pipeline/check.py` with full diff → analyzer → event → SoP flow.
- Per-pillar LLM behavior (crawler thin, news full).
- Homepage (hero + feed + State of Play sidebar).
- `/events/[slug]` and `/sources/[slug]` (basic list, no diff viewer).
- `/about`, `/subscribe`, `/feed.xml`.
- RSS full-text.
- Crawler alert email to `ALERT_EMAILS`.
- Weekly digest + subscription flow with double opt-in.
- LLM disclosure on every event page and `/about`.

### Deferred to v1.1+

- Snapshot side-by-side diff viewer.
- `/archive` standalone page (v1 relies on homepage filter + "Load more").
- Search.
- Slack / webhook distribution.
- Admin UI (all v1 config changes go through PR on `sources.yaml`).
- Per-user email preferences.
- Historical backfill beyond "day of v1 launch" (v1 starts the timeline; prior state is lost unless seeded manually).

---

## 11. Open decisions (deferred to implementation)

- Final URLs for pillar-2 and pillar-3 seed sources — each needs RSS-availability verification during implementation (fall back to `html_page` on listings page if no feed, or substitute a similar source).
- Exact spec-repo choices for pillar 3 item 22 (core Web Bot Auth spec repo — verify current canonical home).
- Exact LLM prompts (iterated in implementation with real diffs).
- Final typography and color palette (frontend-design skill at build time).
- Domain name.

None of these block the implementation plan — they are config-level decisions that can be finalized as the relevant module is built.

---

## 12. Out of scope

- User accounts, comments, social features.
- Mobile app.
- Multi-language (English only for v1).
- Historical archive import (site starts fresh at launch).
- Community contributions to sources list (maintainer-only via PR).
- Paid tier / monetization.
