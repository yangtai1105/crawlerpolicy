---
schema_version: 1
slug: datadome-blog-meta-migrates-muse-agentic-browser-signatures-from-meta-com-to-muse-ai
title: "Meta Migrates Muse Agentic Browser Signatures From meta.com to muse.ai"
source: datadome-blog
source_tier: specialist
status: reported
primary_track: identity-authorization
tracks:
  - identity-authorization
  - standards-protocols
  - access-controls
actors:
  - "Meta"
  - "Muse"
  - "DataDome"
subject: agent
event_date: 2026-11-11T14:50:47+00:00
published_at: 2026-11-11T14:50:47+00:00
detected_at: 2026-11-11T15:53:10.884486+00:00
source_urls:
  - "https://datadome.co/threat-research/meta-muse-now-signs-as-muse-ai/"
change_kind: material
importance: 0.68
confidence: high
evidence_ids:
  - "datadome-blog--da8d7906e0961578"
trend_signals:
  - product-specific agent cryptographic identities
  - gradual signature directory rollouts
  - dynamic agent key discovery
players:
  - "meta"
  - "datadome"
protocols:
  - "web-bot-auth"
position_claims:
  - player: "meta"
    protocol: "web-bot-auth"
    status: shipped
backfilled: false
---

## Summary

Meta transitioned the cryptographic Web Bot Auth signatures for its Muse agentic browser from Meta's corporate key directory to a product-specific directory at muse.ai. The 60-hour rollout began on November 7 and completed on November 9, moving Muse's Signature-Agent header to https://muse.ai. Sites and security systems validating signatures strictly against meta.com now treat Muse requests as unverified unless they update their trusted key directories.

## Key facts

- Muse shifted its cryptographic signing header from Signature-Agent: "https://www.meta.com" to Signature-Agent: "https://muse.ai".
- The transition started around midnight PST on Saturday, November 7, ran at approximately 50/50 for a day and a half, and completed on Monday, November 9.
- The 60-hour overlap gave verifiers time to register the new key directory at https://muse.ai/.well-known/http-message-signatures-directory before the meta.com directory stopped signing Muse traffic.
- Muse's total signed traffic volume remained constant across the transition period.
- Verifiers checking Web Bot Auth signatures that trust only meta.com now see Muse requests as unverified or unknown.
- As of November 10, roughly half of Muse requests still arrive unsigned, requiring detection via client-side signals.
- DataDome updated its list of verified bots and agents to include the new muse.ai key directory.

## Insight

AI operators are decoupling product-level agent identities from parent corporate domains in cryptographic authentication headers, forcing bot verifiers to handle dynamic, multi-domain signature registries rather than hardcoded corporate trust lists.

## Implication

Web hosts and security providers using Web Bot Auth must continuously discover or update accepted signature directories, or risk misclassifying recognized AI agents as unauthenticated scrapers.

## Why it matters

Cryptographic proof of bot identity replaces easily spoofed user-agent strings, but shifts the verification burden to tracking domain-level signature migrations across multi-product AI vendors.

## Evidence

- [Primary source](https://datadome.co/threat-research/meta-muse-now-signs-as-muse-ai/)
- Evidence ID: `datadome-blog--da8d7906e0961578`
