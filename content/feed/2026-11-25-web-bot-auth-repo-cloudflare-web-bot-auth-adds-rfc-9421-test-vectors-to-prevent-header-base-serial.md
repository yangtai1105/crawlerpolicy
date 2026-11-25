---
schema_version: 1
slug: web-bot-auth-repo-cloudflare-web-bot-auth-adds-rfc-9421-test-vectors-to-prevent-header-base-serial
title: "Cloudflare Web Bot Auth Adds RFC 9421 Test Vectors to Prevent Header Base Serialization Bugs"
source: web-bot-auth-repo
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - platform-ecosystem
  - access-controls
actors:
  - "Cloudflare"
subject: both
event_date: 2026-11-25T08:47:41+00:00
published_at: 2026-11-25T08:47:41+00:00
detected_at: 2026-11-25T18:27:10.486917+00:00
source_urls:
  - "https://github.com/cloudflare/web-bot-auth/pull/206"
change_kind: material
importance: 0.46
confidence: high
evidence_ids:
  - "web-bot-auth-repo--31029b05cb6ff41a"
trend_signals:
  - cryptographic bot authentication hardening
  - strict RFC 9421 header dictionary parsing compliance
development_slug: cloudflare-web-bot-auth-adds-rfc-9421-test-vectors-to-prevent-header-base-serial
players:
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

Cloudflare's Web Bot Auth repository added explicit verification test cases replaying Ed25519 vectors from draft-01 of the specification. The new tests address a discrepancy where verifiers constructed RFC 9421 signature bases using entire field values rather than dictionary member values. The update also documents support for both dictionary and legacy string forms during protocol migration.

## Key facts

- A bug in older deployed demo builds caused the Web Bot Auth verifier to extract whole field values (`sig1="https://..."`) instead of member values (`"https://..."`) when constructing component bases under RFC 9421 section 2.1.2.
- Prior to this change, all 33 existing worker tests signed requests using the repository's own `sign()` function, allowing mutual base construction bugs in `sign()` and `verify()` to pass undetected.
- The pull request adds test cases to `/v0/api/verify` replaying static E.2.1 (dictionary) and E.2.2 (legacy) Ed25519 test vectors directly from draft-01.
- The demo landing page was updated to link to the IETF draft and state acceptance of both the dictionary form and the legacy string form for migration.

## Insight

Self-referential test suites that generate test inputs using their own internal signing implementations fail to detect shared serialization errors, allowing deviations from RFC 9421 member-value parsing to persist in deployed verifiers.

## Implication

Implementers of cryptographic bot authentication must validate against canonical external RFC test vectors rather than internally generated signatures to prevent production rejections of valid crawler requests.

## Why it matters

Edge verifiers that misparse structured dictionary headers reject valid automated crawlers and agents that comply with RFC 9421 standards, causing false-positive access denials.

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/206)
- Evidence ID: `web-bot-auth-repo--31029b05cb6ff41a`
