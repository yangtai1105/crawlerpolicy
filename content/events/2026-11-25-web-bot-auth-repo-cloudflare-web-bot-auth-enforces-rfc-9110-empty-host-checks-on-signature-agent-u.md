---
schema_version: 2
slug: cloudflare-web-bot-auth-enforces-rfc-9110-empty-host-checks-on-signature-agent-u
title: "Cloudflare Web Bot Auth Enforces RFC 9110 Empty-Host Checks on Signature-Agent URIs"
source: web-bot-auth-repo
source_tier: primary
primary_track: standards-protocols
tracks:
  - standards-protocols
  - platform-ecosystem
  - identity-authorization
actors:
  - "Cloudflare"
  - "IETF"
event_date: 2026-11-25T08:55:52+00:00
published_at: 2026-11-25T08:55:52+00:00
detected_at: 2026-11-25T18:27:10.486917+00:00
source_url: "https://github.com/cloudflare/web-bot-auth/pull/163"
change_kind: material
importance: 0.47
confidence: high
evidence_ids:
  - "web-bot-auth-repo--8ebd5e7abafc2601"
---

## Development

Cloudflare updated its Rust and TypeScript Web Bot Auth reference parsers to reject Signature-Agent URI values that lack an explicit host identifier, resolving an issue where the WHATWG URL parser silently coerced malformed URIs into valid fetch targets. The fix enforces RFC 9110 Section 4.2.2 and draft-ietf-webbotauth-httpsig-protocol-01 Section 5.2.1 by verifying that the raw header string begins with an explicit https:// scheme followed immediately by a host. The change also adds comprehensive test vectors across both implementations covering plain HTTP member rejections, parameter-carrying member handling, and case-insensitive scheme matching.

## Key facts

- Draft-ietf-webbotauth-httpsig-protocol-01 Section 5.2.1 requires each Signature-Agent member value to be an absolute URI whose scheme MUST be https.
- RFC 9110 Section 4.2.2 mandates that senders MUST NOT generate an https URI with an empty host identifier and recipients MUST reject it as invalid.
- The WHATWG URL parser previously coerced malformed URIs like https:///x.test, https:x.test, and https:\x.test into https://x.test/, causing verifiers to fetch URLs differing from the raw signer value.
- Both Rust and TypeScript parsers now check the raw value directly, requiring it to start with https:// followed by a host or raise 'Signature-Agent must name a host'.
- Test coverage added across packages/web-bot-auth (62 tests passed) and crates/web-bot-auth (57 tests passed) validates 17 Signature-Agent header variations across both languages.
- The update confirms that verify() does not call the resolver for http members, ignores http members carrying parameters, and accepts upper-case HTTPS:// schemes.

## Why it matters

Edge authentication protocols fail securely only when signing and verifying libraries share identical parsing semantics; permitting edge parsers to guess or normalize malformed identity URIs creates semantic ambiguities and potential spoofing vectors.

## Trend impact

- parser-differential hardening
- strict RFC URI syntax enforcement
- cryptographic crawler identity verification

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/163)
- Evidence ID: `web-bot-auth-repo--8ebd5e7abafc2601`

