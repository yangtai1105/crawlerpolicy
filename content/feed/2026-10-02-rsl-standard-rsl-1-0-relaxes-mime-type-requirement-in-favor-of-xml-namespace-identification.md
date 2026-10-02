---
schema_version: 1
slug: rsl-standard-rsl-1-0-relaxes-mime-type-requirement-in-favor-of-xml-namespace-identification
title: "RSL 1.0 Relaxes MIME Type Requirement in Favor of XML Namespace Identification"
source: rsl-standard
source_tier: primary
status: verified
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
source_urls:
  - "https://rslstandard.org/rsl"
change_kind: material
importance: 0.45
confidence: high
evidence_ids:
  - "rsl-standard--38881d1c86e34d60"
trend_signals:
  - protocol error-tolerance
  - declarative licensing parsing
development_slug: rsl-1-0-relaxes-mime-type-requirement-in-favor-of-xml-namespace-identification
backfilled: false
---

## Summary

The RSL Technical Steering Committee updated the Really Simple Licensing (RSL) 1.0 specification to downgrade the HTTP media type serving rule from MUST to SHOULD. Conforming implementations must now identify RSL documents by their XML namespace rather than media type alone and are prohibited from rejecting valid documents that have missing or different MIME types.

## Insight

By shifting document validity enforcement from HTTP transport headers to XML namespace inspection, the standard adopts the robustness principle to prevent crawler parsing failures caused by misconfigured web server Content-Type headers.

## Implication

Developers building RSL-compliant parsers and automated scrapers must update their ingestion pipelines to parse document namespaces rather than discarding files based on HTTP headers, while publishers face fewer ingestion rejections due to web server configuration errors.

## Why it matters

Strict MIME-type requirements frequently cause machine-readable licensing declarations to fail in production environments; decoupling RSL discovery from rigid HTTP Content-Type headers improves the real-world interoperability of automated licensing signals.

## Evidence

- [Primary source](https://rslstandard.org/rsl)
- Evidence ID: `rsl-standard--38881d1c86e34d60`

<details><summary>View observed change</summary>

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
