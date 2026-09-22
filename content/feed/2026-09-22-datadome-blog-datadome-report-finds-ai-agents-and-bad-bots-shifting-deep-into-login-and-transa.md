---
schema_version: 1
slug: datadome-blog-datadome-report-finds-ai-agents-and-bad-bots-shifting-deep-into-login-and-transa
title: "DataDome Report Finds AI Agents and Bad Bots Shifting Deep into Login and Transaction Endpoints"
source: datadome-blog
source_tier: specialist
status: reported
primary_track: measurement-economics
tracks:
  - measurement-economics
  - crawler-controls
  - agentic-web
actors:
  - "DataDome"
event_date: 2026-09-22T09:32:18+00:00
published_at: 2026-09-22T09:32:18+00:00
detected_at: 2026-09-22T13:08:11.171940+00:00
source_urls:
  - "https://datadome.co/press/state-of-bot-and-agent-security-report-2026/"
change_kind: material
importance: 0.73
confidence: high
evidence_ids:
  - "datadome-blog--f7ce6dbe3d5a34bf"
trend_signals:
  - deep endpoint agent crawling
  - automated scraping supply chain growth
  - declining perimeter bot protection efficacy
backfilled: false
---

## Summary

DataDome released its 2026 State of Bot & Agent Security Report, analyzing over one trillion requests across 75,000 customer sites alongside tests of 20,000 external domains. The research found bad bot traffic grew 124% year-over-year—outpacing human traffic by nine times—with scraping representing 70.9% of bad bot volume. Concurrently, AI agents generated 605.6 million requests targeting high-value flows like carts, payments, and login pages, while 65.3% of surveyed websites failed to block any evaluated bot types.

## Insight

Automated access has evolved beyond superficial public page harvesting at the perimeter into deep transactional and authenticated user flows, rendering binary identity checks inadequate without real-time session intent analysis.

## Implication

Web publishers and e-commerce operators relying solely on traditional robots.txt directives or perimeter IP blocks will face increased exposure on authentication, cart, and checkout endpoints as both commercial AI agents and scrapers emulate legitimate user workflows.

## Why it matters

As the AI data supply chain drives aggressive scraping and commercial agents access authenticated services, distinguishing benign AI activity from credential stuffing or unauthorized extraction requires evaluating behavior at transactional endpoints rather than simple crawler identification.

## Evidence

- [Primary source](https://datadome.co/press/state-of-bot-and-agent-security-report-2026/)
- Evidence ID: `datadome-blog--f7ce6dbe3d5a34bf`
