---
schema_version: 1
slug: a2a-spec-a2a-specification-proposes-client-written-artifacts-across-messaging-methods
title: "A2A Specification Proposes Client-Written Artifacts Across Messaging Methods"
source: a2a-spec
source_tier: primary
status: verified
primary_track: standards-protocols
tracks:
  - standards-protocols
  - platform-ecosystem
actors:
  - "A2A Project"
subject: agent
event_date: 2026-10-20T16:56:36+00:00
published_at: 2026-10-20T16:56:36+00:00
detected_at: 2026-10-31T20:51:06.172555+00:00
source_urls:
  - "https://github.com/a2aproject/A2A/pull/2322"
change_kind: material
importance: 0.58
confidence: high
evidence_ids:
  - "a2a-spec--c5c1dae975ca0362"
trend_signals:
  - multi-agent orchestration standardization
  - collaborative agent artifact editing
development_slug: a2a-specification-proposes-client-written-artifacts-across-messaging-methods
protocols:
  - "a2a"
backfilled: false
---

## Summary

A new Agent2Agent (A2A) protocol specification proposal introduces client-authored artifacts across unary, server-streaming, and bidirectional messaging methods. The update enables clients to submit multiple artifacts or chunked updates via SendMessageRequest alongside control messages or against existing tasks. It also defines capability advertising for user artifacts and establishes server ownership over artifact generation sequencing.

## Key facts

- Pull Request #2322 extends SendMessageRequest with artifact_updates (repeated TaskArtifactUpdateEvent) across SendMessage, SendStreamingMessage, and SendLiveMessage.
- A control message is mandatory when creating a new task without a task_id, but message may be omitted when appending artifact_updates to an existing task.
- When a message and artifact_updates are submitted together to create or update a Task, the message appends to the timeline first, followed by artifact_updates in list order.
- Adds AgentCapabilities.user_artifacts as an optional boolean signaling whether an agent accepts client-written ROLE_USER artifacts, returning UnsupportedOperationError or StreamError if unsupported.
- Establishes server ownership of the generation field on TaskArtifactUpdateEvent: clients must leave it unset, servers must ignore incoming values, and servers stamp authoritative values upon broadcasting downstream.
- Restores Artifact.role to differentiate between client-authored inputs (ROLE_USER) and agent outputs (ROLE_AGENT, the default).

## Insight

By extending SendMessageRequest with artifact updates and restoring role attributes (ROLE_USER versus ROLE_AGENT), the protocol formalizes shared, bidirectional document editing and payload handoffs between orchestrators and autonomous agents without requiring separate out-of-band transfer mechanisms.

## Implication

Agent runtime developers and server implementers must update capability discovery to indicate whether they accept user-authored artifacts and implement server-side generation stamping to prevent client collision during collaborative workflows.

## Why it matters

Autonomous agent collaboration frequently requires passing large documents or structured work items back and forth; establishing unified artifact exchange semantics prevents fragmented, proprietary file-handling patterns across multi-agent networks.

## Evidence

- [Primary source](https://github.com/a2aproject/A2A/pull/2322)
- Evidence ID: `a2a-spec--c5c1dae975ca0362`
