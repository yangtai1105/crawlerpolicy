---
schema_version: 1
slug: ietf-webbotauth-wg-ietf-web-bot-auth-working-group-receives-pace-capability-management-draft-for-ag
title: "IETF Web Bot Auth Working Group Receives PACE Capability Management Draft for Agents"
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
subject: agent
event_date: 2026-11-15T15:23:53.906711+00:00
published_at: 2026-11-15T15:23:53.906711+00:00
detected_at: 2026-11-15T15:23:53.906711+00:00
source_urls:
  - "https://datatracker.ietf.org/group/webbotauth/"
change_kind: material
importance: 0.52
confidence: high
evidence_ids:
  - "ietf-webbotauth-wg--b0e8266a52e25cf9"
trend_signals:
  - agent-governance-standardization
  - protocol-level-bot-management
development_slug: ietf-web-bot-auth-working-group-receives-pace-capability-management-draft-for-ag
players:
  - "ietf"
backfilled: false
---

## Summary

A new individual submission titled "PACE: Capability Management for Agents" has been introduced to the IETF Web Bot Auth Working Group. The 24-page Internet-Draft, designated draft-meunier-webbotauth-capacity-management-00, was published on November 15, 2026. This addition expands the working group's related drafts to 12 documents spanning cryptographic signatures, registries, and agent management.

## Key facts

- A new 24-page Internet-Draft titled "PACE: Capability Management for Agents" (draft-meunier-webbotauth-capacity-management-00) was published on November 15, 2026.
- The document was submitted as an individual contribution under the IETF Web Bot Auth (webbotauth) working group umbrella.
- The addition raises the count of related Internet-Drafts and RFCs tracked in the webbotauth repository from 11 to 12 hits.
- The working group continues to maintain one active working-group document, draft-ietf-webbotauth-httpsig-protocol-01 ("HTTP Message Signatures for automated traffic").

## Insight

The introduction of PACE signals a shift from purely authenticating bot identity and IP origin toward negotiating runtime capability and capacity limits directly between autonomous agents and origin servers.

## Implication

If pursued by the working group alongside the core HTTP Message Signatures specification, PACE could establish standard mechanisms for web hosts to dynamically communicate resource capacity, agent limits, and execution boundaries without relying entirely on static access rules.

## Why it matters

Authenticating that an incoming request belongs to an AI agent is only half the operational challenge for site operators; publishers also need standardized protocols to manage the scope, capability, and request capacity granted to those agents.

## Evidence

- [Primary source](https://datatracker.ietf.org/group/webbotauth/)
- Evidence ID: `ietf-webbotauth-wg--b0e8266a52e25cf9`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -19,7 +19,7 @@
 2026-10-29
 I-D Exists
 WG Document
-Related Internet-Drafts and RFCs (11 hits)
+Related Internet-Drafts and RFCs (12 hits)
 6 pages
 draft-farzdusa-webbot-datacollection-01
 Best Practices for Responsible Web Data Collection
@@ -39,6 +39,12 @@
 draft-kelley-webbotauth-sail-00
 SAIL: Source Address Identity List
 2026-10-22
+I-D Exists
+24 pages
+draft-meunier-webbotauth-capacity-management-00
+PACE: Capability Management for Agents
+2026-11-15
+New
 I-D Exists
 26 pages
 draft-meunier-webbotauth-registry-04
```

</details>
