---
schema_version: 1
slug: akamai-blog-akamai-details-rise-of-silent-ai-agents-and-advocates-endpoint-level-cryptograph
title: "Akamai Details Rise of Silent AI Agents and Advocates Endpoint-Level Cryptographic Governance"
source: akamai-blog
source_tier: specialist
status: reported
primary_track: identity-authorization
tracks:
  - identity-authorization
  - access-controls
  - measurement-economics
  - standards-protocols
actors:
  - "Akamai"
  - "Meta"
  - "OpenAI"
  - "Amazon"
  - "Visa"
  - "Skyfire"
  - "Experian"
  - "IETF"
subject: both
event_date: 2026-10-26T15:20:00+00:00
published_at: 2026-10-26T15:20:00+00:00
detected_at: 2026-10-31T20:51:06.172555+00:00
source_urls:
  - "https://www.akamai.com/blog/ai/2026/oct/silent-agents-are-already-on-your-site"
change_kind: material
importance: 0.72
confidence: high
evidence_ids:
  - "akamai-blog--0bda52142e5910a0"
trend_signals:
  - credential-backed silent agent browsing
  - endpoint-specific policy replacing sitewide robots directives
  - cryptographic agent identity standards adoption
players:
  - "akamai"
  - "meta"
  - "openai"
  - "amazon"
  - "visa"
  - "skyfire"
  - "ietf"
protocols:
  - "web-bot-auth"
position_claims:
  - player: "akamai"
    protocol: "web-bot-auth"
    status: stated
backfilled: false
---

## Summary

Akamai published guidance warning that unverified silent AI agents are operating on commerce and banking sites by masquerading as standard browser sessions using consumer credentials. Network data revealed that commerce accounted for 47.9% of AI bot traffic from July to December 2025, with more than 90% left on monitor-only mode. Akamai advised digital operators to abandon binary sitewide blocking in favor of endpoint-level access controls while adopting emerging cryptographic verification standards.

## Key facts

- Commerce accounted for 47.9% of all AI bot traffic across Akamai's global network between July 2025 and December 2025.
- More than 90% of AI bot traffic in commerce had been categorized as monitor-only without active governance, and roughly 75% of the remaining traffic was allowed unrestricted.
- Akamai defines a silent agent as 'automation acting through an ordinary browser or customer session without providing a verifiable agent identity.'
- OpenAI advises users that 'If a website blocks the cloud browser, ask your dot to try your connected computer,' shifting execution to local unflagged environments.
- In August 2026, Akamai segmented its Bot Directory into three categories: training crawlers, search crawlers, and fetchers/agents.
- Amazon blocked Meta's Muse agent from purchasing on behalf of users in September 2026, and major U.S. banks issued public restrictions on agent account access in mid-October 2026.
- Akamai integrated support for cryptographic and trust frameworks including the IETF Web Bot Auth draft, Visa's Trusted Agent Protocol, Skyfire's Know Your Agent (KYA), and Experian Agent Trust.

## Insight

The operational boundary in automated web access is shifting from crawler discovery to delegated user execution, where agents actively evade bot mitigation by routing through local customer machines or browser profiles without cryptographic provenance.

## Implication

E-commerce platforms and financial institutions will increasingly mandate cryptographic authentication at sensitive transactional endpoints while keeping public catalog endpoints open to preserve search and referral traffic.

## Why it matters

Binary blocking forfeits revenue from authorized consumer assistants, whereas blanket permission exposes authenticated accounts to automated fraud, credential abuse, and prompt-injection risks.

## Evidence

- [Primary source](https://www.akamai.com/blog/ai/2026/oct/silent-agents-are-already-on-your-site)
- Evidence ID: `akamai-blog--0bda52142e5910a0`
