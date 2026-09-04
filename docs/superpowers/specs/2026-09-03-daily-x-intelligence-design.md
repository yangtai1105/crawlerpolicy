# Daily X Intelligence Design

**Date:** 2026-09-03  
**Status:** Approved direction; awaiting written-spec review  
**Product:** [crawlerpolicy.com](https://crawlerpolicy.com)

## Purpose

Crawler Policy will publish a fresh, highly selective English-language Daily Brief while preserving its evidence-first weekly intelligence system. The daily product should surface the few developments that materially change how AI systems access, discover, license, authenticate against, or economically interact with the open web.

The system adds xAI X Search as a real-time discovery layer. Gemini remains the editorial analysis layer. X does not replace first-party evidence, configured feeds, standards sources, regulatory sources, or measurement sources.

## Product Contract

1. The home page presents a dated Daily Brief every day.
2. A normal edition targets one to five consequential items; it never fills a quota with generic AI news.
3. Every item includes Summary, Insight, Implication, and Why it matters.
4. Readers can distinguish verified evidence, trusted reporting, and early X signals.
5. Daily developments attach to persistent insight threads so readers can see what is changing over time.
6. Weekly Intelligence synthesizes durable verified change; it is not the site's freshness layer.
7. A quiet day is described honestly. The system may publish fewer items or a short “no material change” note instead of manufacturing news.

## Editorial Scope

Included developments must affect at least one existing canonical track:

- policy and regulation;
- litigation and legal precedent;
- search and AI discovery;
- crawlers and content controls;
- agentic web and agent traffic;
- licensing and monetization;
- standards and protocols;
- content and asset rights;
- measurement and ecosystem economics.

General model launches, funding announcements, benchmarks, consumer AI features, and opinion-only commentary are excluded unless they materially change one of these tracks.

## Source Hierarchy

### Primary and measurement evidence

The current configured sources remain authoritative: company documentation and announcements, standards bodies, repositories, regulators, legal-primary material, transparent datasets, and measurement products.

### Trusted industry reporting

The source registry gains an explicit allowlist of publications and specialist reporters selected for original reporting, named sourcing, subject expertise, and correction practices. Candidate publications may include technology, publishing, search, advertising, standards, and internet-infrastructure outlets. Inclusion is configured, reviewable, and revocable; popularity alone does not qualify a source.

Trusted reporting may publish as `reported`. It cannot independently change a durable trend or support a Weekly Intelligence conclusion unless corroborated by primary or measurement evidence.

### X discovery

X is a real-time lead source. Searches prioritize:

- allowlisted official company, regulator, standards-body, and project accounts;
- allowlisted standards authors, maintainers, researchers, reporters, and industry practitioners;
- narrowly scoped semantic searches for each public front;
- the previous 24–36 hours only.

An X-only item normally publishes as `signal`. A post linking to an approved first-party or trusted-reporting source is resolved to that canonical source before publication, and the canonical source determines its status. X-only material never updates trends or Weekly Intelligence.

The site stores and displays attribution, author handle, post URL, and publication time. It does not republish full posts or large collections of X content.

## Recommended Technical Architecture

The production pipeline calls the xAI Responses API with the server-side `x_search` tool directly. Grok CLI is reserved for local editorial experiments and prompt development; it is not a production dependency.

Reasons:

- the API provides explicit date and account filters;
- requests and responses are observable and testable;
- successful server-side tool usage can be metered;
- GitHub Actions can authenticate non-interactively with one secret;
- the pipeline avoids a second agent shell with filesystem and command permissions;
- structured candidate records can be validated before any publication step.

New environment variables:

- `XAI_API_KEY`: required only for the optional X discovery lane;
- `XAI_DISCOVERY_MODEL`: defaults to the selected supported Grok model;
- `XAI_MAX_DAILY_SEARCH_CALLS`: defaults to `6`;
- `XAI_MONTHLY_SOFT_BUDGET_USD`: defaults to `10`.

Missing or exhausted xAI credentials degrade the discovery lane but do not make the direct-source daily pipeline critical.

## Daily Data Flow

```text
Configured direct sources and trusted feeds
  → fetch and preserve evidence

xAI X Search
  → search allowlisted accounts and narrow ecosystem topics
  → validate structured discovery candidates
  → deduplicate posts, stories, actors, and linked URLs
  → resolve only approved first-party or trusted-reporting links
  → preserve candidate metadata and any fetched canonical evidence

Combined candidate set
  → deterministic source-status assignment
  → Gemini relevance and importance scoring
  → Gemini English editorial analysis
  → select one to five highest-value items
  → publish dated Daily Brief
  → attach items to persistent insight threads
  → promote only verified material items into developments and trends
```

The xAI response is never written directly to the public site. It is an input candidate set that must pass schema validation, scope checks, source-policy checks, deduplication, and Gemini editorial analysis.

## Discovery Queries

The discovery layer runs a small fixed query set rather than an unconstrained “AI news” search:

1. Access and discovery: crawler policies, robots directives, AI search visibility, citations, referrals, and indexing.
2. Agents and identity: agent traffic, Web Bot Auth, authentication, delegation, MCP, and protocol releases.
3. Rights and markets: content licensing, training rights, pay-per-crawl/use, publisher deals, and asset-level controls.
4. Governance and law: regulator action, litigation, competition remedies, copyright, and disclosure requirements.
5. Measurement and economics: crawler volumes, referral ratios, bot identity observations, publisher traffic, and revenue effects.

Queries use `from_date`, `to_date`, and rotating `allowed_x_handles` groups of no more than the provider limit. Broad semantic discovery is run separately from official-account sweeps so provenance remains visible.

## Candidate Schema

Each X discovery candidate contains:

- stable candidate ID;
- discovery query and run timestamp;
- post URL and post ID;
- author handle and configured author class;
- post publication time;
- short model-generated factual synopsis;
- linked canonical URLs, when present;
- proposed tracks and actors;
- provider citations;
- raw provider usage metadata;
- lifecycle state: `discovered`, `resolved`, `rejected`, `analyzed`, or `published`;
- rejection reason when excluded.

Candidate metadata is stored separately from immutable publication evidence. Re-running the same date window is idempotent.

## Deterministic Quality Gates

A candidate is rejected before editorial analysis when any of the following applies:

- it is outside the nine-track scope;
- it is generic AI product news without web-ecosystem consequences;
- the account or linked domain violates the allowlist policy;
- it is a repost, duplicate, reaction-only post, engagement bait, or unsupported prediction;
- its claim cannot be stated proportionally from the retained evidence;
- its publication time cannot be established;
- it duplicates a direct-source item already in the edition.

After Gemini analysis, publication requires a material or concrete contextual development and a minimum configured importance score. The Daily Brief is sorted by consequence, not engagement or posting velocity.

## Daily Brief

The home page becomes explicitly date-led:

- `Today’s Brief — September 3, 2026`;
- one lead development when warranted;
- up to four additional high-value items;
- visible `Verified`, `Reported`, or `Signal` labels;
- source name, event time, and canonical source link;
- concise Summary and Why it matters on the feed;
- full Summary, Insight, Implication, Why it matters, and Evidence on the detail page.

The latest completed edition remains readable while the next run is in progress or degraded. Edition dates are publication dates; source event dates remain separate.

## Persistent Insight Threads

Daily items attach to stable threads such as crawler identity, publisher compensation, AI search referral economics, machine-readable rights, or agent authorization. A thread stores:

- a stable key and reader-facing title;
- current thesis and direction;
- confidence;
- first observed and last updated dates;
- supporting verified development IDs;
- related reported and signal feed IDs;
- a concise “what changed” delta;
- open questions to watch.

Signals and reporting may appear as related context but cannot change a thread's direction or confidence without verified evidence. Weekly Intelligence summarizes only evidence-backed thread changes.

## Cost and Operational Controls

At current published pricing, X Search tool invocations and model tokens are both billable. The implementation therefore:

- caps daily search calls at six by default;
- caps agent turns so one prompt cannot fan out indefinitely;
- records successful search invocation counts and estimated cost per run;
- skips lower-priority searches after the daily cap;
- emits a warning near the monthly soft budget;
- disables X discovery for the remainder of the run if the hard call cap is reached;
- never blocks direct-source publication because of an xAI failure.

The expected initial operating cost is single-digit US dollars per month, with a default soft budget of $10.

## Failure and Replay Semantics

- xAI authentication, quota, billing, timeout, or schema failures are classified separately.
- Valid candidates already returned are saved before later analysis stages.
- Failed candidates remain replayable without repeating X Search when possible.
- A failed X lane marks pipeline health `degraded`, not `critical`, unless it later becomes a required coverage source by explicit configuration.
- Gemini failure preserves X candidates as pending and publishes no incomplete prose.
- Replays cannot duplicate feed items, editions, or insight evidence.

## Security and Policy Constraints

- Only the official xAI/X interfaces are used; no browser automation or scraping of X.
- Secrets exist only in environment variables and GitHub Secrets.
- Only HTTPS URLs on configured host allowlists may be resolved from discovery output.
- Redirects to unapproved hosts are rejected.
- X content is attributed and linked rather than reproduced wholesale.
- Stored discovery metadata is limited to what is necessary for provenance, deduplication, and editorial review.

## Testing and Acceptance Criteria

### Pipeline

- Fake xAI responses validate the candidate schema without network access.
- Date filters, account groups, call caps, and query groups are deterministic.
- Malformed, duplicate, out-of-scope, unapproved-domain, and stale candidates are rejected.
- X-only candidates cannot become verified developments or trend evidence.
- Canonical first-party links inherit the first-party source tier only after successful fetch and evidence preservation.
- Provider usage and estimated costs are recorded.
- Missing `XAI_API_KEY` degrades only the discovery lane.
- Replaying a saved candidate set is idempotent and requires no new search call.

### Publication

- Every day has one dated edition record, including quiet days.
- An edition contains at most five items and never duplicates one story across statuses.
- Feed and detail pages show source status and X attribution clearly.
- Signal items never appear in verified developments, trend evidence, or weekly conclusions.
- Insight threads update only when new linked evidence exists.
- Existing RSS, event, trend, and weekly tests continue to pass.

### Operational trial

Before making X discovery a normal public input, run it in shadow mode for seven daily windows and record:

- relevant candidates per day;
- percentage resolved to first-party or trusted reporting;
- overlap with existing configured sources;
- percentage rejected as noise;
- estimated monthly cost;
- candidate-to-publication conversion rate.

The lane is promoted from shadow mode when it consistently adds unique, in-scope candidates at acceptable cost and quality.

## Deliberate Non-Goals

- Republishing an X timeline or full post archive.
- Ranking by likes, reposts, or controversy.
- Treating Grok output as verified evidence.
- Replacing Gemini as the editorial model.
- Publishing a fixed number of stories regardless of quality.
- Allowing arbitrary URLs returned by a model to be fetched.
- Making xAI availability a prerequisite for direct-source daily publication.
