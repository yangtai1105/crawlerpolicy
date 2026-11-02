---
schema_version: 2
slug: universal-commerce-protocol-backports-ask-capability-to-2026-08-25-release-branc
title: "Universal Commerce Protocol Backports Ask Capability to 2026-08-25 Release Branch"
source: ucp-spec
source_tier: primary
primary_track: standards-protocols
tracks:
  - standards-protocols
  - platform-ecosystem
actors:
  - "Universal Commerce Protocol"
event_date: 2026-11-02T15:56:13+00:00
published_at: 2026-11-02T15:56:13+00:00
detected_at: 2026-11-02T17:52:31.512194+00:00
source_url: "https://github.com/Universal-Commerce-Protocol/ucp/pull/1024"
change_kind: material
importance: 0.65
confidence: high
evidence_ids:
  - "ucp-spec--9f1e1582ff89ae60"
---

## Development

The Universal Commerce Protocol Technical Council approved backporting the natural-language question-and-answer capability to the release/2026-08-25 branch. The update adds dev.ucp.common.ask, enabling platforms to submit questions on behalf of buyers via REST and Model Context Protocol interfaces. The capability is purely additive and backward-compatible, returning read-only, non-authoritative answers with multi-turn conversation context.

## Key facts

- Pull Request #1024 backports PR #538 ('feat: ask capability for natural-language Q&A') to the release/2026-08-25 release branch.
- The change introduces dev.ucp.common.ask, allowing a platform to ask a natural-language question on behalf of a buyer and receive a read-only, non-authoritative answer.
- The implementation ships canonical schemas, REST (POST /ask), and MCP (ask_business) bindings on the Common service.
- Responses require a 'plain' encoding and support optional links, messages, and multi-turn 'conversation' context.
- Changes are backward-compatible and additive, introducing an optional 'id' field to Link and an optional 'Idempotency-Key' header on REST and MCP.

## Why it matters

Autonomous and delegated commercial agents require standardized ways to query product and merchant knowledge bases without executing state-changing shopping cart actions.

## Trend impact

- Standardization of agentic MCP tools for commercial Q&A
- Expansion of read-only conversational context in commerce protocols

## Evidence

- [Primary source](https://github.com/Universal-Commerce-Protocol/ucp/pull/1024)
- Evidence ID: `ucp-spec--9f1e1582ff89ae60`

