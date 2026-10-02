---
schema_version: 2
slug: rsl-1-0-relaxes-mime-type-requirement-in-favor-of-xml-namespace-identification
title: "RSL 1.0 Relaxes MIME Type Requirement in Favor of XML Namespace Identification"
source: rsl-standard
source_tier: primary
primary_track: standards-protocols
tracks:
  - standards-protocols
  - crawler-controls
  - licensing-monetization
actors:
  - "RSL Technical Steering Committee"
event_date: 2026-10-02T14:29:07.997977+00:00
published_at: 2026-10-02T14:29:07.997977+00:00
detected_at: 2026-10-02T14:29:07.997977+00:00
source_url: "https://rslstandard.org/rsl"
change_kind: material
importance: 0.45
confidence: high
evidence_ids:
  - "rsl-standard--38881d1c86e34d60"
---

## Development

The RSL Technical Steering Committee updated the Really Simple Licensing (RSL) 1.0 specification to downgrade the HTTP media type serving rule from MUST to SHOULD. Conforming implementations must now identify RSL documents by their XML namespace rather than media type alone and are prohibited from rejecting valid documents that have missing or different MIME types.

## Why it matters

Strict MIME-type requirements frequently cause machine-readable licensing declarations to fail in production environments; decoupling RSL discovery from rigid HTTP Content-Type headers improves the real-world interoperability of automated licensing signals.

## Trend impact

- protocol error-tolerance
- declarative licensing parsing

## Evidence

- [Primary source](https://rslstandard.org/rsl)
- Evidence ID: `rsl-standard--38881d1c86e34d60`

<details><summary>View raw diff</summary>

```diff
--- prev
+++ curr
@@ -290,7 +290,8 @@
 rsl
 >
 The media type associated with RSL documents is:
-RSL documents MUST be served with this media type when transmitted over HTTP or other Internet protocols.
+RSL documents SHOULD be served with this media type when transmitted over HTTP or other Internet protocols that support media types.
+Implementations MUST identify RSL documents by their XML namespace and MUST NOT rely solely on the media type. An implementation MUST NOT reject an otherwise valid RSL document solely because it is served with a different or missing media type.
 3. RSL Documents
 ​
 An RSL document, also called a
```

</details>
