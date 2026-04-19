---
slug: cloudflare-ai-search-ships-wrangler-cli-namespace-for-instance-management
title: "Cloudflare AI Search ships wrangler CLI namespace for instance management"
source: cf-changelog-ai-search
pillar: agent
detected_at: 2026-04-01T08:00:00+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-04-01-ai-search-wrangler-commands/"
change_kind: material
importance: 0.72
---

## News

[Cloudflare AI Search now supports a `wrangler ai-search` command namespace](https://developers.cloudflare.com/changelog/post/2026-04-01-ai-search-wrangler-commands/) for CLI-based management of search instances. The rollout includes seven core commands: `create`, `list`, `get`, `update`, `delete`, `search`, and `stats`, allowing users to manage instances interactively or via flags, query instances directly from the CLI, and export structured JSON output for programmatic use.

## Why it matters

This addition lowers friction for developers integrating AI Search into CI/CD pipelines and AI agents, complementing the [recent CSS content selectors feature](https://developers.cloudflare.com/changelog/post/2026-04-08-ai-search-css-content-selectors/) (released four days later) that expanded crawler data source control. Together, these updates signal Cloudflare's focus on developer ergonomics and automation-first workflows in the AI Search product line. The `--json` output specifically enables direct consumption by downstream AI agents, a meaningful step toward seamless agent-infrastructure integration. This follows Cloudflare's broader pattern of hardening API/CLI developer experiences in agent-adjacent products, though the ecosystem impact remains bounded to Cloudflare's own platform footprint.

