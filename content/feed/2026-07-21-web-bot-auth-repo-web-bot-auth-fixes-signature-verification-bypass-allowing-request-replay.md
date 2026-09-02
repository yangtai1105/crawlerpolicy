---
schema_version: 1
slug: web-bot-auth-repo-web-bot-auth-fixes-signature-verification-bypass-allowing-request-replay
title: "Web Bot Auth Fixes Signature Verification Bypass Allowing Request Replay"
source: web-bot-auth-repo
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - crawler-controls
  - agentic-web
actors:
  - "Cloudflare"
event_date: 2026-07-21T09:35:47+00:00
published_at: 2026-07-21T09:35:47+00:00
detected_at: 2026-08-30T05:51:00.726967+00:00
source_urls:
  - "https://github.com/cloudflare/web-bot-auth/pull/114"
change_kind: material
importance: 0.75
confidence: high
evidence_ids:
  - "web-bot-auth-repo--1b77cd2d0104888d"
development_slug: web-bot-auth-fixes-signature-verification-bypass-allowing-request-replay
backfilled: true
processed_at: 2026-09-02T06:19:21.357490+00:00
backfill_batch: direct-evidence_2026-06-01_2026-09-01
---

## Summary

A vulnerability in the Web Bot Auth implementation allowed signatures with empty component lists to pass verification without binding to a request target. Pull request #114 resolves security advisory GHSA-x9cc-346q-g27m by requiring signature coverage of @authority or @target-uri and signature-agent headers. The fix ensures verification binds signatures to specific HTTP request targets, matching the behavior of the Rust reference implementation.

## Insight

Cryptographic signature validation provides no protection against replay or request substitution if the verifier does not strictly enforce component binding to the target URI and authority.

## Implication

Implementers and adopters using the Web Bot Auth verification libraries must ensure their verification logic validates required covered components to prevent credential replay across different endpoints.

## Why it matters

Emerging bot authentication standards depend entirely on request-bound cryptographic proof, making component verification enforcement essential to preventing unauthorized automated traffic spoofing.

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/114)
- Evidence ID: `web-bot-auth-repo--1b77cd2d0104888d`
