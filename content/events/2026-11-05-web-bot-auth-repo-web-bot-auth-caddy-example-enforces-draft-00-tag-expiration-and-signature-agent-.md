---
schema_version: 2
slug: web-bot-auth-caddy-example-enforces-draft-00-tag-expiration-and-signature-agent-
title: "Web Bot Auth Caddy Example Enforces draft-00 Tag, Expiration, and Signature-Agent Coverage"
source: web-bot-auth-repo
source_tier: primary
primary_track: standards-protocols
tracks:
  - standards-protocols
  - identity-authorization
  - access-controls
actors:
  - "Cloudflare"
  - "IETF"
event_date: 2026-11-05T17:58:59+00:00
published_at: 2026-11-05T17:58:59+00:00
detected_at: 2026-11-06T15:41:50.881618+00:00
source_url: "https://github.com/cloudflare/web-bot-auth/pull/167"
change_kind: material
importance: 0.53
confidence: high
evidence_ids:
  - "web-bot-auth-repo--e806f56c6990d66a"
---

## Development

Cloudflare's Web Bot Auth repository merged pull request #167, updating its Go Caddy reference implementation to enforce rules from draft-ietf-webbotauth-httpsig-protocol-00. The verifier now requires signatures to be explicitly tagged web-bot-auth and mandates the presence of created, expires, keyid, and tag parameters. In addition, when a request includes a Signature-Agent header, the signature must cryptographically cover its corresponding member dictionary or legacy string field.

## Key facts

- Pull request #167 updates the Go Caddy example to implement verification rules from draft-ietf-webbotauth-httpsig-protocol-00 Sections 5.2, 5.2.1, 5.2.2, and 5.4.
- The verifier now verifies only signatures tagged 'web-bot-auth' and rejects signatures with any other tag or missing a tag.
- Signatures must include 'created', 'expires', 'keyid', and 'tag' parameters; requests omitting 'expires' now fail with a 401 response.
- When a request contains a 'Signature-Agent' header, the signature must cover the member keyed to its own label, while a legacy String 'Signature-Agent' is counted as a single member keyed to the label covering the entire field.
- The implementation rejects requests whose 'Signature-Agent' value is neither a Dictionary nor a String, or where a Dictionary is covered as a whole field.
- End-to-end testing was verified against Caddy v2.11.7 with 101 requests plus five dedicated 'Signature-Agent' coverage validation scenarios.

## Why it matters

As the IETF draft solidifies, edge gateways and verification plugins are moving from loose signature validation to strict fail-closed enforcement, meaning minor signature parameter omissions will directly block legitimate automated access.

## Trend impact

- cryptographic-bot-verification
- strict-identity-binding

## Evidence

- [Primary source](https://github.com/cloudflare/web-bot-auth/pull/167)
- Evidence ID: `web-bot-auth-repo--e806f56c6990d66a`

