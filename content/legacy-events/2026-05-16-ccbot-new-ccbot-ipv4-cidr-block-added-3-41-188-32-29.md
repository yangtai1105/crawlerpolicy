---
slug: new-ccbot-ipv4-cidr-block-added-3-41-188-32-29
title: "New CCBot IPv4 CIDR block added: 3.41.188.32/29"
source: ccbot
pillar: crawler
detected_at: 2026-05-16T09:41:05.148791+00:00
source_url: "https://commoncrawl.org/faq"
change_kind: material
importance: 0.55
---

## What changed

A new IPv4 CIDR block `3.41.188.32/29` has been appended to the [CCBot IP range list](https://commoncrawl.org/faq) under the "What is the IP range of the Common Crawl CCBot?" section. The date stamp on the block list still reads 2024-11-29; the canonical machine-readable source remains at `https://index.commoncrawl.org/ccbot.json`.

## Implication

Webmasters and firewall operators who allowlist or blocklist CCBot by IP must add `3.41.188.32/29` (8 addresses) to their rule sets; requests from this range will now originate from the real CCBot. Operators relying solely on the JSON endpoint at `https://index.commoncrawl.org/ccbot.json` should already receive this update if that file has been refreshed accordingly.

## Raw diff

<details><summary>View diff</summary>

```diff
--- prev
+++ curr
@@ -156,6 +156,7 @@
 18.97.14.80/29
 18.97.14.88/30
 98.85.178.216/32
+3.41.188.32/29
 This information is also provided as JSON at
 https://index.commoncrawl.org/ccbot.json
 .
```

</details>
