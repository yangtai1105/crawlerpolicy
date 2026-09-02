---
schema_version: 2
slug: cloudflare-patches-web-bot-auth-rust-verifier-to-enforce-expiration-checks
title: "Cloudflare Patches Web Bot Auth Rust Verifier to Enforce Expiration Checks"
source: web-bot-auth-repo
source_tier: primary
primary_track: standards-protocols
tracks:
  - standards-protocols
  - crawler-controls
  - agentic-web
actors:
  - "Cloudflare"
event_date: 2026-08-13T03:22:43+00:00
published_at: 2026-08-13T03:22:43+00:00
detected_at: 2026-08-30T05:51:00.726967+00:00
source_url: "https://github.com/cloudflare/web-bot-auth/pull/125"
change_kind: material
importance: 0.55
confidence: high
evidence_ids:
  - "web-bot-auth-repo--aa18efd7c08ab295"
---

## Development

Cloudflare updated its Web Bot Auth Rust reference implementation to reject expired signatures by default during verification. Previously, `WebBotAuthVerifier::verify` permitted signatures with elapsed expiration timestamps if the cryptographic payload was otherwise valid. The change aligns the Rust library's fail-closed behavior with the TypeScript implementation.

## Why it matters

As cryptographic signatures become the cornerstone for verifying automated agents, inconsistent expiration validation across SDKs could allow malicious actors to exploit stale credentials.

## Trend impact

- cryptographic bot authentication
- fail-closed verification
- bot identity standardization

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/125)
- Evidence ID: `web-bot-auth-repo--aa18efd7c08ab295`

