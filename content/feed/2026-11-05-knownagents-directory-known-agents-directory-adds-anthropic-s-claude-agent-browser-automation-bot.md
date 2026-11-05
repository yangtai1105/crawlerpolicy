---
schema_version: 1
slug: knownagents-directory-known-agents-directory-adds-anthropic-s-claude-agent-browser-automation-bot
title: "Known Agents Directory Adds Anthropic's Claude-Agent Browser Automation Bot"
source: knownagents-directory
source_tier: measurement
status: verified
primary_track: access-controls
tracks:
  - access-controls
  - measurement-economics
  - platform-ecosystem
actors:
  - "Anthropic"
  - "Known Agents"
subject: agent
event_date: 2026-11-05T16:10:50.204137+00:00
published_at: 2026-11-05T16:10:50.204137+00:00
detected_at: 2026-11-05T16:10:50.204137+00:00
source_urls:
  - "https://knownagents.com/agents"
change_kind: material
importance: 0.55
confidence: high
evidence_ids:
  - "knownagents-directory--1b700648a1f116c8"
trend_signals:
  - segmentation-of-agent-roles
  - browser-use-agent-emergence
development_slug: known-agents-directory-adds-anthropic-s-claude-agent-browser-automation-bot
players:
  - "anthropic"
backfilled: false
---

## Summary

The Known Agents directory has cataloged a new entry for Claude-Agent, identified as Anthropic's cloud browser agent for Claude Duet. The listing classifies the bot as an AI Agent designed to browse websites and perform multi-step tasks on behalf of users. The addition expands the directory's total coverage across 41 pages.

## Key facts

- Known Agents added Claude-Agent to its directory under the AI Agents category.
- The directory describes Claude-Agent as Anthropic's cloud browser agent for Claude Duet.
- Claude-Agent is documented as navigating websites and completing multi-step tasks on behalf of users using an actual web browser.
- The listing sits alongside other Anthropic bots, including Claude-User (AI Assistant) and Claude-Code (AI Coding Agent).
- The addition of Claude-Agent increased the directory's pagination from 40 to 41 pages.

## Insight

AI model developers are establishing dedicated agent user identifiers for autonomous browser execution (such as Claude-Agent) that operate separately from fetch-only assistant crawlers (such as Claude-User) and developer coding tools (such as Claude-Code).

## Implication

Web administrators seeking to distinguish between passive conversational citations and state-changing or interactive cloud browser automation will need to configure separate access controls for Claude-Agent.

## Why it matters

As autonomous browsing agents move into commercial workflows like Claude Duet, operators require distinct user-agent signatures to manage, rate-limit, or block automated task execution without necessarily breaking user-prompt search lookups.

## Evidence

- [Primary source](https://knownagents.com/agents)
- Evidence ID: `knownagents-directory--1b700648a1f116c8`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -45,6 +45,12 @@
 AI Agent
 Uses an actual web browser to autonomously complete complex tasks on behalf of a human user
 See More →
+Claude-Agent
+Claude-Agent is Anthropic's cloud browser agent for Claude Duet. It navigates websites and completes multi-step tasks on behalf of users.
+AI Agent
+AI Agent
+Uses an actual web browser to autonomously complete complex tasks on behalf of a human user
+See More →
 CledaraBot
 CledaraBot is an AI agent operated by Cledara that visits SaaS providers to complete customer-approved administrative tasks, including invoice collection and user managem…
 AI Agent
@@ -317,11 +323,5 @@
 AI Coding Agent
 Fetches documentation and other resources to help build software
 See More →
-Google-Gemini-CLI
-Gemini CLI is an AI coding agent by Google that can query and edit large codebases, generate apps from images or PDFs, and automate complex workflows directly from the te…
-AI Coding Agent
-AI Coding Agent
-Fetches documentation and other resources to help build software
-See More →
-Page 1 of 40
+Page 1 of 41
 Next →
```

</details>
