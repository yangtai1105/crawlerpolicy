---
schema_version: 1
slug: cloudflare-blog-cloudflare-adds-visibility-analytics-and-granular-policy-controls-for-personal-a
title: "Cloudflare Adds Visibility Analytics and Granular Policy Controls for Personal AI Agents"
source: cloudflare-blog
source_tier: specialist
status: reported
primary_track: access-controls
tracks:
  - access-controls
  - identity-authorization
  - measurement-economics
  - platform-ecosystem
actors:
  - "Cloudflare"
subject: agent
event_date: 2026-11-04T14:00:00+00:00
published_at: 2026-11-04T14:00:00+00:00
detected_at: 2026-11-04T15:58:19.880292+00:00
source_urls:
  - "https://blog.cloudflare.com/personal-agents-visibility-control/"
change_kind: material
importance: 0.82
confidence: high
evidence_ids:
  - "cloudflare-blog--bab89b5eb36af171"
trend_signals:
  - personal-agent-access-management
  - ad-monetization-aware-edge-blocking
  - user-agent-attribution-in-fraud-detection
players:
  - "cloudflare"
backfilled: false
---

## Summary

Cloudflare has introduced dedicated analytics and granular access rules for personal agents acting on behalf of human users. In Security Analytics, personal assistants appear as a distinct classification category alongside existing automated and human traffic types. Site owners can inspect per-agent request behavior, link activity to user accounts via Account Abuse Protection, and enforce individual policies including Allow, Block, or Block on pages with ads.

## Key facts

- Cloudflare introduced "Personal Assistants" as a dedicated category in the Bot Analysis chart within Security Analytics, positioned alongside Verified Bot, Likely Human, Likely Automated, and Automated.
- A new Personal Assistants widget in Top statistics displays which agents visit a site, total request counts, status codes, requested paths, and originating networks.
- For sites using [Account Abuse Protection](https://blog.cloudflare.com/account-abuse-protection-dashboard/), fraud teams can identify which user account an agent represents across login and sign-up events, with options to mitigate suspect accounts via WAF rules on Hashed User IDs.
- Cloudflare renamed its configuration interface to "AI Crawler and Agent access policies" under [Security Settings](https://dash.cloudflare.com/?to=/:account/:zone/security/settings?tabs=bot-traffic).
- Site administrators can configure overall agent behavior and set individual rules per supported personal agent using three choices: "Allow (do not block)", "Block on pages with ads", or "Block".
- Cloudflare added an onboarding prompt for new zones asking whether pages are monetized with ads, tailoring default recommended agent policies based on the answer.

## Insight

Personal agents break the traditional binary of human versus automated bot traffic by executing legitimate user intents while generating automated request footprints. Cloudflare addresses this divergence by decoupling agent access controls from general crawler rules and tying agent identity into user-level authentication and fraud-detection layers.

## Implication

Publishers and e-commerce platforms can selectively permit AI assistants on transactional pages while restricting them from ad-monetized content to preserve display ad revenue. Operators of personal agents will face selective, edge-enforced filtering depending on whether their requests navigate around monetized surfaces or lack transparent user delegation context.

## Why it matters

As end users increasingly deploy automated assistants to browse, compare, and shop, blanket bot blocking risks cutting off genuine paying customers. Providing edge-level controls that distinguish between web crawlers and delegated personal agents establishes a foundational framework for managing agentic web access.

## Evidence

- [Primary source](https://blog.cloudflare.com/personal-agents-visibility-control/)
- Evidence ID: `cloudflare-blog--bab89b5eb36af171`
