---
schema_version: 1
slug: cloudflare-research-cloudflare-designs-post-quantum-anonymous-credentials-for-agent-rate-limiting-un
title: "Cloudflare Designs Post-Quantum Anonymous Credentials for Agent Rate Limiting Under MOLE"
source: cloudflare-research
source_tier: specialist
status: reported
primary_track: identity-authorization
tracks:
  - identity-authorization
  - access-controls
  - standards-protocols
  - platform-ecosystem
actors:
  - "Cloudflare"
  - "Mozilla"
  - "NIST"
subject: both
event_date: 2026-11-06T14:00:00+00:00
published_at: 2026-11-06T14:00:00+00:00
detected_at: 2026-11-06T15:41:50.881618+00:00
source_urls:
  - "https://blog.cloudflare.com/vole-mole/"
change_kind: material
importance: 0.68
confidence: high
evidence_ids:
  - "cloudflare-research--a8857902d6605e13"
trend_signals:
  - Shift toward cryptographic proof-of-authorization over behavioral fingerprinting for agent traffic
  - Decoupling of client identity from access tokens to guarantee unbiasable bot and agent access
  - Post-quantum cryptographic preparation moving into application-layer edge access controls
players:
  - "cloudflare"
  - "nist"
backfilled: false
---

## Summary

Cloudflare Research published design architectures and benchmarks for post-quantum anonymous credentials under MOLE (Moderation Of unLinkable Endorsements), the successor framework to Privacy Pass. The project aims to develop tools to moderate agentic traffic without compromising user privacy or allowing edge operators to discriminate by client issuer. Cloudflare demonstrated that combining VOLE-in-the-Head zero-knowledge proofs with multivariate signatures like UOV enables viable post-quantum token sizes and millisecond execution times.

## Key facts

- Privacy Pass tokens provide unconditional client privacy against quantum computers, but rely on classical RSA and elliptic curves that quantum attackers could forge to bypass rate limits.
- MOLE ('Moderation Of unLinkable Endorsements') introduces an anchor-hiding endorsement system where clients prove authorization from a trusted anchor set without revealing the specific issuer.
- A major goal of MOLE is developing tools to manage agentic traffic that threatens to exhaust site resources and degrade performance for human visitors.
- Cloudflare's implementation of the PoMFRIT blind signature using Unbalanced Oil and Vinegar (UOV) produces 4.3KB presentation sizes with under 1KB issuance.
- Cloudflare is developing two candidate schemes: VOLE-IHAT for MOLE endorsements (5.6KB issuance, 6.5KB presentation) and VOLE-ACT for credentials (5.4KB issuance, 12.0KB spend).
- Each cryptographic operation takes a few milliseconds in Cloudflare's open-source implementation, moving post-quantum credentials from cryptographic theory to protocol engineering.

## Insight

By decoupling parameter selection from protocol design via multivariate quadratic schemes and VOLE-in-the-Head zero-knowledge proofs, edge platforms can construct issuer-hiding endorsements that verify an agent's legitimacy across an anchor set without exposing who authorized it.

## Implication

Autonomous agent frameworks and web scrapers will increasingly interact with zero-knowledge rate-limiting systems, replacing intrusive browser fingerprinting or CAPTCHAs with cryptographic anonymous credentials that endure the transition to post-quantum computing.

## Why it matters

Managing autonomous agent traffic at edge scale requires robust access controls that resist quantum forgery while guaranteeing unlinkability, ensuring bot and agent moderation does not degrade into universal web tracking.

## Evidence

- [Primary source](https://blog.cloudflare.com/vole-mole/)
- Evidence ID: `cloudflare-research--a8857902d6605e13`
