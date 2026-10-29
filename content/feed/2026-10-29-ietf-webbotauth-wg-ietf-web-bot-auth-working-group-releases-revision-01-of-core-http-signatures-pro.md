---
schema_version: 1
slug: ietf-webbotauth-wg-ietf-web-bot-auth-working-group-releases-revision-01-of-core-http-signatures-pro
title: "IETF Web Bot Auth Working Group Releases Revision -01 of Core HTTP Signatures Protocol Draft"
source: ietf-webbotauth-wg
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - identity-authorization
  - platform-ecosystem
actors:
  - "IETF"
  - "IETF Web Bot Auth Working Group"
subject: both
event_date: 2026-10-29T14:58:01.749807+00:00
published_at: 2026-10-29T14:58:01.749807+00:00
detected_at: 2026-10-29T14:58:01.749807+00:00
source_urls:
  - "https://datatracker.ietf.org/group/webbotauth/"
change_kind: material
importance: 0.60
confidence: high
evidence_ids:
  - "ietf-webbotauth-wg--79c2f8436380dea1"
trend_signals:
  - IETF standardization of cryptographic bot authentication
  - Formalization of automated traffic verification protocols
development_slug: ietf-web-bot-auth-working-group-releases-revision-01-of-core-http-signatures-pro
players:
  - "ietf"
backfilled: false
---

## Summary

The IETF Web Bot Auth Working Group has published `draft-ietf-webbotauth-httpsig-protocol-01`, titled "HTTP Message Signatures for automated traffic". This represents the working group's first official document revision since formally adopting the HTTP message signatures draft in September 2026. The 44-page specification remains the working group's sole active adopted Internet-Draft.

## Key facts

- The IETF Web Bot Auth Working Group published draft-ietf-webbotauth-httpsig-protocol-01 on October 29, 2026.
- The document is titled 'HTTP Message Signatures for automated traffic' and comprises 44 pages.
- This is the first revision to the working group's core specification since draft-ietf-webbotauth-httpsig-protocol-00 was published on September 1, 2026.
- The draft remains the only active adopted Working Group Document in the webbotauth charter, alongside 10 related individual submissions.

## Insight

Active maintenance of the primary protocol draft indicates the working group is iterating on its cryptographic core while surrounding individual contributions explore supporting mechanisms like registries, IP discovery, and agent identity cards.

## Implication

Protocol implementers and bot operators tracking automated traffic authentication must evaluate the technical refinements in revision -01 as the working group codifies how web bots sign HTTP requests.

## Why it matters

HTTP Message Signatures represent the premier standards-track effort to replace brittle IP whitelists and spoofable User-Agent strings with cryptographic accountability for bots and crawlers across the web.

## Evidence

- [Primary source](https://datatracker.ietf.org/group/webbotauth/)
- Evidence ID: `ietf-webbotauth-wg--79c2f8436380dea1`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -14,9 +14,10 @@
 AD/Shepherd
 Active Internet-Draft (1 hit)
 44 pages
-draft-ietf-webbotauth-httpsig-protocol-00
+draft-ietf-webbotauth-httpsig-protocol-01
 HTTP Message Signatures for automated traffic
-2026-09-01
+2026-10-29
+New
 I-D Exists
 WG Document
 Related Internet-Drafts and RFCs (10 hits)
```

</details>
