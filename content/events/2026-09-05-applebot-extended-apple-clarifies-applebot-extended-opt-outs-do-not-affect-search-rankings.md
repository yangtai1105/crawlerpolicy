---
schema_version: 2
slug: apple-clarifies-applebot-extended-opt-outs-do-not-affect-search-rankings
title: "Apple Clarifies Applebot-Extended Opt-Outs Do Not Affect Search Rankings"
source: applebot-extended
source_tier: primary
primary_track: crawler-controls
tracks:
  - crawler-controls
  - search-discovery
actors:
  - "Apple"
event_date: 2026-09-05T11:40:15.257245+00:00
published_at: 2026-09-05T11:40:15.257245+00:00
detected_at: 2026-09-05T11:40:15.257245+00:00
source_url: "https://support.apple.com/en-us/119829"
change_kind: material
importance: 0.68
confidence: high
evidence_ids:
  - "applebot-extended--916e5e8faa090c38"
---

## Development

Apple updated its [Applebot support documentation](https://support.apple.com/en-us/119829) to confirm that website rules applied to Applebot-Extended are not factored into Apple Search ranking. The update provides explicit assurance that disallowing the AI training crawler in robots.txt will not impact organic visibility across Spotlight, Siri, and Safari.

## Why it matters

As platforms expand generative AI features, web publishers frequently worry that opting out of model training may invisibly penalize their search distribution. Apple's documented commitment ensures crawler governance decisions remain strictly partitioned from search ranking.

## Trend impact

- ai-search-ranking-decoupling
- crawler-opt-out-safeguards

## Evidence

- [Primary source](https://support.apple.com/en-us/119829)
- Evidence ID: `applebot-extended--916e5e8faa090c38`

<details><summary>View raw diff</summary>

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
