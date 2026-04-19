---
slug: cloudflare-launches-redirects-for-ai-training-canonical-tags-become-http-301s-fo
title: "Cloudflare launches \"Redirects for AI Training\" — canonical tags become HTTP 301s for verified AI training crawlers"
source: cloudflare-blog
pillar: ecosystem
detected_at: 2026-04-17T21:00:00+00:00
source_url: https://blog.cloudflare.com/ai-redirects/
change_kind: material
importance: 0.75
---

## What changed

Cloudflare has introduced a new feature called "Redirects for AI Training," available on all paid plans via a single dashboard toggle under AI Crawl Control. When enabled, Cloudflare intercepts requests from verified AI training crawlers (e.g., GPTBot, ClaudeBot, Bytespider) and, if the served page contains a non-self-referencing, same-origin canonical tag, issues an HTTP 301 redirect to the canonical URL rather than serving the deprecated page. The feature builds on the existing `cf.verified_bot_category` field and requires no changes to site markup, since canonical tags are already present on 65–69% of web pages. Cloudflare reports that in their own 7-day test on developers.cloudflare.com, 100% of AI training crawler requests to pages with qualifying canonicals were redirected. Separately, Cloudflare Radar's AI Insights page now includes a response status code analysis dashboard showing how AI crawlers are treated across all Cloudflare traffic, broken down by bot, industry, and crawl purpose.

## Implication

Publishers and documentation site operators who maintain deprecated or legacy content alongside current pages now have a scalable, infrastructure-level mechanism to prevent AI training crawlers from ingesting outdated material — without touching robots.txt, writing custom redirect rules, or blocking crawlers entirely. Because the feature converts existing canonical tags into enforced redirects rather than advisory signals, it works automatically as content evolves. The limitation is notable: it only applies to verified crawlers in Cloudflare's AI Crawler category and does not retroactively correct already-ingested training data, meaning downstream model quality improvements are probabilistic and depend on recrawl cycles. For agent-infrastructure practitioners, the Radar status code analytics provide the first publicly accessible, at-scale view of how origins are actually responding to AI crawlers (200 vs. 301 vs. 403 vs. 402), which is useful for benchmarking crawler policy adoption across industries. The combination of enforcement tooling and observability data signals Cloudflare is positioning its network layer as a primary governance point for AI data supply chains.

