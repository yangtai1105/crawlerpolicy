---
schema_version: 2
slug: web-bot-auth-enforces-rfc-9421-key-algorithm-matching-rules
title: "Web Bot Auth Enforces RFC 9421 Key Algorithm Matching Rules"
source: web-bot-auth-repo
source_tier: primary
primary_track: standards-protocols
tracks:
  - standards-protocols
  - identity-authorization
  - access-controls
actors:
  - "Cloudflare"
event_date: 2026-10-19T15:59:51+00:00
published_at: 2026-10-19T15:59:51+00:00
detected_at: 2026-10-20T13:22:00.882558+00:00
source_url: "https://github.com/cloudflare/web-bot-auth/pull/157"
change_kind: material
importance: 0.51
confidence: high
evidence_ids:
  - "web-bot-auth-repo--f2800be0b3b43903"
---

## Development

A pull request to Cloudflare's Web Bot Auth repository implements RFC 9421 Section 3.2, step 6 verification rules. The update mandates that whenever an `alg` parameter is present in an HTTP signature, it must name a registered algorithm and agree with the algorithm of the resolved key. The change resolves issue #153 and supersedes earlier work in pull request #154.

## Key facts

- Pull request #157 in the Cloudflare Web Bot Auth repository implements RFC 9421 Section 3.2, step 6.
- The specification rule requires that when `alg` is present, it must name a registered algorithm and agree with the algorithm of the resolved key.
- The pull request resolves issue #153.
- The pull request supersedes pull request #154.

## Why it matters

As web hosts look toward cryptographic signatures under RFC 9421 to authenticate legitimate automated crawlers, strict adherence to algorithm validation prevents security bypasses stemming from mismatched or spoofed signature parameters.

## Trend impact

- Cryptographic bot authentication standards hardening
- RFC 9421 HTTP Message Signatures conformance

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/157)
- Evidence ID: `web-bot-auth-repo--f2800be0b3b43903`

