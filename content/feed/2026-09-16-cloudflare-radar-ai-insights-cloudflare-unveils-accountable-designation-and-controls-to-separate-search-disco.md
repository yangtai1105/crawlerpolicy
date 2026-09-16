---
schema_version: 1
slug: cloudflare-radar-ai-insights-cloudflare-unveils-accountable-designation-and-controls-to-separate-search-disco
title: "Cloudflare Unveils Accountable Designation and Controls to Separate Search Discovery from AI Training"
source: cloudflare-radar-ai-insights
source_tier: measurement
status: verified
primary_track: crawler-controls
tracks:
  - crawler-controls
  - search-discovery
  - measurement-economics
actors:
  - "Cloudflare"
  - "Apple"
  - "Google"
  - "Microsoft"
event_date: 2026-09-16T13:10:48.105175+00:00
published_at: 2026-09-16T13:10:48.105175+00:00
detected_at: 2026-09-16T13:10:48.105175+00:00
source_urls:
  - "https://radar.cloudflare.com/ai-insights"
change_kind: material
importance: 0.82
confidence: high
evidence_ids:
  - "cloudflare-radar-ai-insights--bbb1ca653e82c31c"
trend_signals:
  - mixed-use crawler disentanglement
  - crawler accountability frameworks
  - search vs AI training opt-out bifurcation
development_slug: cloudflare-unveils-accountable-designation-and-controls-to-separate-search-disco
backfilled: false
---

## Summary

Cloudflare has introduced new crawl controls and an Accountable designation developed in alignment with Apple, Google, and Microsoft. The mechanism enables site owners to maintain discoverability in search engines while explicitly disallowing data collection for AI model training. The update was highlighted alongside new resources on Cloudflare Radar's AI Insights dashboard.

## Insight

By introducing an 'Accountable' crawler classification in partnership with major search operators (Apple, Google, Microsoft), Cloudflare is attempting to resolve the long-standing tension between mixed-use search indexers and AI training scrapers through coordinated granular controls rather than binary site blocking.

## Implication

Publishers and web administrators can now selectively block AI training uses without sacrificing search indexing from major platforms, while participating crawler operators face clearer technical accountability standards.

## Why it matters

A persistent problem in machine access has been the bundling of search indexing and AI model training under shared user-agents; standardizing accountable separation provides web operators with enforceable control over their intellectual property without disappearing from search results.

## Evidence

- [Primary source](https://radar.cloudflare.com/ai-insights)
- Evidence ID: `cloudflare-radar-ai-insights--bbb1ca653e82c31c`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -149,6 +149,16 @@
 [Copy link](#latest-ai-blog-posts)
 Posts tagged with "AI" from the Cloudflare blog
 [Cloudflare Blog](https://blog.cloudflare.com/tag/ai/)
+## [Have it both ways: stay discoverable in search while disallowing AI training](https://blog.cloudflare.com/accountable-mixed-use-ai-crawlers/)
+Cloudflare is giving site owners a way to stay discoverable while disallowing AI training. New controls and an Accountable designation establish a shared model with Apple, Google, and Microsoft.
+- [AI](https://blog.cloudflare.com/tag/ai/)
+- [AI Bots](https://blog.cloudflare.com/tag/ai-bots/)
+- [Bot Management](https://blog.cloudflare.com/tag/bot-management/)
+- [Network Services](https://blog.cloudflare.com/tag/network-services/)
+- [Product News](https://blog.cloudflare.com/tag/product-news/)
+- [Security](https://blog.cloudflare.com/tag/security/)
+Bryan Becker
+Sep 2026
 ## [How Cloudflare detects MCP traffic and helps secure it](https://blog.cloudflare.com/mcp-security-updates/)
 Cloudflare Gateway identifies MCP requests using protocol-level heuristics. Security teams can use that signal to find shadow MCP traffic, enforce Portal-only access for approved servers, and block direct connections on managed network paths.
 - [AI](https://blog.cloudflare.com/tag/ai/)
@@ -171,18 +181,5 @@
 - [Zero Trust](https://blog.cloudflare.com/tag/zero-trust/)
 Chythra Malapati, Matt Rothenberg, Matt Provost
 Aug 2026
-## [Everything we launched during Agents Week](https://blog.cloudflare.com/agents-week-review-august-2026/)
-Our latest Agents Week has come to a close. Here’s a recap of all the announcements we made from Wallets to Radar.
-- [Agents](https://blog.cloudflare.com/tag/agents/)
-- [Agents Week](https://blog.cloudflare.com/tag/agents-week/)
-- [AI](https://blog.cloudflare.com/tag/ai/)
-- [Cloudflare One](https://blog.cloudflare.com/tag/cloudflare-one/)
-- [Cloudflare Workers](https://blog.cloudflare.com/tag/cloudflare-workers/)
-- [Developer Platform](https://blog.cloudflare.com/tag/developer-platform/)
-- [Developers](https://blog.cloudflare.com/tag/developers/)
-- [SASE](https://blog.cloudflare.com/tag/sase/)
-- [Zero Trust](https://blog.cloudflare.com/tag/zero-trust/)
-Shelley Jones, Ann Ming Samborski, Kathy Liao
-Aug 2026
 © 2026 Cloudflare, Inc.
 [Privacy Policy](https://www.cloudflare.com/privacypolicy/) [Terms of Use](https://www.cloudflare.com/website-terms/) [Disclosure](https://www.cloudflare.com/disclosure/) [Trust & Safety](https://www.cloudflare.com/abuse/) [Trademark](https://www.cloudflare.com/trademark/) [Support](https://www.support.cloudflare.com/s/?language=en_US)
```

</details>
