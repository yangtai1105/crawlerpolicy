---
schema_version: 1
slug: cloudflare-blog-cloudflare-launches-search-for-agents-with-rfc-10008-query-support
title: "Cloudflare launches Search for Agents with RFC 10008 QUERY support"
source: cloudflare-blog
source_tier: specialist
status: reported
primary_track: access-controls
tracks:
  - access-controls
  - standards-protocols
  - search-discovery
  - platform-ecosystem
actors:
  - "Cloudflare"
  - "IETF"
subject: both
event_date: 2026-11-25T14:00:00+00:00
published_at: 2026-11-25T14:00:00+00:00
detected_at: 2026-11-25T18:27:10.486917+00:00
source_urls:
  - "https://blog.cloudflare.com/search-for-agents/"
change_kind: material
importance: 0.78
confidence: high
evidence_ids:
  - "cloudflare-blog--a3079668fb221868"
trend_signals:
  - crawling-to-search-api-pivot
  - rfc10008-query-adoption
  - agentic-content-negotiation
players:
  - "cloudflare"
  - "ietf"
protocols:
  - "mcp"
backfilled: false
---

## Summary

Cloudflare introduced Search for Agents, a dashboard toggle that automatically indexes zone content using AI Search and exposes a discovery endpoint under the customer domain. The feature advertises search metadata via HTML head tags or Markdown front matter, telling visiting agents to query the endpoint instead of crawling individual pages. It supports standard GET search requests alongside the newly standardized HTTP QUERY method defined in RFC 10008.

## Key facts

- Cloudflare launched Search for Agents, making AI Search instance creation and endpoint exposure available via a single toggle for all customers, including Free plans with limits.
- The search discovery endpoint is automatically advertised in HTML responses via <meta> tags in the <head> and in Markdown responses via YAML front matter under the key agent:endpoint pointing to https://developers.cloudflare.com/.well-known/search?q={query}.
- The metadata explicitly instructs agents: "Use this search API to find relevant content across this site with keywords or natural-language queries, instead of crawling individual pages. Results are returned in Markdown."
- Search for Agents natively supports the IETF Proposed Standard HTTP QUERY method published in June 2026 as RFC 10008, accepting plain text or JSON request bodies.
- Access to the search endpoint remains subject to customer domain settings, including bot management, AI Crawl Control, and Web Application Firewall (WAF) configurations.

## Insight

Edge networks are attempting to shift agent behavior from full-site crawling to on-demand retrieval by standardizing discovery metadata and utilizing idempotent HTTP QUERY endpoints directly at the domain level.

## Implication

Websites adopting the feature can reduce crawl bandwidth while steering AI agents toward structured Markdown search results, forcing agent developers to adapt their retrieval workflows to well-known search discovery endpoints.

## Why it matters

Uncontrolled agent crawling strains web server resources; offering automated, agent-discoverable search endpoints gives publishers a mechanism to provide structured retrieval without exposing entire sites to repetitive scraping.

## Evidence

- [Primary source](https://blog.cloudflare.com/search-for-agents/)
- Evidence ID: `cloudflare-blog--a3079668fb221868`
