---
schema_version: 1
slug: akamai-blog-akamai-promotes-edge-content-shaping-and-price-deception-to-thwart-competitor-sc
title: "Akamai Promotes Edge Content Shaping and Price Deception to Thwart Competitor Scrapers"
source: akamai-blog
source_tier: specialist
status: reported
primary_track: access-controls
tracks:
  - access-controls
  - measurement-economics
  - platform-ecosystem
actors:
  - "Akamai Technologies"
subject: crawler
event_date: 2026-09-21T05:00:00+00:00
published_at: 2026-09-21T05:00:00+00:00
detected_at: 2026-10-31T20:51:06.172555+00:00
source_urls:
  - "https://www.akamai.com/blog/security/2026/sep/what-to-do-when-competitors-scraping-prices"
change_kind: material
importance: 0.72
confidence: high
evidence_ids:
  - "akamai-blog--22d014275390f70e"
trend_signals:
  - edge-native payload shaping over binary IP blocking
  - deliberate data poisoning against competitive repricing scrapers
  - increasing concentration of AI bot scraping on ecommerce catalogs
backfilled: false
---

## Summary

Akamai has detailed a defensive architecture combining Akamai Bot Manager with serverless Akamai Functions to combat competitive price scraping. Instead of outright blocking scrapers—which triggers bot operators to rotate IP addresses—the edge proxy dynamically rewrites responses to serve poisoned, stale, or degraded pricing data while preserving full access for legitimate shoppers and search indexers. Akamai also revealed that bots account for 51% of global web traffic and more than 45% of network-observed AI bot requests target ecommerce platforms.

## Key facts

- Bots represent 51% of global web traffic and bad bots make up 37% of all internet traffic (nearly two-thirds of all bot traffic) according to Akamai's 2026 State of the Internet report.
- AI bot activity increased 300% year-over-year in 2025, with more than 45% of all AI bot traffic on Akamai networks targeting commerce customers—amounting to over 25 billion AI bot requests across a two-month period.
- Across 6.9 billion ecommerce requests analyzed by Akamai, 65% of bot traffic originated from scrapers classified as bad bots.
- Akamai proposes using Akamai Functions and Akamai Bot Manager as a rewriting proxy to replace price values with stale, randomized, or withheld data when competitor scrapers are detected.
- Author Matt Butcher warned that "Traditional IP blocking alerts scrapers, causing an endless escalating cycle that risks blocking real shoppers and partners," arguing instead that "Shoppers can't buy what they can't see" while competitor bots can be served altered data.
- The edge-native solution uses Akamai EdgeKV key-value storage to authenticate partner APIs and comparison engines, executing in Rust, Go, JavaScript, or Python with cold-start latencies of approximately 0.5 milliseconds.

## Insight

Anti-scraping defense is evolving from binary perimeter rejection to deceptive payload manipulation at the edge, treating scraping as an economic data-integrity contest rather than an access-denial battle.

## Implication

Automated repricing tools and commercial scrapers will increasingly ingest poisoned data without receiving HTTP error alerts, forcing scraper operators to develop secondary validation mechanisms to verify whether edge-delivered prices are authentic.

## Why it matters

Binary IP and fingerprint blocks trigger aggressive evasion tactics and risk degrading access for legitimate shoppers and search crawlers; selective content degradation neutralizes competitive price extraction without alerting the scraping bot.

## Evidence

- [Primary source](https://www.akamai.com/blog/security/2026/sep/what-to-do-when-competitors-scraping-prices)
- Evidence ID: `akamai-blog--22d014275390f70e`
