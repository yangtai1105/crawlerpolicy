# AGENTS.md — Codex repository instructions

Codex reads this file automatically when working in this repository.

The detailed project guide and canonical description of the product, taxonomy,
architecture, pipelines, operations, and invariants is [`CLAUDE.md`](./CLAUDE.md).
Read it completely before changing application or pipeline code. For work related
to the current web-intelligence architecture, also read the design document named
in `CLAUDE.md`.

If documentation and the live repository disagree, inspect the implementation,
tests, generated schemas, and recent Git history before deciding which is current.
When a material project fact has changed, update `CLAUDE.md` in the same change.

## Project map

```text
crawlerpolicy/
├── CLAUDE.md             # canonical project knowledge and operating rules
├── AGENTS.md             # Codex workflow and safety boundaries
├── pipeline/              # collection, evidence, analysis, trends, publishing
├── content/               # evidence, current events, legacy archive, snapshots
├── data/                  # health, trend state, completed intelligence issues
├── entities/              # controlled protocol and player registries
├── site/                  # Astro static publication
├── tests/                 # Python test suite
├── sources.yaml           # source configuration and taxonomy assignments
└── .github/workflows/     # scheduled daily and weekly jobs
```

## Working agreement

- The user normally runs one coding agent at a time in this checkout. Do not
  create or switch branches or worktrees unless the user asks. A session worktree
  explicitly created by Codex or another desktop agent is allowed.
- Before editing, run `git status --short` and inspect relevant unstaged and staged
  diffs. Preserve unrelated and user-authored changes.
- Keep work scoped to the request. Do not opportunistically rewrite generated
  content, historical data, or unrelated modules.
- Do not commit, push, deploy, publish, trigger GitHub Actions, or run scheduled
  production pipelines unless the user explicitly requests that external action.
- Do not change dependencies merely to make local setup easier without explaining
  the need and getting approval.

## Credentials and sensitive operations

- Never print, echo, edit, copy into chat, or commit `.env` values or API keys.
- Treat Anthropic, Gemini, GitHub, Cloudflare, Resend, and deployment credentials
  named in `CLAUDE.md` as secrets even when they are available in the environment.
- Keep secrets out of `AGENTS.md`, `CLAUDE.md`, source files, fixtures, logs, and
  generated content.
- Prefer tests and narrowly scoped dry runs. Any network-backed fetch, workflow
  trigger, production mutation, or publication requires an explicit request.

## Project invariants

Follow the detailed rules in `CLAUDE.md`, especially:

- Persist durable evidence before analysis; failed analysis must remain replayable.
- Use primary or official sources for factual claims and trend movement. Discovery
  commentary cannot independently advance a trend.
- Preserve `event_date`, `published_at`, and `detected_at` as distinct dates.
- Use the canonical track and subject axes. Keep legacy slug compatibility at read
  time rather than rewriting historical content.
- Treat `content/legacy-events/` as read-only archive material and keep it out of
  current intelligence loaders and counts.
- Preserve stage-aware health semantics. Never present a failed attempt as the
  last successful run, and never publish weekly intelligence from critical or
  stale health.
- Controlled entity registries are pipeline inputs; automated pipeline code must
  not silently rewrite them.

## Verification

Run checks proportional to the change and report exactly what ran:

```bash
uv run pytest
uv run ruff check pipeline tests

cd site
npm run check
npm run build
```

- Python-only changes normally require the Python tests and Ruff.
- Site or content-schema changes normally require Astro check and build as well as
  any relevant Python checks.
- Pipeline changes that affect both generated content and site consumption require
  both verification groups.
- Documentation-only or agent-instruction changes do not require full application
  tests; run `git diff --check` and review the complete diff instead.
- Do not claim a check passed unless it was run successfully in the current work.

## Documentation alignment

- `CLAUDE.md` owns shared project facts: product model, architecture, taxonomy,
  source/evidence rules, commands, secrets inventory, and operational invariants.
- `AGENTS.md` owns Codex-specific workflow, safety, and verification behavior.
- When implementation changes a shared project fact, update `CLAUDE.md` in the
  same change. Update `AGENTS.md` only when Codex workflow or safety requirements
  change.
- Link to the canonical owner instead of duplicating long explanations across the
  two files. Review both files for contradictions after either one changes.
