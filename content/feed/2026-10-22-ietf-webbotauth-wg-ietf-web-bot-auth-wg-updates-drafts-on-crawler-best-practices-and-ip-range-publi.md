---
schema_version: 1
slug: ietf-webbotauth-wg-ietf-web-bot-auth-wg-updates-drafts-on-crawler-best-practices-and-ip-range-publi
title: "IETF Web Bot Auth WG Updates Drafts on Crawler Best Practices and IP Range Publishing"
source: ietf-webbotauth-wg
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - identity-authorization
  - access-controls
actors:
  - "IETF Web Bot Auth Working Group"
subject: crawler
event_date: 2026-10-22T13:30:16.624196+00:00
published_at: 2026-10-22T13:30:16.624196+00:00
detected_at: 2026-10-22T13:30:16.624196+00:00
source_urls:
  - "https://datatracker.ietf.org/group/webbotauth/"
change_kind: material
importance: 0.50
confidence: high
evidence_ids:
  - "ietf-webbotauth-wg--c6dc433a924a1ecc"
trend_signals:
  - standardization of crawler IP disclosure formats
  - formalization of crawler behavioral best practices
development_slug: ietf-web-bot-auth-wg-updates-drafts-on-crawler-best-practices-and-ip-range-publi
backfilled: false
---

## Summary

Two individual Internet-Drafts related to the IETF Web Bot Auth Working Group have been updated to revision -01, preventing their impending expiration. Author Illyes published new versions of 'Crawler best practices' (draft-illyes-webbotauth-cbcp-01) and 'A JSON-Based Format for Publishing IP Ranges of Automated HTTP Clients' (draft-illyes-webbotauth-jafar-01). The revisions keep proposals for standardized crawler behavioral guidance and machine-readable IP range publication active within the working group's purview.

## Key facts

- On October 22, 2026, 'draft-illyes-webbotauth-cbcp-01' ('Crawler best practices') was published, replacing revision -00 dated April 21, 2026.
- The 'Crawler best practices' draft expanded by one page, growing from 7 pages to 8 pages.
- On October 22, 2026, 'draft-illyes-webbotauth-jafar-01' ('A JSON-Based Format for Publishing IP Ranges of Automated HTTP Clients') was published at 11 pages, replacing the April 21, 2026 revision -00.
- Both drafts had previously been marked as 'Expires soon' on the IETF Web Bot Auth Working Group document tracker before the revisions were posted.
- The drafts remain individual submissions categorized under 'Related Internet-Drafts and RFCs' within the Web Bot Auth Working Group tracker.

## Insight

Alongside cryptographic verification methods like HTTP Message Signatures, IETF contributors are keeping complementary operational tracks alive—specifically standardized JSON formats for IP disclosure and behavioral best practices—ensuring identity and network verification can evolve in parallel.

## Implication

Web platforms, bot operators, and edge security vendors tracking machine access standards will see continued technical work on standardized formats for identifying crawlers via IP publication and defining baseline crawler conduct.

## Why it matters

Cryptographic authentication alone does not solve all crawler identification challenges; establishing standardized data formats for crawler IP ranges and formalized behavioral baselines gives publishers immediate, structured mechanisms to verify and manage automated traffic.

## Evidence

- [Primary source](https://datatracker.ietf.org/group/webbotauth/)
- Evidence ID: `ietf-webbotauth-wg--c6dc433a924a1ecc`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -25,17 +25,17 @@
 Best Practices for Responsible Web Data Collection
 2026-09-23
 I-D Exists
-7 pages
-draft-illyes-webbotauth-cbcp-00
+8 pages
+draft-illyes-webbotauth-cbcp-01
 Crawler best practices
-2026-04-21
-Expires soon
+2026-10-22
+New
 I-D Exists
 11 pages
-draft-illyes-webbotauth-jafar-00
+draft-illyes-webbotauth-jafar-01
 A JSON-Based Format for Publishing IP Ranges of Automated HTTP Clients
-2026-04-21
-Expires soon
+2026-10-22
+New
 I-D Exists
 26 pages
 draft-meunier-webbotauth-registry-03
```

</details>
