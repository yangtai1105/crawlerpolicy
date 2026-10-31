---
schema_version: 2
slug: a2a-specification-clarifies-interrupted-task-states-as-non-terminal-across-strea
title: "A2A Specification Clarifies Interrupted Task States as Non-Terminal Across Streaming Transports"
source: a2a-spec
source_tier: primary
primary_track: standards-protocols
tracks:
  - standards-protocols
  - platform-ecosystem
actors:
  - "A2A Project"
event_date: 2026-10-13T16:17:24+00:00
published_at: 2026-10-13T16:17:24+00:00
detected_at: 2026-10-31T20:51:06.172555+00:00
source_url: "https://github.com/a2aproject/A2A/pull/2270"
change_kind: material
importance: 0.52
confidence: high
evidence_ids:
  - "a2a-spec--816f5d8844a50ffe"
---

## Development

A proposed update to the Agent2Agent (A2A) protocol specification formally designates interrupted task states—specifically input-required and auth-required—as non-terminal. The change clarifies that servers retain lifecycle control during interruptions, meaning streams should not automatically terminate when input or authentication is requested. The update harmonizes divergent server-side SDK implementations across Python, Go, JavaScript, and .NET without modifying wire types.

## Key facts

- Pull Request #2270 in a2aproject/A2A establishes that task states are strictly categorized as terminal or non-terminal.
- The interrupted states TASK_STATE_INPUT_REQUIRED and TASK_STATE_AUTH_REQUIRED are designated as non-terminal.
- Under the clarified lifecycle, a server 'MAY keep processing it and transition it to any other state — including out of an interrupted state — without a message from the client, and MAY keep accepting messages directed to it.'
- Section 3.1.2 is amended so that entering a non-terminal or interrupted state 'SHOULD NOT by itself close the stream,' whereas terminal states still MUST close it.
- Section 11.7 removes 'or interrupted' from the Server-Sent Events (SSE) connection close rule.
- An SDK audit revealed divergence: a2a-python V2 keeps streams open, while a2a-go, a2a-js, and a2a-dotnet close streaming responses upon reaching input-required.

## Why it matters

Multi-agent workflows frequently encounter gating checks such as permission elevation or disambiguation; forcing connection resets during these pauses increases latency and state-handling complexity across interacting agent systems.

## Trend impact

- standardization of autonomous agent lifecycles
- harmonization of multi-agent streaming transports

## Evidence

- [Primary source](https://github.com/a2aproject/A2A/pull/2270)
- Evidence ID: `a2a-spec--816f5d8844a50ffe`

