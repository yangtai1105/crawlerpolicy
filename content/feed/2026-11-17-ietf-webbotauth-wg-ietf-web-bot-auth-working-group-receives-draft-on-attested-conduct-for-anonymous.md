---
schema_version: 1
slug: ietf-webbotauth-wg-ietf-web-bot-auth-working-group-receives-draft-on-attested-conduct-for-anonymous
title: "IETF Web Bot Auth Working Group Receives Draft on Attested Conduct for Anonymous Data Collection"
source: ietf-webbotauth-wg
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - access-controls
  - identity-authorization
actors:
  - "IETF"
  - "IETF Web Bot Auth Working Group"
subject: crawler
event_date: 2026-11-17T17:24:29.231942+00:00
published_at: 2026-11-17T17:24:29.231942+00:00
detected_at: 2026-11-17T17:24:29.231942+00:00
source_urls:
  - "https://datatracker.ietf.org/group/webbotauth/"
change_kind: material
importance: 0.49
confidence: high
evidence_ids:
  - "ietf-webbotauth-wg--b23a210f6971e0dc"
trend_signals:
  - anonymous bot verification
  - tiered crawler attestation
  - responsible web data collection standards
development_slug: ietf-web-bot-auth-working-group-receives-draft-on-attested-conduct-for-anonymous
players:
  - "ietf"
backfilled: false
---

## Summary

A new individual Internet-Draft titled "Attested Conduct for Anonymous Web Data Collection: Use Cases, Requirements, and a Tiered Model" has been submitted to the IETF Web Bot Auth Working Group. Authored under the draft name draft-mckenna-webbotauth-collection-attestation-00, the 13-page document was published on November 16, 2026. The submission expands the group's active exploration of privacy-preserving crawler verification alongside its core cryptographic signature standards.

## Key facts

- A new 13-page Internet-Draft, draft-mckenna-webbotauth-collection-attestation-00, was published on November 16, 2026.
- The draft is titled "Attested Conduct for Anonymous Web Data Collection: Use Cases, Requirements, and a Tiered Model."
- The submission brings the total number of related Internet-Drafts and RFCs tracked under the IETF Web Bot Auth Working Group to 13.
- The proposal builds on the group's related work on bot behavior and privacy, which includes draft-rescorla-anonymous-webbotauth-01 and draft-farzdusa-webbot-datacollection-01.

## Insight

While initial crawler authentication efforts concentrated on non-repudiable entity identification via HTTP signatures, this proposal introduces a framework for anonymous data collection that relies on attested conduct and tiered compliance instead of exposing crawler identity.

## Implication

If pursued by the working group, site operators and automated scrapers may gain a standardized protocol to negotiate data collection allowances anonymously, decoupling behavioral compliance and rate limiting from full corporate identity disclosure.

## Why it matters

Not all automated crawlers can or will identify their corporate operators due to competitive or privacy concerns; establishing an attested, tiered conduct model provides an interoperable middle ground between intrusive identity tracking and indiscriminate bot blocking.

## Evidence

- [Primary source](https://datatracker.ietf.org/group/webbotauth/)
- Evidence ID: `ietf-webbotauth-wg--b23a210f6971e0dc`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -19,7 +19,7 @@
 2026-10-29
 I-D Exists
 WG Document
-Related Internet-Drafts and RFCs (12 hits)
+Related Internet-Drafts and RFCs (13 hits)
 6 pages
 draft-farzdusa-webbot-datacollection-01
 Best Practices for Responsible Web Data Collection
@@ -39,6 +39,12 @@
 draft-kelley-webbotauth-sail-00
 SAIL: Source Address Identity List
 2026-10-22
+I-D Exists
+13 pages
+draft-mckenna-webbotauth-collection-attestation-00
+Attested Conduct for Anonymous Web Data Collection: Use Cases, Requirements, and a Tiered Model
+2026-11-16
+New
 I-D Exists
 24 pages
 draft-meunier-webbotauth-capacity-management-00
@@ -70,7 +76,6 @@
 draft-vilgalys-webbotauth-signed-agent-metadata-00
 The Signed-Agent-Metadata HTTP Header Field for Web Bot Auth
 2026-11-02
-New
 I-D Exists
 14 pages
 draft-meunier-http-message-signatures-directory-05
```

</details>
