---
schema_version: 1
slug: x-discovery-payment-networks-introduce-public-key-signing-protocols-for-ai-agents
title: "Payment Networks Introduce Public Key Signing Protocols for AI Agents"
source: x-discovery
source_tier: commentary
status: signal
primary_track: identity-authorization
tracks:
  - identity-authorization
  - standards-protocols
  - measurement-economics
  - access-controls
actors:
  - "Thales"
  - "Visa"
  - "Mastercard"
  - "Cloudflare"
subject: both
event_date: 2026-11-13T18:30:00+00:00
published_at: 2026-11-13T18:30:00+00:00
detected_at: 2026-11-14T14:47:35.236589+00:00
source_urls:
  - "https://x.com/EauDoon/status/2121309621662986697"
change_kind: material
importance: 0.72
confidence: high
evidence_ids:
  - "x-discovery--9a189f378d284975"
trend_signals:
  - Cryptographic agent authentication
  - Majority bot traffic inflection
  - Payment network mediation of autonomous AI agents
players:
  - "visa"
  - "mastercard"
  - "cloudflare"
protocols:
  - "web-bot-auth"
position_claims:
  - player: "cloudflare"
    protocol: "web-bot-auth"
    status: shipped
backfilled: false
---

## Summary

A Thales report found that bots accounted for over 53% of web traffic in 2025, reaching 58% in Singapore, and identified AI agents as an emerging traffic category. In response to agentic activity, Visa and Mastercard have introduced frameworks that require agents to register public keys and cryptographically sign requests. Both Visa's Trusted Agent Protocol and Mastercard's Agent Pay build directly on Cloudflare's Web Bot Auth architecture.

## Key facts

- A Thales report found that bots comprised over 53% of global web traffic in 2025.
- Bot traffic reached 58% of total web traffic in Singapore according to the report.
- The Thales report classifies AI agents as an emerging third category alongside human users and conventional bots.
- Visa's Trusted Agent Protocol requires agents to register public keys and sign requests.
- Mastercard's Agent Pay requires agents to register public keys and sign requests.
- Both Visa's and Mastercard's agent verification mechanisms build upon Cloudflare's Web Bot Auth.

## Insight

Agent identification is shifting from passive heuristic fingerprinting and user-agent string declarations toward cryptographically verifiable identity standards anchored by major financial networks and edge infrastructure providers.

## Implication

Autonomous commercial agents and delegating platforms will need to implement public-key registration and request signing to interact with commerce endpoints without being blocked as untrusted bots.

## Why it matters

As bot traffic crosses the majority threshold of web requests, payment networks and edge CDNs are establishing enforceable cryptographic protocols to distinguish authorized autonomous transactions from unauthorized scraping and automated abuse.

## Evidence

- [Primary source](https://x.com/EauDoon/status/2121309621662986697)
- Evidence ID: `x-discovery--9a189f378d284975`
