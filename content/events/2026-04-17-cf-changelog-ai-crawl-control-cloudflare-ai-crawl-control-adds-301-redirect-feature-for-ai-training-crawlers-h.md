---
slug: cloudflare-ai-crawl-control-adds-301-redirect-feature-for-ai-training-crawlers-h
title: "Cloudflare AI Crawl Control adds 301-redirect feature for AI training crawlers hitting canonical URLs"
source: cf-changelog-ai-crawl-control
pillar: crawler
detected_at: 2026-04-17T08:00:00+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-04-17-redirects-for-ai-training/"
change_kind: material
importance: 0.72
---

## What changed

A new feature — "Redirects for AI Training" — has been added to [Cloudflare's AI Crawl Control](https://developers.cloudflare.com/ai-crawl-control/reference/redirects-for-ai-training/). When toggled on via **AI Crawl Control > Quick Actions**, verified AI training crawlers requesting pages that carry a `<link rel="canonical">` pointing elsewhere receive a `301` redirect to the canonical URL, while humans, search crawlers, and AI Search agents continue to receive the original page. The feature requires no new configuration beyond enabling the toggle and is available on Pro, Business, and Enterprise plans at no added cost.

## Implication

Site operators on eligible plans can now passively steer AI training crawlers toward canonical content without custom rules — reducing duplicate-page ingestion into AI training datasets. Because only *verified* AI training crawlers are redirected, other traffic (including AI search agents) is unaffected. Publishers concerned about which crawlers qualify as "verified" should consult the [Redirects for AI Training documentation](https://developers.cloudflare.com/ai-crawl-control/reference/redirects-for-ai-training/) for the crawler classification criteria.

