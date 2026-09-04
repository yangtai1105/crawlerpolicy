---
schema_version: 1
slug: ietf-webbotauth-wg-ietf-web-bot-auth-wg-officially-adopts-http-message-signatures-protocol-draft
title: "IETF Web Bot Auth WG Officially Adopts HTTP Message Signatures Protocol Draft"
source: ietf-webbotauth-wg
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - crawler-controls
  - agentic-web
actors:
  - "IETF"
  - "IETF Web Bot Auth Working Group"
event_date: 2026-09-02T12:35:00.275423+00:00
published_at: 2026-09-02T12:35:00.275423+00:00
detected_at: 2026-09-02T12:35:00.275423+00:00
source_urls:
  - "https://datatracker.ietf.org/group/webbotauth/"
change_kind: material
importance: 0.76
confidence: high
evidence_ids:
  - "ietf-webbotauth-wg--72f735794900da14"
development_slug: ietf-web-bot-auth-wg-officially-adopts-http-message-signatures-protocol-draft
backfilled: false
---

## Summary

The IETF Web Bot Auth Working Group has formally adopted the core specification for cryptographically signing automated web requests. The individual submission was re-indexed as the working group document draft-ietf-webbotauth-httpsig-protocol-00 ('HTTP Message Signatures for automated traffic') on September 1, 2026. This marks the transition of the protocol from an individual draft into the working group's official standards track.

## Insight

Working group adoption signals formal consensus within the IETF that HTTP Message Signatures will serve as the baseline technical mechanism for verifying bot identity, moving the ecosystem beyond basic User-Agent heuristics and IP allowlists.

## Implication

Crawler operators, AI agent developers, and origin web servers will now have a centralized, standardized draft target to build and test automated traffic authentication mechanisms.

## Why it matters

As web publishers struggle with scraping volume and bot spoofing, a standardized cryptographic authentication protocol under active IETF development provides a path toward verifiable, accountable crawler identification at scale.

## Evidence

- [Primary source](https://datatracker.ietf.org/group/webbotauth/)
- Evidence ID: `ietf-webbotauth-wg--72f735794900da14`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -12,7 +12,15 @@
 Status
 IPR
 AD/Shepherd
-Related Internet-Drafts and RFCs (11 hits)
+Active Internet-Draft (1 hit)
+44 pages
+draft-ietf-webbotauth-httpsig-protocol-00
+HTTP Message Signatures for automated traffic
+2026-09-01
+New
+I-D Exists
+WG Document
+Related Internet-Drafts and RFCs (10 hits)
 6 pages
 draft-farzdusa-webbot-datacollection-00
 Best Practices for Responsible Web Data Collection
@@ -27,12 +35,6 @@
 draft-illyes-webbotauth-jafar-00
 A JSON-Based Format for Publishing IP Ranges of Automated HTTP Clients
 2026-04-21
-I-D Exists
-44 pages
-draft-meunier-webbotauth-httpsig-protocol-02
-HTTP Message Signatures for automated traffic
-2026-08-18
-New
 I-D Exists
 26 pages
 draft-meunier-webbotauth-registry-03
```

</details>
