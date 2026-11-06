---
schema_version: 1
slug: web-bot-auth-repo-cloudflare-web-bot-auth-corrects-rsassa-pkcs1-v1-5-signature-algorithm-parameter
title: "Cloudflare Web Bot Auth Corrects RSASSA-PKCS1-v1_5 Signature Algorithm Parameter Serialization"
source: web-bot-auth-repo
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - platform-ecosystem
actors:
  - "Cloudflare"
  - "Web Bot Auth"
subject: crawler
event_date: 2026-11-05T18:03:38+00:00
published_at: 2026-11-05T18:03:38+00:00
detected_at: 2026-11-06T15:41:50.881618+00:00
source_urls:
  - "https://github.com/cloudflare/web-bot-auth/pull/184"
change_kind: material
importance: 0.48
confidence: high
evidence_ids:
  - "web-bot-auth-repo--478630190caac379"
trend_signals:
  - strict RFC 9421 HTTP Message Signatures compliance
  - cryptographic crawler identity verification
development_slug: cloudflare-web-bot-auth-corrects-rsassa-pkcs1-v1-5-signature-algorithm-parameter
players:
  - "cloudflare"
backfilled: false
---

## Summary

Cloudflare's Web Bot Auth reference library patched a bug where the RSA signing algorithm variant RsaV1_5Sha256 improperly serialized its algorithm identifier as rsa-pss-sha512 in signature headers. Because message signers generated an incorrect alg parameter in Signature-Input headers, verifiers either rejected the signature outright due to key mismatch checks or failed verification when attempting to process the signature using RSASSA-PSS with SHA-512. The fix aligns the Display implementation with the RFC 9421 identifier rsa-v1_5-sha256 and adds round-trip parsing tests.

## Key facts

- The Algorithm Display trait implementation previously rendered rsa-pss-sha512 for RsaV1_5Sha256 in keyring.rs.
- MessageSigner::generate_signature_headers_content uses the Display output to populate the alg parameter in RFC 9421 Signature-Input headers.
- The mislabeling caused verifiers checking alg against the key to reject requests, and verifiers inferring the algorithm from the alg header to fail verification by expecting RSASSA-PSS with SHA-512.
- The issue affected custom GenerateSignature implementations such as YubiKey, cloud KMS, or web3 wallets, while the built-in [u8] signer only implements ed25519.
- The alg parser already mapped rsa-v1_5-sha256 to RsaV1_5Sha256, but serialization did not match until PR #184 updated keyring.rs to display rsa-v1_5-sha256.

## Insight

Cryptographic crawler authentication protocols are vulnerable to subtle string serialization mismatches in reference libraries, where an incorrect parameter label turns an otherwise valid cryptographic signature into an immediate verification failure.

## Implication

Developers deploying custom signing backends using RSA PKCS#1 v1.5 with SHA-256—such as hardware security keys or cloud key management services—can now successfully authenticate against RFC 9421 verifiers without facing deterministic signature rejections.

## Why it matters

As automated crawlers and platform agents shift toward cryptographic header signatures instead of IP whitelisting or static user-agent tokens, exact cross-implementation parity on RFC 9421 algorithm identifiers is required to avoid widespread false-positive bot blocks.

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/184)
- Evidence ID: `web-bot-auth-repo--478630190caac379`
