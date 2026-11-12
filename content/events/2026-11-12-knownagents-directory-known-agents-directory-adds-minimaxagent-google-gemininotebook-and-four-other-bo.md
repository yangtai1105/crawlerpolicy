---
schema_version: 2
slug: known-agents-directory-adds-minimaxagent-google-gemininotebook-and-four-other-bo
title: "Known Agents Directory Adds MiniMaxAgent, Google-GeminiNotebook, and Four Other Bot Identifiers"
source: knownagents-directory
source_tier: measurement
primary_track: access-controls
tracks:
  - access-controls
  - measurement-economics
  - platform-ecosystem
actors:
  - "Google"
  - "MiniMax"
  - "Diffbot"
  - "Haiku"
  - "Liner"
  - "Known Agents"
event_date: 2026-11-12T16:36:29.095235+00:00
published_at: 2026-11-12T16:36:29.095235+00:00
detected_at: 2026-11-12T16:36:29.095235+00:00
source_url: "https://knownagents.com/agents"
change_kind: material
importance: 0.45
confidence: high
evidence_ids:
  - "knownagents-directory--d1a63e4a5cc93387"
---

## Development

The Known Agents directory has indexed several new bot identifiers, including MiniMaxAgent, Diffbot-User, Google-GeminiNotebook, Haiku-SearchBot, and Liner-User. The update also documents Google-GeminiNotebook as Google's current fetcher for Gemini Notebook source URLs while noting Google-NotebookLM as a legacy identifier that remains active. These entries expand the catalog of browser-based task agents and user-prompted AI assistant fetchers navigating the web.

## Key facts

- Known Agents added MiniMaxAgent under the 'AI Agent' category, defined as browsing and using online information to complete user-directed tasks using an actual web browser.
- Google-GeminiNotebook was added under 'AI Assistant' to fetch individual URLs added as sources in Gemini Notebook for analysis and summarization.
- Google-NotebookLM's description was updated to identify it as Google's 'former Gemini Notebook fetcher identifier that continues to retrieve source URLs users add to their notebooks.'
- Diffbot-User was added as an AI assistant fetcher retrieving URLs on behalf of human users interacting with Diffbot software.
- Haiku-SearchBot was added as a fetcher retrieving web pages in response to user requests across Haiku's legal AI services.
- Liner-User was introduced alongside LinerBot to fetch web content for Liner to answer user queries with cited sources.

## Why it matters

Granular user-agent strings provide web publishers visibility into whether traffic represents automated background crawling or direct, human-prompted retrieval by tools like MiniMax or Google Gemini.

## Trend impact

- user_agent_specialization
- agentic_browser_adoption

## Evidence

- [Primary source](https://knownagents.com/agents)
- Evidence ID: `knownagents-directory--d1a63e4a5cc93387`

<details><summary>View raw diff</summary>

```diff
--- prev
+++ curr
@@ -105,6 +105,12 @@
 AI Agent
 Uses an actual web browser to autonomously complete complex tasks on behalf of a human user
 See More →
+MiniMaxAgent
+MiniMaxAgent browses and uses online information to complete complex user-directed tasks in MiniMax Agent.
+AI Agent
+AI Agent
+Uses an actual web browser to autonomously complete complex tasks on behalf of a human user
+See More →
 Muse
 Muse is a personal AI agent created by Meta that uses a web browser and connected apps to complete multi-step tasks such as filling out forms, booking travel, sending ema…
 AI Agent
@@ -166,6 +172,12 @@
 AI Assistant
 Fetches website content in response to a user prompt, to include in an AI-generated answer
 See More →
+Diffbot-User
+Diffbot-User fetches URLs on behalf of human users interacting with Diffbot software.
+AI Assistant
+AI Assistant
+Fetches website content in response to a user prompt, to include in an AI-generated answer
+See More →
 DuckAssistBot
 DuckAssistBot is a web crawler that scans websites to collect content for DuckDuckGo's AI-assisted answers feature, which generates brief responses to search queries usin…
 AI Assistant
@@ -196,8 +208,14 @@
 AI Assistant
 Fetches website content in response to a user prompt, to include in an AI-generated answer
 See More →
+Google-GeminiNotebook
+Google-GeminiNotebook fetches individual URLs that users add as sources in Gemini Notebook so Google can analyze and summarize their content.
+AI Assistant
+AI Assistant
+Fetches website content in response to a user prompt, to include in an AI-generated answer
+See More →
 Google-NotebookLM
-Google-NotebookLM is an AI-powered research and note-taking assistant that helps users synthesize information from uploaded sources like documents, transcripts, or web co…
+Google-NotebookLM is Google's former Gemini Notebook fetcher identifier that continues to retrieve source URLs users add to their notebooks.
 AI Assistant
 AI Assistant
 Fetches website content in response to a user prompt, to include in an AI-generated answer
@@ -208,6 +226,12 @@
 AI Assistant
 Fetches website content in response to a user prompt, to include in an AI-generated answer
 See More →
+Haiku-SearchBot
+Haiku-SearchBot retrieves webpages in response to user requests through Haiku's legal AI services.
+AI Assistant
+AI Assistant
+Fetches website content in response to a user prompt, to include in an AI-generated answer
+See More →
 kagi-fetcher
 kagi-fetcher is an AI Assistant operated by Kagi that fetches web content to answer user queries through Kagi AI, their suite of AI-powered tools including Assistant, Res…
 AI Assistant
@@ -226,6 +250,12 @@
 AI Assistant
 Fetches website content in response to a user prompt, to include in an AI-generated answer
 See More →
+Liner-User
+Liner-User fetches web content for Liner to answer user questions with cited information.
+AI Assistant
+AI Assistant
+Fetches website content in response to a user prompt, to include in an AI-generated answer
+See More →
 LinerBot
 LinerBot is the web crawler used by Liner AI assistant to gather information from academic sources and websites to provide accurate answers with line-by-line source citat…
 AI Assistant
@@ -292,36 +322,5 @@
 AI Assistant
 Fetches website content in response to a user prompt, to include in an AI-generated answer
 See More →
-AI Coding Agents
-Claude-Code
-Claude-Code is Anthropic's coding agent for building, debugging, and modifying software from the terminal, including multi-file changes and repository workflows.
-AI Coding Agent
-AI Coding Agent
-Fetches documentation and other resources to help build software
-See More →
-Code
-Code (GitHub Copilot) is an AI coding agent that can autonomously plan, build, and execute development tasks, functioning as a collaborative AI pair programmer.
-AI Coding Agent
-AI Coding Agent
-Fetches documentation and other resources to help build software
-See More →
-Codex
-Codex is an AI coding agent by OpenAI that helps developers write, review, debug, and ship code.
-AI Coding Agent
-AI Coding Agent
-Fetches documentation and other resources to help build software
-See More →
-Cursor
-Cursor is an AI coding agent that helps write, edit, and understand code.
-AI Coding Agent
-AI Coding Agent
-Fetches documentation and other resources to help build software
-See More →
-Devin
-Devin is a software engineering AI assistant that can browse websites and perform web-based tasks, functioning as a collaborative AI teammate for engineering teams.
-AI Coding Agent
-AI Coding Agent
-Fetches documentation and other resources to help build software
-See More →
 Page 1 of 41
 Next →
```

</details>
