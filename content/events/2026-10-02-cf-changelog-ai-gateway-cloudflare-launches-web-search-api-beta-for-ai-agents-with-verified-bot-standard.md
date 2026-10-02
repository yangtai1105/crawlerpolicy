---
schema_version: 2
slug: cloudflare-launches-web-search-api-beta-for-ai-agents-with-verified-bot-standard
title: "Cloudflare Launches Web Search API Beta for AI Agents with Verified Bot Standards"
source: cf-changelog-ai-gateway
source_tier: primary
primary_track: agentic-web
tracks:
  - agentic-web
  - search-discovery
  - crawler-controls
actors:
  - "Cloudflare"
  - "Ceramic.ai"
  - "Exa"
  - "Linkup"
event_date: 2026-10-02T13:00:00+00:00
published_at: 2026-10-02T13:00:00+00:00
detected_at: 2026-10-02T14:29:07.997977+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-10-02-introducing-web-search-api/"
change_kind: material
importance: 0.72
confidence: high
evidence_ids:
  - "cf-changelog-ai-gateway--65cd43d47a98d8e1"
---

## Development

Cloudflare has introduced a beta release of its Web Search API to allow AI agents and applications to ground model responses in live web data through AI Gateway. At launch, developers can query third-party search providers Ceramic.ai, Exa, and Linkup via REST or Cloudflare Worker bindings. All participating search providers support Zero Data Retention for requests routed through Cloudflare and have committed to Cloudflare's verified bot crawling standards.

## Why it matters

As AI models transition from static training knowledge to real-time agentic web discovery, the infrastructure mediating web queries will determine how crawling traffic is identified, governed, and billed across the ecosystem.

## Trend impact

- agentic-search-apis
- crawler-verification-mandates
- zero-data-retention-proxies

## Evidence

- [Primary source](https://developers.cloudflare.com/changelog/post/2026-10-02-introducing-web-search-api/)
- Evidence ID: `cf-changelog-ai-gateway--65cd43d47a98d8e1`

