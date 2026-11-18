---
schema_version: 1
slug: simon-willison-prime-radiant-and-simon-willison-introduce-external-sandboxes-and-network-allow-
title: "Prime Radiant and Simon Willison Introduce External Sandboxes and Network Allow-Listing for Coding Agents"
source: simon-willison
source_tier: commentary
status: signal
primary_track: access-controls
tracks:
  - access-controls
  - identity-authorization
  - platform-ecosystem
actors:
  - "Simon Willison"
  - "Prime Radiant"
  - "Microsoft"
subject: agent
event_date: 2026-11-17T22:52:29+00:00
published_at: 2026-11-17T22:52:29+00:00
detected_at: 2026-11-18T16:57:56.492918+00:00
source_urls:
  - "https://simonwillison.net/2026/Nov/17/external-sandboxes-for-coding-agents/"
change_kind: material
importance: 0.68
confidence: high
evidence_ids:
  - "simon-willison--f69f9c6e99c6f354"
trend_signals:
  - agent execution sandboxing
  - credential masking proxies
  - outbound agent network allow-listing
players:
  - "microsoft"
backfilled: false
---

## Summary

Simon Willison and AI research lab Prime Radiant released the external sandbox pattern, separating coding agents from the environment where their generated code executes. The project published three open-source sandbox server implementations alongside an optional HTTP/HTTPS allow-list proxy and credential replacement mechanism. The architecture aims to mitigate prompt injection risks and untrusted code execution for tools like Claude Code, Codex, and Pi.

## Key facts

- Simon Willison collaborated with Prime Radiant to publish the 'external sandbox' pattern, keeping agent orchestration outside the sandbox where generated code runs.
- The project published three sandbox server implementations: external-sandbox-v86 (running Alpine Linux inside WebAssembly via v86), external-sandbox-container (using Apple Containers), and external-sandbox-quicksand (using Microsoft's Quicksand with QEMU and Alpine Linux).
- All three sandbox implementations expose a standardized localhost API compatible with coding agents such as Pi, Claude Code, and Codex.
- The sandboxes provide an optional HTTP/HTTPS allow-list proxy that controls the exact external hosts an agent's code can communicate with.
- A credential replacement mechanism allows code in the sandbox to execute authenticated API calls without exposing raw credentials or secrets to the agent.

## Insight

By placing execution in an external sandbox while intercepting outbound traffic through an allow-list proxy with credential replacement, developers can prevent autonomous agents from exfiltrating credentials or accessing unauthorized external network destinations.

## Implication

Developer tooling and agent runtimes will increasingly decouple model reasoning from code execution environments, adopting granular network proxy controls to restrict outbound requests and isolate sensitive API tokens.

## Why it matters

Autonomous coding agents face significant security risks from prompt injection and accidental system destruction; external sandboxing with network filtering provides a concrete defensive blueprint to govern agent execution and web access.

## Evidence

- [Primary source](https://simonwillison.net/2026/Nov/17/external-sandboxes-for-coding-agents/)
- Evidence ID: `simon-willison--f69f9c6e99c6f354`
