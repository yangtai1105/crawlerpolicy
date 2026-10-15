---
schema_version: 1
slug: cloudflare-blog-cloudflare-data-shows-yandex-outage-halted-verified-crawlers-while-malicious-aut
title: "Cloudflare Data Shows Yandex Outage Halted Verified Crawlers While Malicious Automation Migrated"
source: cloudflare-blog
source_tier: specialist
status: reported
primary_track: measurement-economics
tracks:
  - measurement-economics
  - search-discovery
  - access-controls
actors:
  - "Cloudflare"
  - "Yandex"
  - "Selectel"
  - "Radist"
subject: crawler
event_date: 2026-10-14T20:24:19+00:00
published_at: 2026-10-14T20:24:19+00:00
detected_at: 2026-10-15T13:05:42.271060+00:00
source_urls:
  - "https://blog.cloudflare.com/yandex-outage/"
change_kind: material
importance: 0.65
confidence: high
evidence_ids:
  - "cloudflare-blog--5a2555e77804fad4"
trend_signals:
  - crawler infrastructure resilience
  - bot workload portability
  - JA4 fingerprinting
players:
  - "cloudflare"
backfilled: false
---

## Summary

Following physical strikes on Yandex data center facilities in October 2026, Cloudflare observed traffic drops exceeding 90% across both Yandex Search (AS13238) and Yandex.Cloud (AS200350). The traffic drop from Yandex Search consisted almost entirely of verified indexing bots, notably YandexBot, YandexRenderResourcesBot, and YandexImages, which hit publishing sites the hardest. Conversely, malicious automation and probing from Yandex.Cloud did not halt globally, but instead migrated immediately to alternate Russian hosting providers such as Selectel and Radist with identical JA4 fingerprints and custom user-agent headers.

## Insight

Aggregate traffic and ASN-level drops conflate distinct classes of automated actors: infrastructure outages quickly disable centralized, verified search engine crawlers, whereas evasive and unverified bot operations maintain operational resilience by rapidly migrating workloads across hosting providers.

## Implication

Publishers and site operators will observe reduced indexing and discovery in Yandex Search while Yandex infrastructure remains offline, but security teams cannot rely on ASN-level disruption to block malicious bot operations.

## Why it matters

The analysis demonstrates that web crawling for search indexing is heavily tied to specific infrastructure, making it vulnerable to localized disruption, while malicious automation is highly portable across cloud providers and requires behavioral access controls rather than IP or ASN blocklists.

## Evidence

- [Primary source](https://blog.cloudflare.com/yandex-outage/)
- Evidence ID: `cloudflare-blog--5a2555e77804fad4`
