---
schema_version: 1
slug: ietf-webbotauth-wg-ietf-web-bot-auth-wg-receives-new-sail-internet-draft-for-source-address-identit
title: "IETF Web Bot Auth WG Receives New SAIL Internet-Draft for Source Address Identity Lists"
source: ietf-webbotauth-wg
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - identity-authorization
  - access-controls
actors:
  - "IETF"
  - "IETF Web Bot Auth Working Group"
subject: crawler
event_date: 2026-10-23T13:06:31.696700+00:00
published_at: 2026-10-23T13:06:31.696700+00:00
detected_at: 2026-10-23T13:06:31.696700+00:00
source_urls:
  - "https://datatracker.ietf.org/group/webbotauth/"
change_kind: material
importance: 0.50
confidence: high
evidence_ids:
  - "ietf-webbotauth-wg--590751b5f4db81f6"
trend_signals:
  - crawler-ip-identity-standardization
  - multi-proposal-bot-verification
development_slug: ietf-web-bot-auth-wg-receives-new-sail-internet-draft-for-source-address-identit
players:
  - "ietf"
backfilled: false
---

## Summary

A new 25-page Internet-Draft titled 'SAIL: Source Address Identity List' (draft-kelley-webbotauth-sail-00) has been submitted to the IETF Web Bot Auth Working Group tracker. Dated October 22, 2026, the submission expands the working group's related documents from 9 to 10. The draft arrives alongside other recent proposals addressing IP address verification and crawler publication formats.

## Key facts

- A new Internet-Draft titled 'SAIL: Source Address Identity List' (draft-kelley-webbotauth-sail-00) was published in the IETF Web Bot Auth Working Group tracker.
- The SAIL draft is 25 pages long, carries the status 'I-D Exists' and 'New', and is dated 2026-10-22.
- The addition increased the count of related Internet-Drafts and RFCs tracked under the Web Bot Auth WG from 9 to 10.
- The submission follows another IP-related proposal dated the same day, draft-illyes-webbotauth-jafar-01 ('A JSON-Based Format for Publishing IP Ranges of Automated HTTP Clients').

## Insight

The introduction of SAIL alongside draft-illyes-webbotauth-jafar indicates growing interest in standardizing network-level source address publication for bots, offering alternative or complementary mechanisms to cryptographic HTTP message signatures.

## Implication

Working group participants and web operators evaluating automated bot verification will need to assess competing or complementary network-layer identity proposals against application-layer signature architectures.

## Why it matters

While cryptographic HTTP signatures remain the primary adopted protocol, network-level IP and source address lists represent a lower-friction, immediate method for publishers to identify and verify automated traffic.

## Evidence

- [Primary source](https://datatracker.ietf.org/group/webbotauth/)
- Evidence ID: `ietf-webbotauth-wg--590751b5f4db81f6`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -19,7 +19,7 @@
 2026-09-01
 I-D Exists
 WG Document
-Related Internet-Drafts and RFCs (9 hits)
+Related Internet-Drafts and RFCs (10 hits)
 6 pages
 draft-farzdusa-webbot-datacollection-01
 Best Practices for Responsible Web Data Collection
@@ -34,6 +34,12 @@
 11 pages
 draft-illyes-webbotauth-jafar-01
 A JSON-Based Format for Publishing IP Ranges of Automated HTTP Clients
+2026-10-22
+New
+I-D Exists
+25 pages
+draft-kelley-webbotauth-sail-00
+SAIL: Source Address Identity List
 2026-10-22
 New
 I-D Exists
```

</details>
