---
schema_version: 2
slug: web-bot-auth-verifier-disallows-shared-hmac-signatures
title: "Web Bot Auth Verifier Disallows Shared HMAC Signatures"
source: web-bot-auth-repo
source_tier: primary
primary_track: standards-protocols
tracks:
  - standards-protocols
  - identity-authorization
  - access-controls
actors:
  - "Cloudflare"
event_date: 2026-11-06T15:07:02+00:00
published_at: 2026-11-06T15:07:02+00:00
detected_at: 2026-11-06T15:41:50.881618+00:00
source_url: "https://github.com/cloudflare/web-bot-auth/pull/187"
change_kind: material
importance: 0.55
confidence: high
evidence_ids:
  - "web-bot-auth-repo--2f675ebb40cb7d9e"
---

## Development

The Web Bot Auth specification reference implementation has been updated to strictly reject shared HMAC signatures during verification. Although HMAC is not supported in keyrings, it was previously retained in the shared HTTP message signatures library. The project chose to enforce the ban at the verifier layer rather than removing HMAC from the underlying algorithm definitions, preserving generic RFC 9421 compatibility.

## Key facts

- Per the Web Bot Auth protocol, shared HMAC is no longer considered acceptable for bot authentication.
- Shared HMAC is currently not supported in keyrings but retains utility for generic HTTP message signatures under RFC 9421.
- Maintainers implemented the restriction by making the Web Bot Auth verifier stricter rather than removing the algorithm from the underlying Algorithm enum.
- Removing HMAC from the Algorithm enum was avoided because it would constitute a low-level breaking change for generic HTTP message signature use cases.
- The change maintains full RFC 9421 coverage while strictly enforcing new Web Bot Auth verification contracts.

## Why it matters

Cryptographic crawler verification relies on public verifiability without distributing private signing secrets to edge verifiers. Deprecating shared HMAC prevents insecure authentication setups from undermining the emerging cryptographic bot identification ecosystem.

## Trend impact

- cryptographic crawler authentication
- asymmetric bot identity
- RFC 9421 implementation hardening

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/187)
- Evidence ID: `web-bot-auth-repo--2f675ebb40cb7d9e`

