# Agentic Map Layer — Design

Date: 2026-10-10
Status: approved for planning
Supersedes nothing. Extends `2026-08-29-web-intelligence-rearchitecture-design.md` and `2026-09-03-daily-x-intelligence-design.md`.

## 1. Why

Crawler Policy publishes a reliable daily and weekly intelligence flow. The flow answers *what happened*. It does not answer *where the field stands*, and it cannot answer *show me everything about agents* without enumerating a growing set of agent-shaped tracks.

Two changes drive this work:

1. **Scope.** The subject is no longer primarily crawlers. Agents, agent identity, agent protocols (Web Bot Auth, A2A, MCP, the agent-payment cluster), and the full set of defense players — not only Cloudflare — are now in scope.
2. **Shape.** Adding sources to a chronological feed makes the feed longer, not the publication better. The missing artifact is a persistent **map**: which players hold which positions on which protocols, kept with evidence, and read qualitatively.

The product becomes two legs on one evidence base: **intelligence** (the existing flow) and **the map** (new). Everything in the map is derived from the same evidence records the feed already produces.

## 2. Scope decisions

In scope:

- A second taxonomy axis so that any domain can be expressed for crawlers or for agents.
- Controlled entity registries for protocols and players.
- A position state per (player × protocol) with the project's existing evidence discipline.
- A qualitative reading layer attached to protocol columns and fronts.
- A proposal → pull request flow so no map state changes without human approval.
- New site pages for the map, rendered in the Editorial visual direction.
- Source expansion across defense players, agent protocols, identity/payments, monetization, and standards bodies.

Out of scope for this spec:

- Per-player qualitative readings (24+ prose blocks to maintain). The registry and page support it; the reading layer does not populate it yet.
- Any change to how the daily feed decides publication status, importance, or trend movement.
- Backfilling `subject` or entity links onto historical records.
- Notifications, alerting, and the reserved `ALERT_EMAILS` / `RESEND_API_KEY` values.

## 3. Taxonomy: two orthogonal axes

The current taxonomy conflates domain and subject. `crawler-controls` names a subject; `policy-regulation` names a domain. The consequence is that "the EU regulates agent payments" has no correct home, and every new agent-adjacent area demands a new track.

### 3.1 Domain axis — `tracks`, 9 → 10

Subject words are removed from track names.

| Track | Change |
|---|---|
| `policy-regulation` | unchanged |
| `litigation-legal` | unchanged |
| `search-discovery` | unchanged |
| `licensing-monetization` | unchanged |
| `standards-protocols` | unchanged |
| `asset-rights` | unchanged |
| `measurement-economics` | unchanged |
| `access-controls` | renamed from `crawler-controls` |
| `platform-ecosystem` | renamed from `agentic-web` |
| `identity-authorization` | **new** — identity, authentication, delegated authority, agent payment credentials |

`standards-protocols` continues to track a protocol's own progress (draft to RFC). Who adopted it is position state, not a track.

### 3.2 Subject axis — `subject`, new field

Values: `crawler` | `agent` | `both` | `unknown`.

Composition replaces proliferation:

- agent regulation → `policy-regulation` × `agent`
- crawler blocking → `access-controls` × `crawler`
- agent payment credentials → `identity-authorization` × `agent`
- a future agent lawsuit → `litigation-legal` × `agent`, with no new track

### 3.3 Fronts

The five fronts are unchanged: `access-discovery`, `agents-identity`, `rights-markets`, `governance-law`, `measurement-economics`. They roll up the domain axis. `identity-authorization` rolls up to `agents-identity`.

### 3.4 Compatibility

- An alias map holds `crawler-controls` → `access-controls` and `agentic-web` → `platform-ecosystem`. Loaders resolve aliases; existing records, legacy archive material, and existing URLs keep working. Old track URLs redirect to the new slug.
- `subject` is additive. Records written before this change carry `unknown` and are not backfilled, consistent with the existing rule against backfilling history for newly added coverage.
- The feed's existing `primary_track` semantics are unchanged.

## 4. Entity registries

Two human-maintained YAML registries become the project's controlled vocabulary. They sit beside `sources.yaml`, follow its editing discipline, and are reviewed like it.

```
entities/protocols.yaml
entities/players.yaml
```

### 4.1 `protocols.yaml`

Per protocol: `slug`, `display_name`, `kind` (`identity` | `access` | `payments` | `provenance` | `licensing` | `transport`), `steward` (standards body or vendor), `spec_url`, `spec_status` (`draft` | `wg-draft` | `standards-track` | `rfc` | `stable` | `deprecated`), `front`, `first_observed`, optional `supersedes` / `related`.

`spec_status` describes the protocol itself and is distinct from any player's position on it.

### 4.2 `players.yaml`

Per player: `slug`, `display_name`, `category`, `short_descriptor` (the one line shown under the name in the matrix first column), `bots` (user-agent tokens operated, where applicable), `home_url`, optional `aliases` for name matching.

Categories: `defense-infra`, `agent-operator`, `identity-payments`, `monetization`, `standards-body`, `publisher`.

### 4.3 Connecting to what already exists

The feed schema already extracts `actors` as free text. That becomes the anchor:

- `actors` is promoted to **controlled extraction**: the analysis step may only emit player slugs present in `players.yaml`.
- A new `protocols` field is extracted the same way, constrained to `protocols.yaml`.
- The free-text `actors` values are preserved in a new `actors_raw` field so nothing observed is lost.
- When analysis believes it has seen an entity outside the registry, it appends a candidate to `data/entity-candidates.json` with the evidence that suggested it. **This queue is the only path by which the registries grow.** The pipeline never writes to the registries.

## 5. Position state — the matrix

`data/positions.json`. One record per (player, protocol) that has ever held a non-default position. **An absent record means `none` and is not stored**, so the file grows with observed positions rather than with the size of the grid; the matrix renders `none` for any pair it does not find.

```
player_slug, protocol_slug
status: shipped | preview | stated | declined | none
since                      # when this status took effect in the world
previous_status
last_changed_at            # when this record last changed
evidence_level: primary | secondary   # strongest evidence behind this record
source_urls[]
supporting_development_slugs[]
proposed_by                # pipeline run id
merged_at                  # set by the human merge, never by the pipeline
note                       # optional one line, e.g. a deliberate strategic position
```

`declined` carries real intelligence value and is a first-class status: a player publicly rejecting or declining to implement a protocol is a signal, not an absence. A player with no public position is `none`; the distinction between `none` and `declined` must never be inferred by the model — `declined` requires an explicit public statement in a primary source.

### 5.1 Invariants

- A status change requires at least one `verified` development backed by a primary or official source, so **every published change carries `evidence_level: primary`**. `secondary` appears only on corroborating entries attached to a record whose change was already established by primary evidence; it can never be the sole basis for a status. This mirrors the existing rule that `gemini_search` and X-only items cannot independently advance a trend.
- `signal`-grade and `reported`-grade evidence can never move a position. They remain readable in the feed.
- The pipeline never writes `positions.json`. Only a merged pull request does.
- "Changes this week" is derived: records whose `last_changed_at` falls inside the last seven days. No separate counter is stored.

## 6. Reading layer — the qualitative read

The map's weakness without this layer is that coloured cells state facts and answer nothing. Readings attach an editorial judgment to each axis of the map.

```
data/readings/protocol-<slug>.json
data/readings/front-<slug>.json
```

Per reading: `stance` (one sentence of judgment), three fixed angles, provenance.

| Angle | What it answers |
|---|---|
| `adoption_shape` | What the pattern of positions actually means — who moved, who did not, and why that grouping matters |
| `new_entrants` | Who has arrived in this area recently and what they are trying to control |
| `watch_for` | The specific thing whose presence or absence in the next months would change the read |

The angles are fixed deliberately. Free-form commentary is hard to generate consistently and harder to keep honest; fixed angles give the pipeline a stable target and give the reader a stable shape.

Provenance per reading: `built_from` (development slugs), `generated_at`, `merged_at`, `development_count`.

**Cadence: weekly**, aligned with Weekly Intelligence. Daily regeneration would produce prose churn and pull-request noise without adding information.

Front pages additionally surface the existing `data/insight-threads.json` as "threads in motion", read directly rather than copied. Threads already carry `thesis`, `direction`, `confidence`, and `related_feed_slugs` — the shape the front page needs.

Readings go through the same pull request gate as positions. A wrong cell is a factual error and visible; a wrong reading is a judgment error and damages credibility.

## 7. Pipeline: propose, then merge

A new stage runs after the feed write and never mutates published map state.

```
pipeline/map_proposals.py            # writes proposals/ only
pipeline/readings.py                 # weekly; writes proposals/ only
.github/workflows/map-proposals.yml  # turns proposals into one pull request
```

Flow:

1. `map_proposals.py` reads the day's `verified` developments with their entity links, compares implied positions against merged state, and writes `proposals/<date>-<n>.json` describing each candidate change: entity pair, from-status, to-status, evidence level, source URLs, originating development.
2. The workflow maintains a single long-lived branch `map/proposals` and one open pull request. New proposals update that branch rather than opening a pull request per change.
3. The pull request body renders each change as `Akamai × AIPREF: none → stated`, with effective date, evidence links, and the development that triggered it.
4. Merging applies the change. `merged_at` is set by the merge.

### 7.1 Hard constraints

- **The daily feed is unaffected.** A proposal-stage failure records `degraded` in stage-aware health and never blocks publication. Required coverage for the feed does not include map proposals.
- **The site reads merged state only.** An unmerged pull request means the map continues to show the last approved state. Nothing reaches the map without passing human review.
- **No silent registry growth.** Entity candidates queue for review; the pipeline cannot add a protocol or player.

## 8. Site structure

Information architecture: dual-entry homepage. The map and the flow both sit on the landing page.

| Route | Content |
|---|---|
| `/` | Persistent field-state band (matrix excerpt plus this week's changes), then the Daily Brief, with protocols-in-motion and developing insights alongside |
| `/matrix` | Full position grid, banded by player category, bands collapsible, first column sticky, cells open an evidence popover, category filter, "changes only" toggle |
| `/protocols` | Protocol index |
| `/protocols/{slug}` | Status buckets (shipped / preview / stated / declined), dossier sidebar, status-change history, the protocol reading |
| `/players` | Player index, grouped by category |
| `/players/{slug}` | Mirror of the protocol page: this player's positions across protocols, plus its change history |
| `/fronts/{front}` | Existing route, extended with the front reading, a field summary, the largest gap, and threads in motion |

Existing routes (`/intelligence`, `/developments`, `/sources`, `/events/{slug}`, `/archive`, legacy `/reading`) are unchanged.

### 8.1 Matrix behaviour

- Default state: first three bands expanded, remaining bands collapsed.
- Clicking a column header opens the protocol reading drawer; clicking a band header opens the category read (reusing the front-reading shape).
- Clicking a cell opens the evidence popover: current status, effective date, previous status, evidence level, source link, originating development.
- Below 900px the grid degrades to the protocol-page status-bucket layout rather than horizontal scrolling. The grid is never horizontally scrollable; the band and bucket layouts are the only two forms.

### 8.2 Visual direction

**Editorial.** Warm off-white ground, serif display type for headlines and stances, IBM Plex Sans for body and data, a single restrained accent for change markers and links.

Two concessions make Editorial carry dense data, both validated in mockup:

- Status cells are rounded capsules, not hard squares.
- The matrix first column carries a `short_descriptor` line under each player name to hold the density.

The existing Field Ledger tokens in `site/src/styles/global.css` are replaced by an Editorial token set. Status colour must stay distinguishable without relying on hue alone; the five statuses differ in lightness as well as hue, and the change marker is an outline rather than a colour swap.

## 9. Initial roster

Verified by web research on 2026-10-10. Positions below are starting points for the registries, **not** seeded position state: every cell in `positions.json` must be established by the normal evidence path before it is published.

### 9.1 Protocols

| Slug | Kind | Steward | Spec status (Oct 2026) |
|---|---|---|---|
| `web-bot-auth` | identity | IETF `webbotauth` WG | Standards Track; adopted as WG document 2026-09-01; `Signature-Agent` mandatory on signed requests |
| `a2a` | transport | Linux Foundation (Agentic AI Foundation) | v1.0; 150+ supporting organisations |
| `mcp` | transport | Anthropic / open spec | established |
| `ap2` | payments | Google plus partners | launched 2025-09; 60+ partners; SD-JWT Checkout and Payment Mandates |
| `acp` | payments | OpenAI and Stripe | live in ChatGPT since 2025-09 |
| `x402` | payments | open | emerging |
| `aipref-vocab` | access | IETF `aipref` WG | WG draft, Proposed Standard track; `train-ai` and `search` categories |
| `aipref-attach` | access | IETF `aipref` WG | WG draft; updates RFC 9309 |
| `rsl` | licensing | RSL Collective | launched 2025-09-10 |
| `tdmrep` | licensing | W3C | published |
| `c2pa` | provenance | C2PA | published |
| `robots-txt` | access | IETF RFC 9309 | RFC |

The payment cluster also contains `tap`, which is deferred from the registry until a tracked player holds a public position on it. Tracking AP2 and ACP separately matters because they are different layers, not competitors — ACP handles checkout, AP2 handles payment consent — and a player can hold positions on both.

### 9.2 Players

**`defense-infra`** — Cloudflare, Akamai, Fastly, DataDome, HUMAN Security, Imperva, F5, Vercel, Stytch (verifier role), Amazon/AWS.
Notable: DataDome ships Agent Trust and supports Web Bot Auth; HUMAN ships AgenticTrust; Akamai's public position is to keep agent traffic in the same detection pipeline rather than ship an agent-only product — a deliberate stance that the reading layer should capture rather than render as a gap.

**`agent-operator`** — OpenAI, Google, Anthropic, Microsoft, Perplexity, Amazon (Bedrock AgentCore), Meta.
Confirmed Web Bot Auth signature producers: Google, OpenAI, Amazon Bedrock AgentCore. Anthropic is **not** confirmed as a producer and must not be entered as one without a primary source.

**`identity-payments`** — Visa, Mastercard, American Express, PayPal, Stripe, Coinbase, Okta, Skyfire, WorkOS, Auth0, Microsoft Entra, CyberArk, Permit.io, Clerk.
Okta Agent SSO is generally available since 2026-05; Skyfire pairs a Know Your Agent credential with an agentic wallet.

**`monetization`** — TollBit, ProRata, RSL Collective, Scalepost, Human Native.

**`standards-body`** — IETF (`webbotauth`, `aipref`), W3C, Linux Foundation / Agentic AI Foundation, C2PA, NIST.
NIST launched an autonomous-agent standards initiative in 2026-02 covering agent identity and authentication, action logging and auditability, and containment boundaries — all three map onto existing fronts.

**`publisher`** — Reddit, Yahoo, Ziff Davis, People Inc., Internet Brands, Quora, O'Reilly Media, Medium, Vox Media, BuzzFeed, USA Today Co., Arena Group, News/Media Alliance.

### 9.3 Source expansion

New `sources.yaml` entries, each assigned tier, role, domain track, and subject:

- **Defense:** Akamai blog and bot-manager docs, Fastly blog, HUMAN Security research, Imperva/Thales blog, F5 Labs, Vercel changelog (BotID), AWS security blog. DataDome and Cloudflare already covered.
- **Agent protocols:** IETF `webbotauth` and `aipref` datatracker pages, A2A and AP2 repositories, MCP spec repository (covered), ACP specification, Linux Foundation / Agentic AI Foundation announcements.
- **Identity and payments:** Okta newsroom, Stytch changelog, Skyfire, Visa and Mastercard agent-commerce newsrooms, Stripe changelog.
- **Monetization:** TollBit, ProRata, RSL Collective, Scalepost.
- **Governance:** NIST agent-standards initiative, EU AI Office guidance (EU AI Act provisions apply from 2026-08-02), existing UK CMA / FTC / EU Commission sources retained.

Fetch-mode discipline is unchanged: ordinary HTML, RSS, GitHub, and IETF sources are fetched without a model; `cf_browser_run` only where ordinary fetching cannot recover content; the first successful fetch of a stable HTML source establishes a baseline instead of inventing a change; no history backfill for newly added canonical sources.

## 10. Health and failure behaviour

- Map proposals and readings are **non-required** stages. Their failure yields `degraded`, never `critical`.
- Weekly Intelligence continues to refuse publication from critical or stale health. Readings follow the same refusal.
- The matrix and entity pages always render from merged state; if a reading is missing, the page renders the map without it rather than blocking.
- The footer timestamp continues to mean the last fully successful run and must never imply a failed attempt succeeded.

## 11. Testing

- Taxonomy: alias resolution for both renamed tracks; front roll-up for the new track; `subject` defaults to `unknown` on records lacking it; legacy track URLs redirect.
- Entity extraction: slugs outside the registries never enter `actors`/`protocols`; candidates land in the queue; `actors_raw` preserves observed names.
- Position invariants: a `signal` or `reported` development cannot change a status; `declined` requires an explicit primary source; the pipeline never writes `positions.json`.
- Proposals: a proposal with insufficient evidence is rejected before it reaches the branch; re-running a day does not duplicate proposals; proposal-stage failure leaves feed publication successful and health `degraded`.
- Readings: `built_from` references resolve to real developments; a reading whose window has no verified developments is skipped rather than invented.
- Site: `npm run check` and `npm run build` pass; matrix degrades to bucket layout below the breakpoint; status capsules remain distinguishable in a greyscale render.

## 12. Build order

Three sub-projects, each with its own plan and merge:

1. **Taxonomy and entities** — the two axes, alias map, registries, controlled extraction, the candidate queue.
2. **Positions and proposals** — `positions.json`, invariants, the proposal stage, the pull request workflow, readings.
3. **Site** — Editorial token set, matrix page, protocol and player pages, front page extensions, homepage dual entry.

Order matters: the site renders content that must exist first. Source expansion lands incrementally with sub-project 1 and continues through 2.

## 13. Resolved decisions

| Decision | Resolution |
|---|---|
| Site positioning | Intelligence plus map, both first-class |
| Audience | Industry practitioners |
| Player categories tracked | Defense, agent operators, identity/payments, monetization, standards bodies, publishers |
| Who writes map state | Pipeline proposes, human merges — for positions and readings alike |
| Homepage | Dual entry: persistent field-state band above the daily flow |
| Matrix rendering | Banded grid, collapsible, sticky first column, cell evidence popover; bucket layout on protocol pages and small screens |
| Visual direction | Editorial |
| Reading attachment points | Protocol columns and fronts; per-player readings deferred |
| Reading cadence | Weekly |
| Taxonomy | Two axes: domain track (10) plus subject (`crawler`/`agent`/`both`/`unknown`) |

---

## Known gaps carried forward from sub-project 1

Sub-project 1 (taxonomy and entities) landed on 2026-10-10. Its final whole-branch
review surfaced these gaps, which were deliberately deferred rather than discovered
later. Read this before starting sub-project 2 or 3.

### For sub-project 2 (positions and proposals)

- **Development records carry no entity links.** `pipeline/event_writer.py` emits
  `actors` only — no `subject`, `players`, or `protocols` — and the `events`
  collection schema declares none of them. §7 step 1 assumes `map_proposals.py`
  reads "the day's verified developments with their entity links". Either add the
  three fields to `event_writer` and the `events` schema, or join back through
  `content/feed` on `development_slug`. Decide which **before** building
  `map_proposals.py`; the join direction shapes that module.
- **The candidate queue has no dismissal state.** A candidate a human reviews and
  rejects re-queues forever and keeps incrementing `occurrences`. This spec does not
  define one. Add a dismissed/ignored state when the queue gets a review workflow.

### For sub-project 3 (site)

- **`Player.category` is single-valued and cannot express the roster this spec
  describes.** §9.2 lists Amazon under both `defense-infra` and `agent-operator`, and
  the matrix bands by category (§8.1), so a dual-role player lands in one band only.
  Decide the representation — a second category, or `roles: list[PlayerCategory]` —
  **before** building the banding.
- **The shipped registry is a subset.** `entities/players.yaml` holds 30 of the ~54
  players §9.2 enumerates. Missing: Amex, PayPal, Coinbase, WorkOS, Auth0, Microsoft
  Entra, CyberArk, Permit.io, Clerk, Scalepost, Human Native, C2PA as a standards
  body, and 11 of the 13 publishers. Omitted players resolve to `None` and flow into
  the candidate queue indefinitely instead of into `players[]`.
- **Stytch is categorised against this spec.** §9.2 lists it under `defense-infra`
  (verifier role); it ships as `identity-payments`.
- **`SUBJECT_LABELS` in `site/src/lib/taxonomy.ts` is currently dead code**, and no
  page reads the `subject` field the feed schema validates. Rendering the axis is
  sub-project 3's work.

### For the deferred source-expansion plan (§9.3)

- **Both new axes ship unexercised in production.** No source declares
  `default_subject`, so `subject` resolves to `unknown` on every record; and no source
  monitors 24 of the 30 registry players, so most registry rows can never be
  populated. The per-source subject fallback is correct but currently unobservable.
  Landing a first batch of `default_subject` declarations is the cheapest way to make
  the axis real.

### Archived content that intentionally still shows old slugs

- Three weekly issues (`2026-W35`, `W38`, `W39`) contain a raw track slug inside
  generated watchlist prose — "What primary evidence would make `crawler-controls`
  materially change?" — because the generator interpolated `track.value` before
  2026-10-10. The generator now uses a human-readable label; the frozen issues were
  deliberately left alone under the never-rewrite rule. Rendered track *attributes*
  and *link paths* across the built site contain zero legacy slugs; this prose is the
  one remaining visible occurrence.
