# Readable Ecosystem Feed Design

**Date:** 2026-08-30  
**Status:** Approved direction; awaiting written-spec review  
**Product:** [crawlerpolicy.com](https://crawlerpolicy.com)

## Purpose

Crawler Policy will become an English-language, feed-first intelligence publication about the relationship between AI systems and the open web. The primary audience is a technically and commercially literate reader who wants to understand crawler access, agent identity, content rights, regulation, and machine-traffic economics without reading every source directly.

The site must optimize first for reading. Evidence, pipeline health, and source coverage remain important, but they support the publication rather than define its main experience.

## Product Principles

1. Every published item must tell the reader what happened and why it matters.
2. Evidence is preserved before model analysis and remains the source of truth.
3. Source quality determines publication status; the model cannot promote its own output.
4. Daily signals and durable intelligence are different products and must remain visibly distinct.
5. A failed model run must delay updates, not erase the last successful publication.
6. The new publication starts on 2026-08-30 and does not backfill historical items.
7. English is the public editorial language.

## Information Architecture

### Primary navigation

- **Feed** (`/`): lead insight, latest ecosystem items, active themes, and a weekly-intelligence entry point.
- **Weekly** (`/intelligence`): completed weekly synthesis built only from verified developments.
- **Themes** (`/fronts/...`): the existing five fronts presented as reader-facing themes.
- **Sources** (`/sources`): source registry, coverage, and methodology.

### Secondary destinations

- **Developments** (`/developments`): only verified, material developments.
- **Story detail** (`/events/[slug]`): the complete four-layer analysis and evidence record for any feed item.
- **Archive** (`/archive`): legacy schema-v1 records only.
- **RSS** (`/feed.xml`): all public daily-feed items, not only verified developments.
- **About** (`/about`): methodology, evidence policy, model-assistance disclosure, and pipeline status.

Pipeline health moves out of the home-page hierarchy. The footer shows a compact status and links to detailed coverage. A degraded run may add a restrained “Updates delayed” notice without replacing the editorial content.

## Editorial Model

### Feed item fields

Every public feed item contains:

- `title`: a factual, specific headline.
- `summary`: two or three sentences describing what happened.
- `insight`: the new pattern, distinction, or mechanism exposed by the evidence.
- `implication`: the likely effect on actors, controls, markets, standards, or policy.
- `why_it_matters`: a concise statement of why the reader should care now.
- `status`: `verified`, `reported`, or `signal`.
- `confidence`: `high`, `medium`, or `low`.
- `primary_track` and `tracks`: the existing nine-track taxonomy.
- `source_tier`: inherited from the configured source.
- `source_urls`: one or more canonical source links.
- `evidence_ids`: immutable evidence records supporting the item.
- `observed_at`, `published_at`, and `event_date`.
- `change_kind`: `material`, `context`, or `watch`.
- `development_slug`: present only when a verified material item is promoted into the durable development record.

### Publication levels

#### Verified

Verified items require primary or measurement evidence, including official documentation, regulatory material, repository activity, company announcements, or approved measurement sources. A verified item may become a development when `change_kind` is `material`. Only verified developments may update trends or support weekly conclusions.

#### Reported

Reported items come from configured specialist, publisher, or reputable reporting sources. They are readable daily-feed content but cannot independently update trends or support a weekly conclusion. They may be promoted later when corroborated by primary evidence.

#### Signal

Signals are early observations from configured commentary or discovery sources. They appear with an explicit unverified label and never update trends. They are retained only when they contain a concrete, reader-relevant claim and at least one source URL.

Status is computed from source tier, evidence type, and corroboration rules. Gemini may recommend relevance, materiality, and confidence, but it cannot assign or elevate publication status outside those deterministic rules.

## Storage Boundaries

`content/feed/` becomes the canonical store for public daily-feed items. Feed records use their own schema version and contain the full editorial body. `content/events/` remains the durable verified-development record used by trends and weekly intelligence.

When a feed item qualifies as a verified material development:

1. The feed item is written once with its complete reader-facing analysis.
2. A development record is written to `content/events/` with the same evidence IDs and a link back to the feed item.
3. Trends and weekly intelligence continue to consume only the development record.

This deliberate separation avoids treating every reported story as durable evidence while preserving existing trend invariants.

## Daily Data Flow

```text
Configured sources
  → direct HTML / RSS / GitHub / IETF / optional browser rendering
  → normalize and diff
  → save immutable evidence
  → apply 2026-08-30 launch cutoff
  → Gemini 3.7 structured analysis
  → deterministic status and publication rules
  → write daily feed item
  → optionally promote to verified development
  → update trends and state of play from verified developments only
  → build Astro site and RSS
  → commit and deploy through GitHub/Vercel
```

The crawler does not use an LLM to fetch ordinary sources. Gemini receives already-fetched evidence and returns structured editorial analysis.

## Gemini-Only Analysis Layer

Anthropic is removed as a runtime requirement. One provider adapter owns all model calls so the pipeline does not import provider clients throughout its domain logic.

The first implementation uses:

- `GEMINI_API_KEY` for all analysis.
- `GEMINI_ANALYSIS_MODEL`, defaulting to `gemini-3.7-flash`.
- Gemini structured output with a JSON schema for relevance, feed analysis, state of play, and weekly synthesis.
- The existing `GITHUB_TOKEN` for GitHub REST access.
- Cloudflare Browser Rendering secrets only for explicitly configured browser-rendered sources.

Google Search grounding is not required for the core pipeline. Existing `gemini_search` sources must not be treated as primary evidence or used to discover URLs for automatic crawling. They remain disabled for public-feed publication until their retention and product-use constraints are reviewed. Broader daily coverage comes from the expanded configured source registry.

## Reading Experience

The selected visual direction is **Signal Prism**:

- deep violet base rather than the current fog-gray observatory palette;
- electric cyan, violet, and pink used as a controlled spectrum;
- high-contrast off-white reading text;
- translucent signal surfaces used selectively for the lead item;
- a spectral edge or rail encoding content status;
- Syne-style expressive display typography, a highly legible sans-serif body face, and mono utility labels;
- one memorable luminous moment around the lead insight, with the rest of the page kept quiet.

The selected content density is **Layered Feed**:

- the lead item exposes Summary and Why it matters on the home page;
- ordinary feed cards expose Summary and the single most useful analytical field;
- the detail page exposes Summary, Insight, Implication, Why it matters, and Evidence;
- cards remain scannable on active days;
- status is communicated by both text and color, never color alone.

The home page order is:

1. navigation and current publication date;
2. editorial thesis and lead insight;
3. latest feed items;
4. active themes;
5. current weekly-intelligence entry point;
6. compact method and health footer.

The design must support keyboard navigation, visible focus, reduced motion, high contrast, and responsive layouts down to 320 CSS pixels.

## Empty, Delayed, and Failed States

- The first successful fetch of a stable HTML source establishes a baseline and does not invent a change.
- If there are no new items today, the page shows the most recent successful feed and a clear “No new verified developments today” timestamp.
- If Gemini authentication, quota, or billing fails, a circuit breaker stops further model calls after the provider failure is classified.
- Evidence fetched before the failure remains pending and replayable.
- The home page continues serving the last successful feed and shows “Updates delayed” with the last successful publication time.
- A failed required source keeps health degraded or critical, but does not remove already published reader content.
- Weekly generation continues to refuse critical or stale evidence windows.

## Replay and Launch Cutoff

The publication cutoff is `2026-08-30T00:00:00Z`. Evidence with an underlying item publication date before this cutoff cannot become a new feed item. Evidence observed after the cutoff may be replayed without refetching when its underlying item is also on or after the cutoff.

Stable HTML baseline snapshots do not generate feed items. RSS and GitHub items must be filtered by their source publication timestamps before Gemini analysis. This prevents the first healthy run from publishing a backlog as if it were current.

## Testing and Acceptance Criteria

### Pipeline

- Provider-independent domain tests do not import Anthropic.
- Gemini structured responses are parsed into the feed schema and reject missing required fields.
- Provider billing, quota, and authentication errors open the circuit breaker and preserve pending evidence.
- Launch-cutoff tests prove pre-cutoff RSS and GitHub items are not published.
- Deterministic promotion tests prove reported and signal items cannot update trends.
- Verified material items create linked feed and development records with identical evidence IDs.
- Evidence replay produces no duplicate feed items.

### Site

- The home page renders the latest feed even when the current run is delayed.
- Feed cards display textual status, summary, and one analytical field.
- Detail pages display all four editorial sections and evidence links.
- `/developments` contains verified material items only.
- RSS contains all public feed levels with visible status labels.
- The Astro content schema rejects invalid status, confidence, or missing evidence.
- The full production build completes without warnings or broken internal links.
- Desktop and mobile screenshots are reviewed for hierarchy, contrast, overflow, and empty states.

### Success definition

A visitor can open the home page, understand the most important ecosystem development in under one minute, scan the rest of the day’s signals, distinguish verified facts from reporting and early signals, and open the underlying evidence without encountering pipeline-oriented jargon.

## Deliberate Non-Goals

- No historical feed backfill.
- No personalized recommendations or user accounts.
- No automated crawling of arbitrary URLs returned by a search-grounding tool.
- No newsletter-delivery implementation in this release.
- No replacement of GitHub/Vercel deployment with a custom CMS.
- No requirement to maintain Anthropic or OpenAI API credentials.
