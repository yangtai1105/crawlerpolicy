---
slug: perplexity-bots-doc-adds-llms-txt-documentation-index-pointer
title: "Perplexity bots doc adds llms.txt documentation index pointer"
source: perplexitybot
pillar: crawler
detected_at: 2026-04-29T10:06:36.216827+00:00
source_url: "https://docs.perplexity.ai/guides/bots"
change_kind: material
importance: 0.40
---

## What changed

A new "Documentation Index" header block was prepended to the [Perplexity bots guide](https://docs.perplexity.ai/guides/bots), directing readers (and LLM crawlers) to fetch [https://docs.perplexity.ai/llms.txt](https://docs.perplexity.ai/llms.txt) to discover all available documentation pages before exploring further. No existing content was modified.

## Implication

Perplexity has adopted the emerging `llms.txt` convention — a machine-readable site index intended for AI agents — on their own developer docs. Automated crawlers or AI assistants parsing this page will now be directed to `llms.txt` as the canonical entry point for the full docs structure. No changes to UA strings, IP ranges, or crawl policies were made.

## Raw diff

<details><summary>View diff</summary>

```diff
--- prev
+++ curr
@@ -1,3 +1,7 @@
+Documentation Index
+Fetch the complete documentation index at:
+https://docs.perplexity.ai/llms.txt
+Use this file to discover all available pages before exploring further.
 User Agent
 Description
 PerplexityBot
```

</details>
