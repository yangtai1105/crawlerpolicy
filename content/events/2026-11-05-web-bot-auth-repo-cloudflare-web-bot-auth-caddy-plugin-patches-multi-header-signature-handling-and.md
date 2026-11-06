---
schema_version: 2
slug: cloudflare-web-bot-auth-caddy-plugin-patches-multi-header-signature-handling-and
title: "Cloudflare Web Bot Auth Caddy Plugin Patches Multi-Header Signature Handling and Documents Upstream Parsing Bug"
source: web-bot-auth-repo
source_tier: primary
primary_track: standards-protocols
tracks:
  - standards-protocols
  - access-controls
  - platform-ecosystem
actors:
  - "Cloudflare"
event_date: 2026-11-05T23:33:07+00:00
published_at: 2026-11-05T23:33:07+00:00
detected_at: 2026-11-06T15:41:50.881618+00:00
source_url: "https://github.com/cloudflare/web-bot-auth/pull/185"
change_kind: material
importance: 0.52
confidence: high
evidence_ids:
  - "web-bot-auth-repo--202719f2d0bba953"
---

## Development

Cloudflare updated its Web Bot Auth Caddy example plugin to handle multi-line HTTP signatures and work around upstream limitations in the Go HTTP message signature library. The update combines split Signature and Signature-Input field lines in place before validation, ensuring requests containing multiple signatures are not dropped. It also documents and adds test coverage for an upstream bug where dictionary members of the Signature-Agent header fail signature verification under draft-ietf-webbotauth-httpsig-protocol-00.

## Key facts

- The Caddy plugin's Validate function now merges multi-line Signature-Input and Signature headers into single lines before verification to comply with RFC 9110 Section 5.3.
- Upstream library httpsig-go v1.2.2 only reads the first line of Signature-Input and Signature fields (remitly-oss/httpsig-go#18), causing verification to fail with 'The signature for label \'sig2\' not found' when signatures were spread across separate lines.
- Under draft-ietf-webbotauth-httpsig-protocol-00 Section 5.2.1, signatures must cover the Signature-Agent member keyed to their label, but httpsig-go v1.2.2 ignores the key parameter and signs the entire field, causing 401 rejections for dictionary Signature-Agent headers.
- Cloudflare pinned httpsig-go v1.2.2 while adding a README 'Known Limitations' section and introducing a regression test designed to fail automatically once an updated dependency without the upstream fix is installed.
- The hand-built signature base was verified against ed25519 test vectors in packages/web-bot-auth/test/test_data/web_bot_auth_architecture_v2.json.

## Why it matters

Cryptographic crawler authentication relies on absolute bit-level parity across heterogeneous libraries; small discrepancies in header parsing or component base construction result in immediate 401 Unauthorized rejections for valid bots.

## Trend impact

- Edge proxy normalization of RFC 9421 signatures
- Standardization testing for cryptographic crawler headers
- Maturity gaps in ecosystem HTTP signature libraries

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/185)
- Evidence ID: `web-bot-auth-repo--202719f2d0bba953`

