---
schema_version: 1
slug: datadome-blog-meta-muse-agentic-browser-operates-without-declared-user-agent-or-dedicated-ip-r
title: "Meta Muse Agentic Browser Operates Without Declared User-Agent or Dedicated IP Ranges"
source: datadome-blog
source_tier: specialist
status: reported
primary_track: agentic-web
tracks:
  - agentic-web
  - crawler-controls
  - standards-protocols
actors:
  - "Meta"
  - "DataDome"
  - "Shopify"
  - "Amazon"
  - "Cloudflare"
  - "Fastly"
event_date: 2026-09-28T16:10:10+00:00
published_at: 2026-09-28T16:10:10+00:00
detected_at: 2026-09-28T16:29:28.092567+00:00
source_urls:
  - "https://datadome.co/threat-research/meta-muse-doesnt-declare-itself-heres-why-that-matters/"
change_kind: material
importance: 0.82
confidence: high
evidence_ids:
  - "datadome-blog--4ca1db7b982ac7ca"
trend_signals:
  - undeclared agentic traffic
  - sentinel virtual machine fingerprinting
  - agentic commerce friction
  - lack of cryptographic agent identity standards
backfilled: false
---

## Summary

Technical analysis from DataDome reveals that Meta's new consumer agent, Muse, does not identify itself via a distinct User-Agent header, custom request headers, or documented IP ranges. Muse sessions run inside sandboxed 'Sentinel VM' environments presenting as standard desktop Chrome on Linux and egressing through generic Cloudflare or Fastly address space without cryptographic signatures. DataDome added client-side environmental fingerprinting detection for Muse to its Agentic Trust dashboard to help merchants categorize or control this traffic.

## Insight

Unlike traditional search crawlers and AI scrapers that declare bot identities and maintain published IP allowlists, emerging consumer agentic browsers blend into ordinary desktop traffic, forcing site operators to rely on client-side browser fingerprinting and behavioral intent analysis rather than declarative protocol-level controls.

## Implication

Merchants and anti-bot systems face heightened challenges distinguishing authorized consumer proxy sessions from malicious automated scrapers, scalpers, and impersonation attacks that mimic sandboxed agent environments.

## Why it matters

As tech giants deploy agentic browsers that perform end-to-end commerce actions on behalf of consumers, the absence of standard identification protocols like Web Bot Auth creates friction between platforms embracing automated checkout and retailers blocking unverified automation.

## Evidence

- [Primary source](https://datadome.co/threat-research/meta-muse-doesnt-declare-itself-heres-why-that-matters/)
- Evidence ID: `datadome-blog--4ca1db7b982ac7ca`
