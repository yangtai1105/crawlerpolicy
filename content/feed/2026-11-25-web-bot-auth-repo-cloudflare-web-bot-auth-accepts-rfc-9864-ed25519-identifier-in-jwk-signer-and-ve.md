---
schema_version: 1
slug: web-bot-auth-repo-cloudflare-web-bot-auth-accepts-rfc-9864-ed25519-identifier-in-jwk-signer-and-ve
title: "Cloudflare Web Bot Auth Accepts RFC 9864 'Ed25519' Identifier in JWK Signer and Verifier"
source: web-bot-auth-repo
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - identity-authorization
actors:
  - "Cloudflare"
subject: crawler
event_date: 2026-11-25T08:49:26+00:00
published_at: 2026-11-25T08:49:26+00:00
detected_at: 2026-11-25T18:27:10.486917+00:00
source_urls:
  - "https://github.com/cloudflare/web-bot-auth/pull/201"
change_kind: material
importance: 0.48
confidence: high
evidence_ids:
  - "web-bot-auth-repo--a5b3da832249fc8b"
trend_signals:
  - cryptographic crawler authentication
  - fail-closed edge security
  - standards convergence
development_slug: cloudflare-web-bot-auth-accepts-rfc-9864-ed25519-identifier-in-jwk-signer-and-ve
players:
  - "cloudflare"
protocols:
  - "web-bot-auth"
backfilled: false
---

## Summary

Cloudflare updated the Web Bot Auth reference library to accept JSON Web Keys (JWKs) using the alg identifier "Ed25519" in signerFromJWK and verifierFromJWK functions. Previously, the library rejected these keys, causing incompatibilities with Node.js crypto.subtle.exportKey output. In accordance with [RFC 9864 Section 2.2](https://www.rfc-editor.org/info/rfc9864/#section-2.2), which registers "Ed25519" and deprecates "EdDSA", the implementation now supports both identifiers.

## Key facts

- Cloudflare updated signerFromJWK and verifierFromJWK in the Web Bot Auth repository to accept Ed25519 JWKs with alg: "Ed25519".
- Node's crypto.subtle.exportKey returns JWKs using alg: "Ed25519", which previously caused rejection by Web Bot Auth JWK parsing functions.
- [RFC 9864 Section 2.2](https://www.rfc-editor.org/info/rfc9864/#section-2.2) registers "Ed25519" and deprecates "EdDSA".
- The Web Bot Auth reference implementation now accepts both the "Ed25519" and "EdDSA" algorithm identifiers.
- The change resolves pull request #201 and relates to issue #168.

## Insight

Cryptographic authentication across modern runtimes requires verifier libraries to tolerate both legacy JOSE registrations and newer RFC algorithm identifiers to prevent ecosystem fragmentation between standard Node.js crypto outputs and verification gateways.

## Implication

Developers building bot signing and verification services in Node.js can use standard WebCrypto exports directly without manual JSON Web Key parameter workarounds or runtime validation failures.

## Why it matters

Cryptographic bot verification cannot succeed if legitimate crawlers are rejected at the edge due to mismatched JWK metadata specifications across different language runtimes and evolving IETF standards.

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/201)
- Evidence ID: `web-bot-auth-repo--a5b3da832249fc8b`
