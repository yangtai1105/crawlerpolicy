---
schema_version: 1
slug: ietf-webbotauth-wg-ietf-web-bot-auth-wg-receives-internet-draft-on-signed-agent-metadata-http-heade
title: "IETF Web Bot Auth WG Receives Internet-Draft on Signed-Agent-Metadata HTTP Header Field"
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
  - "Internet Engineering Task Force"
subject: both
event_date: 2026-11-03T15:51:57.033950+00:00
published_at: 2026-11-03T15:51:57.033950+00:00
detected_at: 2026-11-03T15:51:57.033950+00:00
source_urls:
  - "https://datatracker.ietf.org/group/webbotauth/"
change_kind: material
importance: 0.48
confidence: high
evidence_ids:
  - "ietf-webbotauth-wg--73b525a0d33d1f6c"
trend_signals:
  - standardization of cryptographically signed agent and bot request headers
  - in-band metadata delivery for automated web clients
development_slug: ietf-web-bot-auth-wg-receives-internet-draft-on-signed-agent-metadata-http-heade
backfilled: false
---

## Summary

A new individual Internet-Draft titled "The Signed-Agent-Metadata HTTP Header Field for Web Bot Auth" was submitted to the IETF Web Bot Auth Working Group on November 2, 2026. Authored under the draft name draft-vilgalys-webbotauth-signed-agent-metadata-00, the 15-page specification introduces a dedicated HTTP header for signed agent metadata. The submission increases the working group's list of related Internet-Drafts and RFCs to 11.

## Key facts

- A new 15-page Internet-Draft titled "The Signed-Agent-Metadata HTTP Header Field for Web Bot Auth" (draft-vilgalys-webbotauth-signed-agent-metadata-00) was published on 2026-11-02.
- The draft entered the IETF Web Bot Auth datatracker repository with status "I-D Exists" as a new related submission.
- The addition expands the IETF Web Bot Auth Working Group's tracked related Internet-Drafts and RFCs from 10 to 11 hits.
- The document joins an active working group roster that includes the adopted protocol draft-ietf-webbotauth-httpsig-protocol-01 alongside drafts for crawler IP ranges, agent cards, and data collection best practices.

## Insight

While the core working group effort standardizes cryptographic request signing, peripheral draft proposals are defining specialized HTTP headers to transmit authenticated identity, provenance, and capability metadata in-band with automated client requests.

## Implication

If standardized and adopted, origin servers and edge proxies will be able to parse and cryptographically verify structured agent metadata directly from request headers to make granular access-control and rate-limiting decisions.

## Why it matters

Moving beyond binary bot blocking requires automated clients to present verifiable claims about their identity and intent; standardizing a signed agent metadata header offers an interoperable mechanism to deliver trusted agent declarations directly to web servers.

## Evidence

- [Primary source](https://datatracker.ietf.org/group/webbotauth/)
- Evidence ID: `ietf-webbotauth-wg--73b525a0d33d1f6c`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -20,7 +20,7 @@
 New
 I-D Exists
 WG Document
-Related Internet-Drafts and RFCs (10 hits)
+Related Internet-Drafts and RFCs (11 hits)
 6 pages
 draft-farzdusa-webbot-datacollection-01
 Best Practices for Responsible Web Data Collection
@@ -65,6 +65,12 @@
 Hosted Key Directories for Web Bot Auth
 2026-07-19
 I-D Exists
+15 pages
+draft-vilgalys-webbotauth-signed-agent-metadata-00
+The Signed-Agent-Metadata HTTP Header Field for Web Bot Auth
+2026-11-02
+New
+I-D Exists
 14 pages
 draft-meunier-http-message-signatures-directory-05
 HTTP Message Signatures Directory
```

</details>
