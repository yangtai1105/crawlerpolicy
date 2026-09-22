---
schema_version: 1
slug: datadome-blog-datadome-2026-security-report-highlights-rising-scraping-volumes-and-ai-agent-sp
title: "DataDome 2026 Security Report Highlights Rising Scraping Volumes and AI Agent Spoofing"
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
  - "OpenAI"
  - "Meta"
event_date: 2026-09-22T09:32:14+00:00
published_at: 2026-09-22T09:32:14+00:00
detected_at: 2026-09-22T13:08:11.171940+00:00
source_urls:
  - "https://datadome.co/threat-research/state-of-bot-and-agent-security-report-2026-key-takeaways/"
change_kind: material
importance: 0.78
confidence: high
evidence_ids:
  - "datadome-blog--e5ed15c94d320fe3"
trend_signals:
  - ai-agent-spoofing
  - intent-based-traffic-filtering
  - accelerating-scraping-volume
  - deep-endpoint-agent-crawling
backfilled: false
---

## Summary

DataDome released its 2026 State of Bot & Agent Security Report based on an analysis of over 75,000 customer sites and tests against 21,491 websites between July 2025 and June 2026. Bad bot traffic surged 124% year-over-year, driven heavily by scraping, which represented 70.9% of bad bot volume. Additionally, AI agent spoofing rose 45% between February and July 2026, while over 70% of tested websites permitted spoofed AI crawlers past defenses without challenge.

## Insight

Traditional identity-based controls like user-agent matching (such as claiming to be GPTBot or ClaudeBot) and static allowlists are failing as automated tools increasingly spoof recognized crawler identities and penetrate deep transactional endpoints, including login and checkout flows.

## Implication

Web publishers and site operators relying solely on robots.txt rules or unverified user-agent filtering will face higher rates of unverified scraping and credential stuffing, forcing a transition toward behavioral and intent-based traffic verification.

## Why it matters

As the AI data supply chain expands and agentic browsing moves into transactional workflows, the inability to distinguish between legitimate user agents and unauthorized spoofed bots poses severe operational, security, and content governance challenges.

## Evidence

- [Primary source](https://datadome.co/threat-research/state-of-bot-and-agent-security-report-2026-key-takeaways/)
- Evidence ID: `datadome-blog--e5ed15c94d320fe3`
