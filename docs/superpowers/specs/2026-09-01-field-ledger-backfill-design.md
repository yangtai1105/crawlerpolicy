# Field Ledger and Direct-Evidence Backfill Design

**Date:** 2026-09-01  
**Status:** Approved direction; awaiting written-spec review  
**Product:** [crawlerpolicy.com](https://crawlerpolicy.com)

## Purpose

Crawler Policy will replace the dark Signal Prism interface with the selected **Field Ledger** direction and seed the publication with useful recent history. The backfill will transform only evidence already collected from configured direct sources during the last three months. It will not use the legacy Gemini Search corpus, invent current news, or weaken the publication rules used by future daily runs.

The result must give a first-time reader enough material to understand the ecosystem immediately while preserving the distinction between an item's original publication date and the date it was processed into the new feed.

## Scope and Fixed Decisions

- Backfill evidence whose underlying `published_at`, falling back to `detected_at`, is on or after `2026-06-01T00:00:00Z` and not in the future at execution time.
- Reuse the immutable records already stored in `content/evidence/`; do not crawl historical websites or search for missing history.
- Exclude every source whose configured type is `gemini_search`, including records captured before those sources were disabled.
- Exclude legacy schema-v1 event prose as an analysis input. Legacy pages remain unchanged in the Legacy Archive.
- Re-run relevance and four-layer analysis with the configured Gemini structured-model provider.
- Preserve the original evidence timestamp as the public `event_date` and `published_at`.
- Mark generated feed records with `backfilled: true`, a processing timestamp, and a stable backfill batch identifier.
- Continue deriving `verified`, `reported`, and `signal` from source tier. The model cannot elevate status.
- Keep the normal daily publication cutoff at `2026-08-30T00:00:00Z`. The historical exception exists only inside an explicit backfill command.
- Apply the selected Field Ledger visual direction to the full public site, with the home feed and story page receiving the most substantial changes.

## Backfill Architecture

### One-time command

Add this explicit command:

```bash
uv run python -m pipeline.backfill_feed \
  --since 2026-06-01T00:00:00Z \
  --until 2026-09-01T23:59:59Z \
  --direct-only \
  --limit 15
```

The command is intentionally separate from `pipeline.check`. Daily Check must not silently begin replaying older records if configuration changes or a new machine runs the project.

The command loads the normal configuration and source registry, requires `GEMINI_API_KEY`, and uses `GEMINI_ANALYSIS_MODEL`. `--until` defaults to the current UTC time. `--limit` bounds the number of previously unfinished eligible records attempted in one run; the deterministic processing order is newest evidence first, then evidence ID.

A dedicated manually dispatched `backfill-feed.yml` workflow exposes `since`, `until`, and `limit`, runs one bounded batch, and commits its feed files and manifest to `main`. The operator repeats the workflow until the summary reports zero unfinished eligible records. A default limit of 15 keeps every commit recoverable and every run inside the GitHub Actions timeout.

### Eligibility

An evidence record is eligible when all of the following are true:

1. Its source exists in `sources.yaml`.
2. The source type is not `gemini_search`.
3. Its underlying publication timestamp is within the requested inclusive window.
4. It contains a source URL and enough content to classify.
5. It does not already map to an existing feed record with the same evidence ID.

The command may process evidence in the existing `skipped_cutoff`, `analyzed`, or `failed_analysis` stages. It does not depend on the old stage because records analyzed by the former pipeline do not contain the new four-layer output. Backfill progress therefore needs its own append-safe manifest rather than overloading operational evidence stage.

### Processing flow

```text
content/evidence records
  → join configured source metadata
  → direct-source and date-window filter
  → deduplicate by evidence ID
  → Gemini structured relevance
  → Gemini four-layer analysis
  → deterministic publication status
  → content/feed record marked backfilled
  → optional verified material development
  → append result to backfill manifest
```

Relevance is evaluated before the more expensive editorial analysis. Ordinary model availability failures use the existing provider-failure classification and circuit breaker. Authentication, billing, or quota failures stop the batch promptly. The manifest is written after every attempted item. The bounded workflow then commits that checkpoint; a later invocation resumes from the manifest and existing feed evidence IDs.

### Manifest and idempotency

Store a machine-readable manifest under `data/backfills/`. The batch ID is deterministically derived as `direct-evidence_<since-date>_<until-date>`; the approved production batch is `direct-evidence_2026-06-01_2026-09-01`. Each evidence ID receives one outcome:

- `published`
- `irrelevant`
- `duplicate`
- `failed`
- `excluded_source`
- `outside_window`

Published feed files remain the primary idempotency boundary: if any existing feed record already contains the evidence ID, the command skips it even if the manifest is missing. The manifest adds resumability, auditability, counts, and error reporting; it must never be the only duplicate check.

Re-running the same batch must not change successful content unless an explicit future `--force` capability is designed. This release does not add `--force`.

## Feed and Development Records

The feed frontmatter gains these optional fields:

- `backfilled: boolean`, default `false`
- `processed_at: datetime`, required when `backfilled` is true
- `backfill_batch: string`, required when `backfilled` is true

The body remains exactly:

1. Summary
2. Insight
3. Implication
4. Why it matters
5. Evidence

Backfilled feed items use the same deterministic status and promotion rules as live items. A primary or measurement source can produce a verified item; a specialist source produces a reported item. Only verified plus material backfilled items may create a schema-v2 development record. Feed and development records must share the same evidence IDs.

Historical development promotion is allowed because the date is preserved and clearly labeled. It enriches theme and trend source material, but the backfill operation must not automatically rewrite current trend status or regenerate past weekly issues. Trend changes remain a deliberate follow-up based on completed current logic.

## Field Ledger Visual System

### Palette

- **Field paper:** `#E8EEEA` — cool sage-gray page background.
- **Ledger ink:** `#192820` — primary reading text.
- **Forest block:** `#203A30` — lead story and high-authority surfaces.
- **Clay marker:** `#D16B50` — implications, active rules, and the lead block's offset edge.
- **Evidence mint:** `#7BB497` — verified status, source links, and evidence relationships.
- **Quiet rule:** `#AEBDB4` — dividers and low-priority structure.

Long-form reading never uses low-contrast text on luminous gradients. Body copy targets a comfortable 16–18 CSS pixels with a line height near 1.7 and a line length no wider than about 72 characters.

### Typography

Use the IBM Plex family to connect editorial reading with technical documentation:

- IBM Plex Sans Condensed or IBM Plex Sans for restrained display roles.
- IBM Plex Sans for navigation and body copy.
- IBM Plex Mono for timestamps, evidence IDs, status, and taxonomy.

Display typography remains bold enough to establish a voice but no longer dominates several screens of vertical space. The lead headline and Summary must both remain visible within a 1440×900 viewport.

### Layout and signature

The page signature is a single dark forest evidence block offset by a clay-colored edge, like a field note pinned onto a ledger. The rest of the page is flat, light, and ruled rather than glassy, glowing, or card-heavy.

The home hierarchy becomes:

1. compact masthead and current date;
2. split editorial thesis;
3. latest available lead item in the forest evidence block;
4. chronological ledger rows for the remaining feed;
5. theme index;
6. weekly-intelligence entry;
7. restrained method and health footer.

Each ledger row gives date and textual status their own narrow column, followed by headline, Summary, and the most useful analytical layer. Backfilled items display `Backfilled · Original publication date` in text. Status continues to use text and color together.

Story pages use the light field-paper background. Summary, Insight, Implication, and Why it matters are separated by quiet rules with generous reading space. Evidence appears in a forest-tinted terminal-like block at the end, but ordinary prose never uses that dark treatment.

### Responsive and accessible behavior

- At narrow widths, the split hero and ledger rows become one column.
- Date and status remain above the headline rather than disappearing.
- The forest lead block loses its lateral offset before it can cause overflow.
- The site must have no horizontal overflow at 320, 390, 768, or desktop widths.
- Focus outlines use the forest/mint system with sufficient contrast.
- Reduced-motion preferences remove nonessential transitions.
- Information conveyed by clay, mint, or forest always has a textual label.

## Site Behavior With Backfilled Content

The home page selects the newest eligible feed item by original `published_at`, preferring a high-importance verified item only within the latest publication window. It must not select a three-month-old high-importance item over a materially newer item merely because the older score is higher.

When the newest item is backfilled, the lead block states that clearly. The page date reflects the item's original publication date rather than the processing date. The site can therefore show useful recent history without claiming a false daily edition.

RSS includes backfilled items with their original dates and a visible `[Backfilled]` marker during the initial publication batch. Subsequent Daily Check items retain the current `[Verified]`, `[Reported]`, or `[Signal]` label. This allows feed readers to distinguish the one-time historical import.

## Failure and Cost Controls

- Relevance runs before analysis to reduce Gemini calls.
- A fatal provider failure opens the circuit and stops the batch.
- Each workflow invocation processes at most 15 previously unfinished records and commits that batch with its updated manifest.
- Failed evidence remains retryable and is recorded in the manifest with the error class.
- No content is deleted or overwritten by the backfill command.
- No old Gemini Search prose is sent through as authoritative evidence.
- No arbitrary URLs returned by a model are fetched.

The CLI reports eligible, attempted, remaining, irrelevant, published, duplicate, excluded, and failed counts. Production repeats bounded 15-record workflow runs until `remaining` is zero; a failed provider run stops the sequence for diagnosis rather than looping.

## Testing and Acceptance Criteria

### Backfill

- A direct-source evidence record inside the window is eligible.
- A `gemini_search` evidence record is excluded even if its source remains in the registry.
- Evidence before June 1 or after the supplied upper bound is excluded.
- `published_at` and `event_date` equal the original evidence date.
- Generated feed frontmatter includes `backfilled`, `processed_at`, and `backfill_batch`.
- A second run publishes zero duplicates.
- Existing feed records are detected by evidence ID even without a manifest.
- Reported items never create developments.
- Verified material items create linked feed and development records with identical evidence IDs.
- Authentication, quota, and billing failures stop subsequent model calls and leave a resumable manifest.

### Site

- Backfilled status is visible in the lead, ledger row, detail page, and RSS.
- All four editorial layers and evidence links remain readable.
- Original dates are shown; processing dates are never presented as event dates.
- The Field Ledger palette replaces Signal Prism across primary routes.
- The home page remains useful with one, many, or no feed items.
- Desktop and mobile browser QA confirms contrast, hierarchy, focus, and absence of overflow.

### Production

- Python lint and the full test suite pass.
- Astro content validation, type checking, integration tests, and production build pass.
- A dry-run reports the expected eligible and exclusion counts without writing feed records.
- Repeated bounded production workflows reduce `remaining` to zero or pause resumably on a provider failure without duplicate output.
- The resulting commit reaches `main`, Daily Check remains healthy, and the public home page exposes recent readable items.

## Non-Goals

- No arbitrary three-month web crawl.
- No use of legacy Gemini Search digests for publication.
- No rewriting or deleting the Legacy Archive.
- No regeneration of historical weekly issues.
- No automatic trend-status rewrite from backfilled evidence.
- No user accounts, personalization, or newsletter delivery.
