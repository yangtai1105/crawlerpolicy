---
slug: ip-range-json-source-renamed-from-googlebot-json-to-common-crawlers-json
title: "IP range JSON source renamed from googlebot.json to common-crawlers.json"
source: google-extended
pillar: crawler
detected_at: 2026-04-19T18:36:49.010383+00:00
source_url: https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers
change_kind: material
importance: 0.70
---

## What changed

The authoritative JSON object for common crawler IP ranges was renamed from `googlebot.json` to `common-crawlers.json`. The page's last-updated date also advanced from 2025-04-25 to 2026-02-11.

## Implication

Operators and tools that fetch or reference the `googlebot.json` endpoint to verify crawler IP ranges must update to `common-crawlers.json`. Using the old filename will likely result in missing or stale IP data, potentially breaking crawler-verification logic.

## Raw diff

<details><summary>View diff</summary>

```diff
--- prev
+++ curr
@@ -9,7 +9,7 @@
 technical properties
 of Google's crawlers also apply to the common crawlers.
 The common crawlers generally crawl from the IP ranges published in the
-googlebot.json
+common-crawlers.json
 object, and the reverse DNS mask
 of their hostname matches
 crawl-***-***-***-***.googlebot.com
@@ -296,4 +296,4 @@
 . For details, see the
 Google Developers Site Policies
 . Java is a registered trademark of Oracle and/or its affiliates.
-Last updated 2025-04-25 UTC.
+Last updated 2026-02-11 UTC.
```

</details>
