---
schema_version: 1
slug: applebot-extended-apple-clarifies-applebot-extended-opt-outs-do-not-affect-search-rankings
title: "Apple Clarifies Applebot-Extended Opt-Outs Do Not Affect Search Rankings"
source: applebot-extended
source_tier: primary
status: verified
primary_track: crawler-controls
tracks:
  - crawler-controls
  - search-discovery
actors:
  - "Apple"
event_date: 2026-09-05T11:40:15.257245+00:00
published_at: 2026-09-05T11:40:15.257245+00:00
detected_at: 2026-09-05T11:40:15.257245+00:00
source_urls:
  - "https://support.apple.com/en-us/119829"
change_kind: material
importance: 0.68
confidence: high
evidence_ids:
  - "applebot-extended--916e5e8faa090c38"
trend_signals:
  - ai-search-ranking-decoupling
  - crawler-opt-out-safeguards
development_slug: apple-clarifies-applebot-extended-opt-outs-do-not-affect-search-rankings
backfilled: false
---

## Summary

Apple updated its [Applebot support documentation](https://support.apple.com/en-us/119829) to confirm that website rules applied to Applebot-Extended are not factored into Apple Search ranking. The update provides explicit assurance that disallowing the AI training crawler in robots.txt will not impact organic visibility across Spotlight, Siri, and Safari.

## Insight

The addition formalizes an explicit policy boundary between AI model training opt-outs and core search indexing algorithms, countering concerns that withholding training data might degrade search discovery.

## Implication

Publishers and site operators can safely block foundation model training using User-agent: Applebot-Extended in their robots.txt files without risking their position or visibility in Apple Search results.

## Why it matters

As platforms expand generative AI features, web publishers frequently worry that opting out of model training may invisibly penalize their search distribution. Apple's documented commitment ensures crawler governance decisions remain strictly partitioned from search ranking.

## Evidence

- [Primary source](https://support.apple.com/en-us/119829)
- Evidence ID: `applebot-extended--916e5e8faa090c38`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -103,7 +103,7 @@
 Webpage design characteristics
 Search results may use the factors above with no (pre-determined) importance of ranking. Users of Search are subject to the privacy policy in
 Siri Suggestions, Search & Privacy
-.
+. Site rules for Applebot-Extended are not considered in ranking for Search.
 If you have questions or concerns, please contact us at
 applebot@apple.com
 .
@@ -111,4 +111,4 @@
 Contact the vendor
 for additional information.
 Published Date:
-June 08, 2026
+September 04, 2026
```

</details>
