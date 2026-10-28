---
schema_version: 2
slug: cloudflare-web-bot-auth-rejects-duplicate-signature-labels-under-rfc-9421
title: "Cloudflare Web Bot Auth Rejects Duplicate Signature Labels Under RFC 9421"
source: web-bot-auth-repo
source_tier: primary
primary_track: standards-protocols
tracks:
  - standards-protocols
  - identity-authorization
  - platform-ecosystem
actors:
  - "Cloudflare"
event_date: 2026-10-27T18:45:43+00:00
published_at: 2026-10-27T18:45:43+00:00
detected_at: 2026-10-28T14:52:45.308044+00:00
source_url: "https://github.com/cloudflare/web-bot-auth/pull/169"
change_kind: material
importance: 0.50
confidence: high
evidence_ids:
  - "web-bot-auth-repo--cb346e9d26f1be1d"
---

## Development

Cloudflare updated the Rust reference verifier in its Web Bot Auth repository to enforce RFC 9421 rules requiring signature labels to be unique across all Signature-Input and Signature field values. Previously, the Rust parser used a structured field dictionary that silently retained only the last duplicate key and allowed invalid messages to verify. The update brings the Rust verifier into parity with the TypeScript implementation by returning a parsing error when duplicate labels are detected.

## Key facts

- RFC 9421 §4.1 and §4.2 mandate that signature labels 'MUST be unique across all field values' for both 'Signature-Input' and 'Signature'.
- Rust's 'MessageVerifier::parse' previously read headers into an 'sfv::Dictionary', which retained only the last duplicate key per RFC 9651 and merged values with 'extend', permitting repeated labels such as 'sig1' to verify.
- The TypeScript implementation of Web Bot Auth already rejected repeated signature labels with 'DuplicateLabel'.
- Both header fields now pass through a unified 'parse_signature_dictionary' helper that counts keys during parsing and raises a 'ParsingError' if any labels are dropped.
- Validation was executed on Rust 1.95 including workspace tests, clippy checks, formatting, documentation, and the wasm32 target.

## Why it matters

Cryptographic authentication for automated crawlers relies on strict cross-language parsing parity; subtle differences in how verifiers handle duplicate header labels could let malicious traffic slip past edge security controls.

## Trend impact

- rigorous adherence to RFC 9421 HTTP Message Signatures for crawler verification
- hardening and cross-runtime parity between Rust and TypeScript bot authentication libraries

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/169)
- Evidence ID: `web-bot-auth-repo--cb346e9d26f1be1d`

