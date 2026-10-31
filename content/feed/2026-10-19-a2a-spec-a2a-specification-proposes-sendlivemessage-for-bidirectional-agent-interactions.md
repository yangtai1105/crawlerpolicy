---
schema_version: 1
slug: a2a-spec-a2a-specification-proposes-sendlivemessage-for-bidirectional-agent-interactions
title: "A2A Specification Proposes SendLiveMessage for Bidirectional Agent Interactions"
source: a2a-spec
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - platform-ecosystem
actors:
  - "Agent2Agent Protocol (spec)"
subject: agent
event_date: 2026-10-19T16:40:46+00:00
published_at: 2026-10-19T16:40:46+00:00
detected_at: 2026-10-31T20:51:06.172555+00:00
source_urls:
  - "https://github.com/a2aproject/A2A/pull/2153"
change_kind: material
importance: 0.65
confidence: high
evidence_ids:
  - "a2a-spec--ab47ccabfa0adab8"
trend_signals:
  - agent-to-agent duplex streaming
  - standardized agent task observation
development_slug: a2a-specification-proposes-sendlivemessage-for-bidirectional-agent-interactions
protocols:
  - "a2a"
backfilled: false
---

## Summary

The Agent2Agent (A2A) protocol specification introduced a pull request defining `SendLiveMessage`, a single operation facilitating bidirectional communication between agents. The fully additive operation supports duplex sessions, short message exchanges, and passive task observation across gRPC, WebSocket, and HTTP transports. It establishes opening semantics, stream-level error handling via `StreamError`, and introduces `TaskMessageUpdateEvent` for clients using A2A version 1.1 or higher.

## Key facts

- Pull Request #2153 introduces `SendLiveMessage` as an additive operation for bidirectional agent interaction in the A2A specification.
- The operation serves three primary use cases: long-lived duplex sessions, brief connect-send-disconnect exchanges, and attaching to an existing task strictly to observe it.
- `StreamRequest.payload` reuses existing message definitions (`SubscribeToTaskRequest` and `SendMessageRequest`) rather than defining new wrapper messages.
- Opening semantics allow binding via `subscribe` with an optional `last_seen_generation` to replay missed events without resending a full `Task` snapshot.
- Native duplex transports like gRPC and WebSocket use a single connection, while HTTP models the downlink as a server stream with separate short-lived calls for uplink messages.
- A new `StreamError` mechanism rejects malformed requests without terminating the underlying connection, and servers must reject unrecognized payloads with `StreamError` instead of closing streams.
- `TaskMessageUpdateEvent` delivers client-originated timeline entries exclusively to clients negotiating `A2A-Version: 1.1` or higher.
- Client-written artifacts were deferred and split into a separate pull request (#2322).

## Insight

Rather than creating dedicated streaming wrappers, the specification reuses existing request structures (`SubscribeToTaskRequest` and `SendMessageRequest`) within a single polymorphic stream, achieving transport parity by mapping the same semantics across native duplex connections and split HTTP server streams.

## Implication

Developers building autonomous agent runtimes and client integrations will be able to maintain persistent, interactive sessions with running tasks without tearing down connections on individual request failures.

## Why it matters

Real-time collaboration between autonomous agents requires robust duplex streaming that handles mid-stream errors and state resynchronization without brittle connection resets.

## Evidence

- [Primary source](https://github.com/a2aproject/A2A/pull/2153)
- Evidence ID: `a2a-spec--ab47ccabfa0adab8`
