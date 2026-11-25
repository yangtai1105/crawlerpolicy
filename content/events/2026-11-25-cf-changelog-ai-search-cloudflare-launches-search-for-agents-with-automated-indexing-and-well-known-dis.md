---
schema_version: 2
slug: cloudflare-launches-search-for-agents-with-automated-indexing-and-well-known-dis
title: "Cloudflare launches Search for Agents with automated indexing and .well-known discovery"
source: cf-changelog-ai-search
source_tier: primary
primary_track: search-discovery
tracks:
  - search-discovery
  - platform-ecosystem
  - standards-protocols
actors:
  - "Cloudflare"
event_date: 2026-11-25T00:00:00+00:00
published_at: 2026-11-25T00:00:00+00:00
detected_at: 2026-11-25T18:27:10.486917+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-11-25-search-for-agents/"
change_kind: material
importance: 0.72
confidence: high
evidence_ids:
  - "cf-changelog-ai-search--c3e94e9ecf5854dd"
---

## Development

Cloudflare has introduced Search for Agents, a dashboard feature that automatically indexes a website's content and publishes a search endpoint on the domain. Agents discover the endpoint via HTML or Markdown metadata and can query it at `/.well-known/search` using HTTP GET or QUERY methods. The endpoint returns indexed content in raw Markdown format rather than synthesized answers, allowing visiting agents to process the source data directly.

## Key facts

- Search for Agents can be enabled under Quick Actions on the domain Overview page in the Cloudflare dashboard.
- Cloudflare automatically creates an AI Search instance, indexes site content, and exposes a search endpoint on the domain.
- The search interface is exposed at `https://<domain>/.well-known/search`.
- Cloudflare injects discovery metadata into HTML pages and, when Markdown for Agents is active, into Markdown responses.
- The endpoint supports both HTTP GET and HTTP QUERY requests.
- Responses are served as relevant content in Markdown rather than AI-generated conversational answers.
- The feature is available across all Cloudflare plans, subject to AI Search pricing and plan limits.

## Why it matters

As automated agents increasingly browse the live web, standardizing discovery endpoints like `/.well-known/search` and returning token-efficient Markdown provides an alternative to traditional, resource-intensive web scraping.

## Trend impact

- standardization of .well-known agent discovery
- adoption of HTTP QUERY method for agent search
- shift from bot scraping to edge-indexed search APIs
- markdown-first content delivery for autonomous agents

## Evidence

- [Primary source](https://developers.cloudflare.com/changelog/post/2026-11-25-search-for-agents/)
- Evidence ID: `cf-changelog-ai-search--c3e94e9ecf5854dd`

