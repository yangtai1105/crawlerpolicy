---
schema_version: 1
slug: fastly-blog-fastly-observes-over-6-million-daily-probing-requests-spoofing-ai-bots
title: "Fastly Observes Over 6 Million Daily Probing Requests Spoofing AI Bots"
source: fastly-blog
source_tier: specialist
status: reported
primary_track: access-controls
tracks:
  - access-controls
  - identity-authorization
  - measurement-economics
actors:
  - "Fastly"
subject: crawler
event_date: 2026-10-13T00:00:00+00:00
published_at: 2026-10-13T00:00:00+00:00
detected_at: 2026-10-31T20:51:06.172555+00:00
source_urls:
  - "https://www.fastly.com/blog/ai-bot-cosplay/"
change_kind: material
importance: 0.65
confidence: high
evidence_ids:
  - "fastly-blog--1ae04057d84be42a"
trend_signals:
  - ai-crawler-impersonation
  - crawler-verification-waf
players:
  - "fastly"
backfilled: false
---

## Summary

Fastly reported that more than 6 million requests in a single day impersonated AI bots to probe websites for private files. Attackers spoofed AI crawler identities to scan for sensitive data including .env files, Git metadata, and credentials. Fastly outlined Web Application Firewall (WAF) rules to detect and block these unauthorized impostors.

## Key facts

- Over 6 million requests posed as AI bots in a single day to probe for private files.
- Probing requests specifically targeted .env files, Git metadata, credentials, and other sensitive server assets.
- Fastly termed the impersonation threat 'AI bot cosplay.'
- Fastly deployed WAF rules to detect and block impostor bots mimicking AI crawlers.

## Insight

Attackers exploit permissive access policies granted to AI scrapers by disguising vulnerability scans under legitimate AI crawler identities, exposing the vulnerability of basic User-Agent string filtering.

## Implication

Site administrators and security teams will need to replace unverified User-Agent allowlists with robust crawler verification, such as reverse DNS lookups and IP range validation, to prevent credential harvesting.

## Why it matters

Exempting AI bots from strict bot protection creates an immediate attack vector unless access controls rigorously verify crawler provenance beyond easily faked request headers.

## Evidence

- [Primary source](https://www.fastly.com/blog/ai-bot-cosplay/)
- Evidence ID: `fastly-blog--1ae04057d84be42a`
