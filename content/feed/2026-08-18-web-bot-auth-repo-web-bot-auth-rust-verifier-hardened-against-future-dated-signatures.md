---
schema_version: 1
slug: web-bot-auth-repo-web-bot-auth-rust-verifier-hardened-against-future-dated-signatures
title: "Web Bot Auth Rust Verifier Hardened Against Future-Dated Signatures"
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
event_date: 2026-08-18T02:19:46+00:00
published_at: 2026-08-18T02:19:46+00:00
detected_at: 2026-08-30T05:51:00.726967+00:00
source_urls:
  - "https://github.com/cloudflare/web-bot-auth/pull/127"
change_kind: material
importance: 0.45
confidence: high
evidence_ids:
  - "web-bot-auth-repo--1fa8d57cb4122f97"
development_slug: web-bot-auth-rust-verifier-hardened-against-future-dated-signatures
backfilled: true
processed_at: 2026-09-02T06:15:06.311359+00:00
backfill_batch: direct-evidence_2026-06-01_2026-09-01
---

## Summary

A pull request to Cloudflare's Web Bot Auth specification repository updates the Rust verifier implementation to fail closed when a signature's created timestamp is in the future. Previously, the Rust library verified the cryptographic signature before checking created timestamps, diverging from the TypeScript reference implementation which already rejected them upfront. The change aligns both implementations by validating timestamp windows prior to running cryptographic checks.

## Insight

Protocol parity across multiple language reference implementations is critical for authentication standards; divergent validation sequences between Rust and TypeScript created an edge-case discrepancy where compromised keys could use forward-skewed creation times.

## Implication

Developers and server operators deploying the Rust implementation of Web Bot Auth will now strictly reject requests carrying signatures with future creation timestamps, standardizing signature enforcement across deployment stacks.

## Why it matters

As cryptographic bot verification frameworks mature into industry standards, consistent fail-closed behavior across reference libraries prevents implementation-specific security bypasses and replay vulnerabilities.

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/127)
- Evidence ID: `web-bot-auth-repo--1fa8d57cb4122f97`
