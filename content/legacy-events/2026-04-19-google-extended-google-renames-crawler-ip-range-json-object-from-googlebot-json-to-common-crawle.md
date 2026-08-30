---
slug: google-renames-crawler-ip-range-json-object-from-googlebot-json-to-common-crawle
title: "Google renames crawler IP range JSON object from `googlebot.json` to `common-crawlers.json`"
source: google-extended
pillar: crawler
detected_at: 2026-04-19T21:35:19.602033+00:00
source_url: "https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers"
change_kind: material
importance: 0.70
---

## What changed

The [Google common crawlers reference page](https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers) changed the named IP-range data source for common crawlers from `googlebot.json` to `common-crawlers.json`. The page's last-updated date was also bumped from 2025-04-25 to 2026-02-11.

## Implication

Operators and tools that fetch Google crawler IP allowlists by referencing the `googlebot.json` object specifically for common crawlers should update to point to `common-crawlers.json` instead. This suggests Google has split or renamed the published IP-range JSON feed, and firewall rules, bots-detection scripts, or CDN configurations relying on the old filename may no longer be accurate for verifying common crawler IPs.

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
