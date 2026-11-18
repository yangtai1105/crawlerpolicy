---
schema_version: 1
slug: x-discovery-google-details-bot-defense-verification-and-cryptographic-signatures-for-google-
title: "Google Details Bot-Defense Verification and Cryptographic Signatures for Google-Agent"
source: x-discovery
source_tier: commentary
status: signal
primary_track: access-controls
tracks:
  - access-controls
  - identity-authorization
  - standards-protocols
  - platform-ecosystem
actors:
  - "Google"
  - "IETF"
subject: agent
event_date: 2026-11-17T19:07:41+00:00
published_at: 2026-11-17T19:07:41+00:00
detected_at: 2026-11-18T16:57:56.492918+00:00
source_urls:
  - "https://x.com/rep_insider/status/2122768656316740011"
  - "https://www.reputation-insider.com/google-tells-websites-how-to-let-ai-agents-past-bot-defenses/"
change_kind: material
importance: 0.78
confidence: high
evidence_ids:
  - "x-discovery--590af0057172938e"
trend_signals:
  - agentic-web-access
  - cryptographic-bot-authentication
  - bypass-of-robots-txt-by-delegated-agents
  - firewall-adaptation-for-ai-agents
players:
  - "google"
  - "ietf"
protocols:
  - "web-bot-auth"
  - "robots-txt"
position_claims:
  - player: "google"
    protocol: "web-bot-auth"
    status: preview
saved_copies:
  - "https://github.com/yangtai1105/crawlerpolicy-archive/blob/main/articles/2026-11-17/x-discovery--590af0057172938e-1.md"
backfilled: false
---

## Summary

Google has published technical guidance advising website operators on how to identify, verify, and permit requests from its user-directed AI agent, Google-Agent, through content delivery networks and bot-management firewalls. The instructions specify verification via the Google-Agent User-Agent header paired with published IP address ranges in user-triggered-agents.json, while noting that user-directed agents bypass robots.txt. Google is also previewing an experimental implementation of Web Bot Auth using RFC 9421 HTTP Message Signatures to cryptographically authenticate participating requests.

## Key facts

- Google published operational instructions for website operators to verify requests from Google-Agent, an existing user-directed AI agent that performs tasks on behalf of users.
- Google-Agent requests contain the identifier 'Google-Agent' in the User-Agent header and originate from IP ranges listed in Google's published user-triggered-agents.json file.
- Google noted that Google-Agent operates in response to user actions and generally ignores robots.txt restrictions, distinguishing it from conventional search crawling.
- The guidance warns that allowlists must cover more than page loading, specifically highlighting add-to-cart operations, booking functions, XHR requests, and GraphQL or API endpoints that are often blocked downstream.
- Google advised operators to let verified agent traffic bypass interactive verification procedures, including CAPTCHA checks and JavaScript challenges.
- Google is experimentally testing Web Bot Auth using RFC 9421 HTTP Message Signatures, where participating agents identify as 'https://agent.bot.goog' and include Signature-Agent, Signature, and Signature-Input headers.
- Web Bot Auth remains in development through the IETF and applies only to a subset of Google-Agent traffic, meaning websites cannot yet rely exclusively on cryptographic signatures for verification.

## Insight

Traditional bot defenses treat non-human automated traffic uniformly, but user-directed agents execute multi-step interactive workflows—such as cart operations and API calls—that break under conventional CAPTCHAs, per-IP rate limits, and endpoint-level filtering unless firewalls explicitly carve out deep, multi-layer exemptions.

## Implication

Website administrators and security vendors will need to distinguish search indexers from authenticated transactional user agents, potentially reconfiguring WAF evaluation orders, API endpoint rules, and rate limits to accommodate multi-user egress IPs without opening holes to spoofed bot traffic.

## Why it matters

As search engines evolve into task-executing agents, websites face a trade-off between protecting transactional infrastructure from automated abuse and enabling user-commissioned AI browsing that cannot complete CAPTCHA challenges or multi-step checkout flows.

## Evidence

- [Primary source](https://x.com/rep_insider/status/2122768656316740011)
- [Supporting source 2](https://www.reputation-insider.com/google-tells-websites-how-to-let-ai-agents-past-bot-defenses/)
- Evidence ID: `x-discovery--590af0057172938e`
