---
schema_version: 1
slug: ietf-webbotauth-wg-ietf-web-bot-auth-wg-sees-revision-of-registry-and-signature-agent-card-draft
title: "IETF Web Bot Auth WG Sees Revision of Registry and Signature Agent Card Draft"
source: ietf-webbotauth-wg
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - identity-authorization
actors:
  - "IETF Web Bot Auth Working Group"
subject: both
event_date: 2026-10-27T14:01:01.414035+00:00
published_at: 2026-10-27T14:01:01.414035+00:00
detected_at: 2026-10-27T14:01:01.414035+00:00
source_urls:
  - "https://datatracker.ietf.org/group/webbotauth/"
change_kind: material
importance: 0.45
confidence: high
evidence_ids:
  - "ietf-webbotauth-wg--585a35def49ea164"
trend_signals:
  - Bot authentication registry standardization
  - Agent card specification development
development_slug: ietf-web-bot-auth-wg-sees-revision-of-registry-and-signature-agent-card-draft
protocols:
  - "web-bot-auth"
backfilled: false
---

## Summary

An updated Internet-Draft, draft-meunier-webbotauth-registry-04, has been published under the IETF Web Bot Auth Working Group tracker. The draft, titled "Registry and Signature Agent card for Web bot auth," advances identity registry specifications following its previous version in June 2026. The 26-page document remains an active individual submission related to the working group's broader authentication framework.

## Key facts

- On October 27, 2026, draft-meunier-webbotauth-registry-04 was published to the IETF Web Bot Auth Working Group repository.
- The updated draft is titled "Registry and Signature Agent card for Web bot auth" and spans 26 pages.
- The new revision replaces draft-meunier-webbotauth-registry-03, which was dated June 26, 2026.
- The document is listed as a related Internet-Draft with the status "I-D Exists" alongside active WG document draft-ietf-webbotauth-httpsig-protocol-00.

## Insight

Alongside the core HTTP Message Signatures protocol and IP verification proposals, the working group continues refining metadata and registry discovery mechanisms (the "Signature Agent card") required to map cryptographic signatures back to verified bot and agent operators.

## Implication

Implementers and web servers evaluating bot authentication architectures will have an updated reference for how automated agents register identities and publish signature metadata across directories.

## Why it matters

Cryptographic authentication relies not just on signature headers, but on dependable, standardized discovery mechanisms and registries so publishers can reliably verify which entity signed a request.

## Evidence

- [Primary source](https://datatracker.ietf.org/group/webbotauth/)
- Evidence ID: `ietf-webbotauth-wg--585a35def49ea164`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -44,9 +44,10 @@
 New
 I-D Exists
 26 pages
-draft-meunier-webbotauth-registry-03
+draft-meunier-webbotauth-registry-04
 Registry and Signature Agent card for Web bot auth
-2026-06-26
+2026-10-27
+New
 I-D Exists
 5 pages
 draft-popov-webbotauth-semantic-anchor-00
```

</details>
