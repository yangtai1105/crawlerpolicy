---
slug: cloudflare-ai-crawl-control-adds-waf-rule-preservation-for-custom-modifications
title: "Cloudflare AI Crawl Control adds WAF rule preservation for custom modifications"
source: cf-changelog-ai-crawl-control
pillar: crawler
detected_at: 2026-03-24T08:00:00+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-03-24-waf-rule-preservation/"
change_kind: material
importance: 0.50
---

## What changed

A new capability was added to Cloudflare AI Crawl Control: custom modifications made directly in the WAF custom rules editor (e.g., path-based exceptions, extra user agents, additional expression clauses) are now preserved when crawler actions are updated via AI Crawl Control. If the WAF rule expression is modified in a way AI Crawl Control cannot parse, a warning banner appears on the Crawlers page linking to the rule in WAF. Full details at [WAF rule management](https://developers.cloudflare.com/ai-crawl-control/features/manage-ai-crawlers/#waf-rule-management).

## Implication

Operators who previously avoided mixing AI Crawl Control with direct WAF rule edits — fearing overwrites — can now safely layer custom WAF expressions (e.g., path allowlists, additional bot UA patterns) on top of AI Crawl Control-managed rules without losing them on the next UI update. This reduces the friction of fine-grained crawler access control within Cloudflare's ecosystem.

