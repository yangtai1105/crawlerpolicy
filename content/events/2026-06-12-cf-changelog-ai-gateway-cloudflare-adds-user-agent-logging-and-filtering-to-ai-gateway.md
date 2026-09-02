---
schema_version: 2
slug: cloudflare-adds-user-agent-logging-and-filtering-to-ai-gateway
title: "Cloudflare Adds User-Agent Logging and Filtering to AI Gateway"
source: cf-changelog-ai-gateway
source_tier: primary
primary_track: agentic-web
tracks:
  - agentic-web
  - crawler-controls
  - standards-protocols
actors:
  - "Cloudflare"
event_date: 2026-06-12T00:00:00+00:00
published_at: 2026-06-12T00:00:00+00:00
detected_at: 2026-08-30T05:51:00.726967+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-06-12-user-agent-logging/"
change_kind: material
importance: 0.55
confidence: high
evidence_ids:
  - "cf-changelog-ai-gateway--5122ae7cb6371559"
---

## Development

Cloudflare has updated AI Gateway to capture the client user agent for every incoming request. Operators can now view the user agent alongside existing request metadata and filter logs in the dashboard by exact match, exclusion, or substring.

## Why it matters

As automated agents and diverse AI client libraries proliferate, visibility into the exact client software initiating model queries becomes essential for governance, debugging, and traffic attribution.

## Trend impact

- ai-gateway-observability
- client-attribution
- agent-telemetry

## Evidence

- [Primary source](https://developers.cloudflare.com/changelog/post/2026-06-12-user-agent-logging/)
- Evidence ID: `cf-changelog-ai-gateway--5122ae7cb6371559`

