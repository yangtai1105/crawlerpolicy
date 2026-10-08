---
schema_version: 1
slug: datadome-blog-datadome-report-shows-ai-bot-requests-surging-toward-sensitive-endpoints-as-spoo
title: "DataDome Report Shows AI Bot Requests Surging Toward Sensitive Endpoints as Spoofing Rises 45%"
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
  - "Meta"
  - "OpenAI"
  - "Anthropic"
  - "Google"
  - "DuckDuckGo"
  - "Huawei"
event_date: 2026-10-07T13:16:27+00:00
published_at: 2026-10-07T13:16:27+00:00
detected_at: 2026-10-08T15:14:55.717190+00:00
source_urls:
  - "https://datadome.co/threat-research/state-of-bot-and-agent-security-report-key-ai-findings/"
change_kind: material
importance: 0.73
confidence: high
evidence_ids:
  - "datadome-blog--7fa24f12e66d78da"
trend_signals:
  - transactional-agent-penetration
  - crawler-identity-spoofing
  - ineffectiveness-of-static-allowlists
  - ai-traffic-polarization
backfilled: false
---

## Summary

DataDome's 2026 State of Bot & Agent Security Report analyzed 52.7 billion AI agent and LLM crawler requests between July 2025 and June 2026, finding that AI traffic grew 82.3% to reach 1.7% of all web requests. While Meta (46.3%) and OpenAI (34.6%) dominated observed AI traffic, 605.6 million requests hit sensitive endpoints like login and checkout flows, with AI hits to login pages growing 735.8% over six months. Across 21,491 audited websites, 65.3% blocked none of the tested bot or spoofed agent types, even as agent impersonation rose 45% between February and July 2026.

## Insight

Relying on user-agent strings for crawler governance has broken down: 80% of AI agents do not declare a reliable identity, and popular identifiers like Meta-ExternalAgent, GPTBot, and ClaudeBot are heavily spoofed to bypass static filters. At the same time, AI agents are shifting from passive crawling of public pages to deep transactional interactions across authentication and checkout flows, blurring the distinction between automated shopping assistants and credential-stuffing bots.

## Implication

Web operators using basic robots.txt directives or static User-Agent blocklists cannot verify authenticity or protect sensitive endpoints from impersonation. Site owners will increasingly need behavior-based session verification and reverse DNS or cryptographic validation to separate legitimate delegated agents and referral traffic from malicious scrapers.

## Why it matters

As AI assistants attempt autonomous actions on behalf of consumers, traditional perimeter defenses that treat all automation as scrapers risk breaking high-intent referral channels, while permissive setups leave authentication endpoints exposed to spoofed agent traffic.

## Evidence

- [Primary source](https://datadome.co/threat-research/state-of-bot-and-agent-security-report-key-ai-findings/)
- Evidence ID: `datadome-blog--7fa24f12e66d78da`
