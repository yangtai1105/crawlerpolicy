---
schema_version: 2
slug: cloudflare-radar-integrates-botbase-and-adds-access-level-and-content-use-metada
title: "Cloudflare Radar Integrates BotBase and Adds Access Level and Content Use Metadata"
source: cf-changelog-radar
source_tier: measurement
primary_track: measurement-economics
tracks:
  - measurement-economics
  - access-controls
  - platform-ecosystem
  - identity-authorization
actors:
  - "Cloudflare"
event_date: 2026-11-09T00:00:00+00:00
published_at: 2026-11-09T00:00:00+00:00
detected_at: 2026-11-10T16:07:51.172582+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-11-09-radar-bots-directory-botbase/"
change_kind: material
importance: 0.68
confidence: high
evidence_ids:
  - "cf-changelog-radar--6921f9e63b3d07d2"
---

## Development

Cloudflare Radar has updated its Bots Directory to use BotBase, introducing structured tracking for both autonomous crawlers and delegated agents. Bot profiles and associated API endpoints now classify traffic by access level, content usage model, user agents, and Web Bot Auth verification status.

## Key facts

- The Cloudflare Radar Bots Directory now runs on BotBase, Cloudflare's catalog of tracked bots and agents.
- Bot profiles include a new Identity section detailing access level, content use, Web Bot Auth verification, and user agents.
- API endpoints 'List bots' and 'Get bot details' define accessLevel as either DIRECT (reaching websites under its own identity) or INTERMEDIARY (acting on behalf of another agent or a person).
- The contentUse field classifies bot data retention into full (content kept and reused, such as for model training or search indexing), reference (cited or linked back to the source), or immediate (used once to answer a user's request).
- The API now supports multiple categories per bot following BotBase groups, including the addition of a COMMERCE category.
- The category and operatorUrl API fields have been deprecated in favor of categories and documentationUrl.

## Why it matters

As AI agents blur the line between autonomous scrapers and user-driven proxy requests, edge platforms are standardizing metadata that categorizes not just who is fetching content, but why and how long the data is retained.

## Trend impact

- agent-vs-crawler taxonomy differentiation
- declarative content retention tracking
- edge bot directory standardization

## Evidence

- [Primary source](https://developers.cloudflare.com/changelog/post/2026-11-09-radar-bots-directory-botbase/)
- Evidence ID: `cf-changelog-radar--6921f9e63b3d07d2`

