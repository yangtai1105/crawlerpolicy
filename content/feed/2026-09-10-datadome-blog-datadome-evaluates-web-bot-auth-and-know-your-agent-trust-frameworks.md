---
schema_version: 1
slug: datadome-blog-datadome-evaluates-web-bot-auth-and-know-your-agent-trust-frameworks
title: "DataDome Evaluates Web Bot Auth and Know Your Agent Trust Frameworks"
source: datadome-blog
source_tier: specialist
status: reported
primary_track: agentic-web
tracks:
  - agentic-web
  - standards-protocols
  - crawler-controls
actors:
  - "DataDome"
  - "Cloudflare"
  - "AWS Bedrock"
  - "IETF"
event_date: 2026-09-10T14:21:23+00:00
published_at: 2026-09-10T14:21:23+00:00
detected_at: 2026-09-11T12:38:01.191471+00:00
source_urls:
  - "https://datadome.co/agent-trust-management/web-bot-auth-and-know-your-agent-why-identity-isnt-enough/"
change_kind: material
importance: 0.68
confidence: high
evidence_ids:
  - "datadome-blog--9a96b94c624592fd"
trend_signals:
  - cryptographic agent authentication
  - know your agent governance
  - http message signatures
  - behavioral bot detection
backfilled: false
---

## Summary

DataDome outlined the mechanisms and limitations of two emerging agent trust standards: Web Bot Auth (WBA), an IETF cryptographic protocol using Ed25519 HTTP message signatures and public key directories at /.well-known/http-message-signature-directory, and Know Your Agent (KYA), an identity governance framework. While WBA verifies platform origin and KYA establishes ownership and authorized scope, DataDome argues that neither guarantees benign runtime execution. The firm advocates combining both standards with continuous real-time behavioral and intent-based enforcement to prevent abuse from authenticated agents.

## Insight

Cryptographic authentication proves platform origin and governance defines permitted scope, but neither protocol layer can determine dynamic intent or prevent authenticated agents with over-scoped credentials from executing malicious actions.

## Implication

Security teams and web operators cannot rely solely on cryptographic allowlisting or signed bot directories from major providers like AWS Bedrock or Cloudflare to permit autonomous traffic without active runtime behavioral inspection.

## Why it matters

As autonomous AI agents rapidly expand across the open web, establishing robust crawler control requires moving beyond static user-agent strings toward multi-layered systems that combine cryptographic provenance with dynamic session analysis.

## Evidence

- [Primary source](https://datadome.co/agent-trust-management/web-bot-auth-and-know-your-agent-why-identity-isnt-enough/)
- Evidence ID: `datadome-blog--9a96b94c624592fd`
