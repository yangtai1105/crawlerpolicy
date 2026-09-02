---
schema_version: 1
slug: cf-changelog-ai-search-cloudflare-ai-search-adds-custom-domains-mcp-access-controls-and-link-discovery-
title: "Cloudflare AI Search Adds Custom Domains, MCP Access Controls, and Link-Discovery Crawling"
source: cf-changelog-ai-search
source_tier: primary
status: verified
primary_track: agentic-web
tracks:
  - agentic-web
  - search-discovery
  - crawler-controls
actors:
  - "Cloudflare"
event_date: 2026-08-06T00:00:00+00:00
published_at: 2026-08-06T00:00:00+00:00
detected_at: 2026-08-30T05:51:00.726967+00:00
source_urls:
  - "https://developers.cloudflare.com/changelog/post/2026-08-06-public-endpoint-custom-domains-and-namespaces/"
change_kind: material
importance: 0.68
confidence: high
evidence_ids:
  - "cf-changelog-ai-search--d0c79db373ba0a55"
development_slug: cloudflare-ai-search-adds-custom-domains-mcp-access-controls-and-link-discovery-
backfilled: true
processed_at: 2026-09-02T06:16:39.453289+00:00
backfill_batch: direct-evidence_2026-06-01_2026-09-01
---

## Summary

Cloudflare has updated its AI Search service to support serving search endpoints from custom domains with Cloudflare Access authentication, enabling controlled access to agent endpoints like `/mcp`. The release also introduces namespace-level multi-instance fanout and a new `discover` parse type that crawls websites by following links rather than relying solely on sitemaps.

## Insight

By bundling link-depth web crawling with gated Model Context Protocol (`/mcp`) endpoints behind identity tokens, infrastructure providers are standardizing the full pipeline from raw site indexing to secure agent retrieval.

## Implication

Website owners and enterprise developers can restrict automated AI agent retrieval to authorized consumers while deploying custom crawlers that index sites lacking structured sitemaps.

## Why it matters

As websites transition from static search indexes to agent-facing endpoints, native crawler discovery combined with zero-trust access management ensures organizations can govern how their content is surfaced and queried by automated agents.

## Evidence

- [Primary source](https://developers.cloudflare.com/changelog/post/2026-08-06-public-endpoint-custom-domains-and-namespaces/)
- Evidence ID: `cf-changelog-ai-search--d0c79db373ba0a55`
