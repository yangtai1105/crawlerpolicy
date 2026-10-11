# Editorial Restyle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Field Ledger visual direction with Editorial — warm off-white ground, serif display type, generous leading — across all 14 routes, without touching any content or pipeline logic.

**Architecture:** Token adoption in this codebase is 98% (622 `var(--…)` references against 13 hardcoded hex values), so rewriting the `:root` token set in `site/src/styles/global.css` cascades the new palette to nearly every surface. Three further passes finish it: the nav/footer and the 13 hardcoded values, the nine components' scoped style blocks, and the two things that make the site *read* dead regardless of styling — the quiet-day hero and a degraded health notice caused by five permanently failing sources.

**Tech Stack:** Astro 6, scoped `<style>` blocks, CSS custom properties, `@fontsource` self-hosted fonts (no CDN).

**Spec:** `docs/superpowers/specs/2026-10-10-agentic-map-layer-design.md` §8.2

## Global Constraints

- Editorial direction, from spec §8.2: "Warm off-white ground, serif display type for headlines and stances, IBM Plex Sans for body and data, a single restrained accent for change markers and links."
- Spec §8.2's two mockup-validated concessions, both already shipped and to be preserved: status cells are rounded capsules rather than hard squares, and the matrix first column carries a `short_descriptor` line. Do not revert either.
- "Status colour must stay distinguishable without relying on hue alone; the five statuses differ in lightness as well as hue, and the change marker is an outline rather than a colour swap."
- **Nothing under `content/`, `data/`, or `entities/` may be modified.** This is a presentation change.
- **No pipeline Python may be modified** except `sources.yaml` in Task 5, which is config.
- Fonts stay self-hosted via `@fontsource`. No CDN links, no `fonts.googleapis.com` — the site must build and render offline.
- `npm run check` and `npm run build` must be clean before every commit.
- No hardcoded hex colours outside `:root` when the work is done.
- Do not push. Commit on a feature branch.

## Why a restyle still needs verification

A restyle has no unit tests, and a passing build proves almost nothing: CSS silently ignores an undefined custom property and falls back to the inherited or initial value, so renaming a token breaks styling with a green build and no error. That is the same silent-failure class that cost sub-project 1 a Critical finding. Task 1 therefore ships a script, `site/scripts/check-tokens.mjs`, that fails when any referenced token is undefined, and every later task re-runs it.

## File Structure

| File | Responsibility |
|---|---|
| `site/package.json` (modify) | Add the self-hosted serif dependency |
| `site/src/layouts/Base.astro` (modify) | Import the serif face alongside the existing Plex imports |
| `site/src/styles/global.css` (modify) | The Editorial token set, base typography, nav, footer |
| `site/scripts/check-tokens.mjs` (create) | Fails on any `var(--x)` with no definition in `:root`; the restyle's only real test |
| `site/src/pages/index.astro` (modify) | 9 hardcoded colours; the dark hero block reworked for a light ground; quiet-day hero |
| `site/src/pages/events/[slug].astro` (modify) | 2 hardcoded colours |
| `site/src/components/FeedCard.astro` (modify) | 2 hardcoded status rail colours |
| `site/src/components/*.astro` (modify) | Eight further scoped style blocks tuned to the new tokens |
| `sources.yaml` (modify) | Task 5 only: disable the five permanently failing `xai_search` sources |

---

### Task 1: Editorial token set, serif face, and the token checker

Rewriting `:root` is the single highest-leverage change in this plan: with 622 token references it restyles every page at once. The token checker ships in the same task because the rename is exactly what can break styling silently.

**Files:**
- Modify: `site/package.json`
- Modify: `site/src/layouts/Base.astro`
- Modify: `site/src/styles/global.css`
- Create: `site/scripts/check-tokens.mjs`

**Interfaces:**
- Consumes: nothing (first task)
- Produces: the full Editorial token set on `:root`, every name listed below; `node scripts/check-tokens.mjs` run from `site/`, exiting non-zero with a list when any referenced token is undefined

- [ ] **Step 1: Write the token checker first, and watch it pass on the current tree**

Create `site/scripts/check-tokens.mjs`:

```js
#!/usr/bin/env node
// Fails when a var(--token) reference has no definition in :root.
// CSS silently ignores undefined custom properties, so a token rename
// breaks styling with a green build and no error. This is the guard.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, extname } from "node:path";

const ROOT = new URL("../src", import.meta.url).pathname;
const GLOBAL_CSS = join(ROOT, "styles/global.css");

function walk(dir) {
  return readdirSync(dir).flatMap((entry) => {
    const full = join(dir, entry);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

const rootBlock = readFileSync(GLOBAL_CSS, "utf8").match(/:root\s*\{([\s\S]*?)\n\}/);
if (!rootBlock) {
  console.error("Could not find a :root block in styles/global.css");
  process.exit(1);
}
const defined = new Set([...rootBlock[1].matchAll(/^\s*(--[\w-]+)\s*:/gm)].map((m) => m[1]));

// Tokens may also be defined locally on a selector (e.g. --rail on a card).
const files = walk(ROOT).filter((f) => [".astro", ".css", ".ts"].includes(extname(f)));
for (const file of files) {
  const text = readFileSync(file, "utf8");
  for (const m of text.matchAll(/^\s*(--[\w-]+)\s*:/gm)) defined.add(m[1]);
}

const missing = new Map();
for (const file of files) {
  const text = readFileSync(file, "utf8");
  for (const m of text.matchAll(/var\(\s*(--[\w-]+)/g)) {
    if (!defined.has(m[1])) {
      if (!missing.has(m[1])) missing.set(m[1], new Set());
      missing.get(m[1]).add(file.replace(ROOT, "src"));
    }
  }
}

if (missing.size) {
  console.error(`Undefined CSS custom properties (${missing.size}):`);
  for (const [token, where] of [...missing].sort()) {
    console.error(`  ${token} — referenced in ${[...where].join(", ")}`);
  }
  process.exit(1);
}
console.log(`All var(--token) references resolve. ${defined.size} tokens defined.`);
```

Add the script to `site/package.json`'s `scripts` block:

```json
    "check:tokens": "node scripts/check-tokens.mjs",
```

- [ ] **Step 2: Run it against the current, unmodified tree**

Run: `cd site && npm run check:tokens`
Expected: PASS — it reports all references resolving. This proves the checker works on a known-good tree before you change anything. If it reports anything missing now, stop and report it: that is a pre-existing bug, not something you introduced.

- [ ] **Step 3: Add the serif face**

The Editorial mockup was rendered in a system serif stack (`Iowan Old Style`, `Palatino`, Georgia). That reproduces exactly what was approved on macOS but renders as Georgia or a platform default elsewhere. Self-host instead, so every reader sees the same publication:

```bash
cd site && npm install @fontsource-variable/source-serif-4
```

In `site/src/layouts/Base.astro`, add alongside the existing `@fontsource` imports at the top (keep all four current imports):

```js
import "@fontsource-variable/source-serif-4/index.css";
```

**Note for the reviewer and the project owner:** Source Serif 4 is a substitution for the Iowan Old Style the mockup displayed. Both are text serifs of moderate contrast and the character of the direction is preserved, but it is not pixel-identical to what was approved. This is the one judgement call in this plan that is purely a matter of taste — it is a one-line change to swap for another `@fontsource` serif (`newsreader`, `spectral`, `libre-baskerville`, `eb-garamond`) or to fall back to the system stack.

- [ ] **Step 4: Replace the `:root` token block**

In `site/src/styles/global.css`, replace the entire `:root { … }` block (currently lines 2-68) with the following. Every token name currently referenced anywhere in `src/` is retained so nothing breaks; the Field Ledger names are kept as aliases pointing at Editorial values, because 17 references to `--pillar-*`, 9 to `--trace-violet` and 3 to `--evidence-mint` live in the frozen `reading/*` archive pages and `subscribe.astro`, and remapping them is cheaper and safer than editing archive pages.

```css
:root {
  /* Editorial — warm off-white ground, serif display, one restrained accent */
  --paper-warm: #fbfaf6;
  --paper-tint: #f3f1ea;
  --paper-high: #ffffff;
  --ink: #1a1a18;
  --ink-body: #3a3a34;
  --ink-muted: #5a5a54;
  --ink-faint: #8a7f6d;
  --rule: #e3dfd3;
  --rule-strong: #c9c3b2;
  --accent: #9c3a1e;
  --accent-soft: #e0c4b8;

  /* Surfaces */
  --bg: var(--paper-warm);
  --bg-elev: var(--paper-high);
  --bg-hover: var(--paper-tint);
  --ink-dim: var(--ink-muted);
  --border: var(--rule);
  --border-strong: var(--rule-strong);
  --focus: var(--accent);

  /* Status — differ in lightness as well as hue (spec §8.2) */
  --status-shipped: #2f6b4e;
  --status-preview: #9dbfa9;
  --status-stated: #d8b47e;
  --status-declined: #c9a79c;
  --status-none: #e7e3d7;
  --status-healthy: #2f6b4e;
  --status-degraded: #a9762c;
  --status-critical: #9c3a1e;
  --status-unknown: var(--ink-faint);
  --signal-hot: var(--accent);
  --signal-cool: var(--ink-faint);

  /* Field Ledger names kept as aliases — referenced by the frozen
     reading/* archive pages and subscribe.astro. Do not delete. */
  --field-paper: var(--paper-warm);
  --ledger-ink: var(--ink);
  --forest-block: #2f4a3c;
  --clay-marker: var(--accent);
  --evidence-mint: var(--status-preview);
  --quiet-rule: var(--rule-strong);
  --protocol-blue: var(--status-shipped);
  --trace-violet: var(--ink-faint);
  --alert-red: var(--accent);
  --pillar-crawler: var(--status-shipped);
  --pillar-ecosystem: var(--ink-faint);
  --pillar-agent: var(--status-stated);
  --paper: var(--ink);
  --muted: var(--ink-muted);
  --dim: var(--ink-faint);
  --cyan: var(--status-shipped);
  --violet: var(--forest-block);
  --pink: var(--accent);
  --amber: var(--status-stated);
  --night: var(--forest-block);
  --surface: var(--paper-high);
  --surface-high: var(--paper-tint);

  /* Type */
  --font-display: "Source Serif 4 Variable", "Iowan Old Style", Palatino, Georgia, serif;
  --font-body: "IBM Plex Sans Variable", "Helvetica Neue", sans-serif;
  --font-mono: "IBM Plex Mono", "SFMono-Regular", monospace;

  /* Space and measure — unchanged */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;
  --space-9: 96px;
  --content-w: 1240px;
  --sidebar-w: 300px;
  --radius-sm: 2px;
  --radius-md: 3px;
  color-scheme: light;
}
```

- [ ] **Step 5: Rewrite the base typography**

Still in `global.css`, replace the `body` rule and the `h1, h2, h3, h4` rules (currently lines 69-94) with:

```css
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink-body);
  font-family: var(--font-body);
  font-size: 1rem;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

h1, h2, h3, h4 {
  margin: 0;
  color: var(--ink);
  font-family: var(--font-display);
  font-weight: 400;
  line-height: 1.15;
  letter-spacing: -0.014em;
  text-wrap: balance;
}

h1 { font-size: clamp(2.1rem, 4.2vw, 3.6rem); }
h2 { font-size: clamp(1.5rem, 2.4vw, 2.1rem); }
h3 { font-size: clamp(1.2rem, 1.6vw, 1.5rem); }
h4 { font-size: 1.05rem; }

p { margin: 0 0 var(--space-4); max-width: 68ch; }
a { color: inherit; text-decoration: none; }
a:hover { color: var(--accent); }
```

The display sizes come down substantially from Field Ledger's `clamp(2.65rem, 6vw, 5.75rem)`: a serif at 5.75rem reads as a poster, and Editorial is a publication. Keep the `prefers-reduced-motion` block and the two existing `@media` breakpoints at the end of the file as they are.

- [ ] **Step 6: Run the checker, then the build**

Run: `cd site && npm run check:tokens && npm run check && npm run build`
Expected: the checker reports all references resolving; `astro check` 0 errors; build completes 215 pages. If the checker names any token, you removed something still in use — add it back as an alias rather than editing the page that uses it.

- [ ] **Step 7: Commit**

```bash
cd ~/Documents/Claude/Skills/ai-ecosystem-tracker
git add site/package.json site/package-lock.json site/src/layouts/Base.astro \
        site/src/styles/global.css site/scripts/check-tokens.mjs
git commit -m "feat: replace Field Ledger tokens with the Editorial set

Warm off-white ground, Source Serif 4 for display, one restrained clay
accent. Field Ledger token names are kept as aliases pointing at
Editorial values because 29 references live in the frozen reading/*
archive pages and subscribe.astro, where remapping is safer than editing
archived pages.

Adds scripts/check-tokens.mjs, which fails when a var(--token) reference
has no definition. CSS silently ignores undefined custom properties, so a
token rename otherwise breaks styling with a green build and no error."
```

---

### Task 2: Nav, footer, and the thirteen hardcoded colours

Thirteen hex values sit outside `:root` and would stay Field-Ledger green against the new warm ground. Nine of them are in one dark hero block on the homepage, which has to be rethought rather than recoloured: a near-black panel was the Field Ledger lead treatment, and Editorial leads with type on paper.

**Files:**
- Modify: `site/src/styles/global.css` (nav and footer rules)
- Modify: `site/src/pages/index.astro` (9 values, the `.lead-signal` block)
- Modify: `site/src/pages/events/[slug].astro` (2 values)
- Modify: `site/src/components/FeedCard.astro` (2 values)

**Interfaces:**
- Consumes: the Editorial tokens from Task 1
- Produces: zero hardcoded hex outside `:root`, verified by the grep in Step 5

- [ ] **Step 1: Restyle the nav and footer**

**Preserve layout mechanics; change only appearance.** The current nav carries behaviour a restyle must not touch: `.site-nav` is `position: sticky; z-index: 50; top: 0`, and `.site-nav-inner` is `display: grid` with a three-column template and `min-height: 76px`. The `@media (max-width: 900px)` block at the end of the file positions the nav with `grid-template-columns`, `grid-column` and `grid-row`, so switching to flex would silently turn all three into no-ops and stop the links wrapping to a second row below 900px — while dropping `position: sticky` would stop the masthead sticking. Neither shows up on a desktop build or in `astro check`.

So keep every structural and behavioural property and restyle only border colour and weight, background, type, and the link treatment. Replace the `.site-nav*`, `.brand*`, and `.site-footer*` rules (currently lines 103-129) with:

```css
.site-nav {
  position: sticky;
  z-index: 50;
  top: 0;
  border-bottom: 1px solid var(--ink);
  background: var(--bg);
}
.site-nav-inner {
  min-height: 76px;
  display: grid;
  grid-template-columns: minmax(230px, 0.9fr) minmax(0, 2fr) auto;
  gap: var(--space-5);
  align-items: center;
}
.brand-lockup { display: flex; flex-direction: column; gap: 2px; }
.site-nav .brand { font: 400 1.45rem/1.1 var(--font-display); letter-spacing: -0.014em; color: var(--ink); }
.brand-descriptor { color: var(--ink-faint); font: 400 0.62rem/1.4 var(--font-body); letter-spacing: 0.04em; text-transform: uppercase; }
.site-nav .links { display: flex; gap: clamp(14px, 2vw, 30px); align-items: center; color: var(--ink-muted); font: 400 0.84rem var(--font-body); letter-spacing: 0.01em; }
.site-nav .links a { padding-block: 6px; border-bottom: 1.5px solid transparent; }
.site-nav .links a:hover { color: var(--ink); border-bottom-color: var(--accent); }
.site-nav .links a[aria-current="page"] { color: var(--ink); border-bottom-color: var(--accent); }
.nav-rss { color: var(--accent); font: 400 0.78rem var(--font-body); }

.site-footer { margin-top: var(--space-9); padding: var(--space-6) 0 var(--space-7); border-top: 1px solid var(--rule-strong); background: var(--paper-tint); color: var(--ink-muted); font-size: 0.82rem; }
.footer-grid { display: grid; grid-template-columns: minmax(200px, 1fr) 2fr 1fr; gap: var(--space-6); align-items: start; }
.site-footer p { margin: 0; max-width: none; }
.footer-status strong, .site-footer strong { color: var(--ink); font-weight: 600; }
.footer-links { display: flex; gap: var(--space-4); justify-content: flex-end; }
```

Two changes carry the Editorial signal: the masthead's 4px forest-green top border is gone and its bottom border becomes a single hairline in full ink, and the condensed-sans wordmark becomes the serif. Both cost nothing structurally.

**Verify the behaviour survived** — a green build will not tell you:

```bash
cd site && npm run build
grep -o 'position:sticky\|position: sticky' dist/index.html | head -1
grep -o 'display:grid\|display: grid' dist/index.html | head -1
grep -o '@media (max-width: *900px)' dist/index.html | head -1
```

Expected: all three present. Then resize a browser below 900px on `npm run dev` and confirm the nav links still occupy their own row.

- [ ] **Step 2: Rework the homepage lead block for a light ground**

`site/src/pages/index.astro` styles `.lead-signal` as a dark panel. Line 181 is the panel itself:

```css
  .lead-signal { position: relative; padding: clamp(28px, 3.5vw, 48px); border: 1px solid var(--forest-block); border-radius: var(--radius-md); background: var(--forest-block); color: var(--paper-high); box-shadow: 10px 10px 0 var(--clay-marker); }
```

and lines 182-195 carry nine hardcoded light-on-dark colours (`#c3d2c8`, `#b6dcc7`, `#efb7a7`, `#e7c28d`, `#e4ece7`, `#efaa97`, `#486052`). Replace line 181 **and** that whole group with a light treatment that carries emphasis through type and a heavy top rule instead of a filled panel and a hard shadow. Note that the `box-shadow`, the `background`, the `color` and the `border-radius` all go — a 10px offset shadow is a Field Ledger gesture, not an Editorial one:

```css
  .lead-signal { position: relative; padding: var(--space-6) 0 var(--space-7); border-top: 3px solid var(--ink); border-bottom: 1px solid var(--rule); background: transparent; color: var(--ink-body); }
  .lead-signal h2 { max-width: 30ch; margin: var(--space-4) 0 var(--space-5); font-size: clamp(1.9rem, 3.2vw, 3.1rem); }
  .lead-meta { display: flex; flex-wrap: wrap; gap: var(--space-3); color: var(--ink-faint); font: 400 0.72rem var(--font-body); letter-spacing: 0.08em; text-transform: uppercase; }
  .lead-status { color: var(--status-shipped); font-weight: 600; }
  .lead-signal[data-status="reported"] .lead-status { color: var(--ink-muted); }
  .lead-signal[data-status="signal"] .lead-status { color: var(--status-degraded); }
  .lead-reading > div > p:last-child { max-width: 62ch; color: var(--ink-body); font-size: 1.05rem; }
  .lead-why .utility-label { color: var(--accent); }
  .lead-signal footer { display: flex; justify-content: space-between; gap: var(--space-5); align-items: end; margin-top: var(--space-7); padding-top: var(--space-4); border-top: 1px solid var(--rule); }
  .lead-signal footer > a { color: var(--accent); font: 400 0.84rem var(--font-body); border-bottom: 1px solid var(--accent-soft); white-space: nowrap; }
```

Also replace the `.insight-section` background on line 208 — `background: #dce5df` becomes `background: var(--paper-tint)`.

If `.lead-signal` sets a dark `background` or `color` anywhere else in that file, remove it: the block is light now, and a leftover dark background with light text removed is unreadable. Search the file for `lead-signal` and check every rule.

- [ ] **Step 3: Fix the two event-page values**

`site/src/pages/events/[slug].astro` lines 169 and 171 style the evidence block as light-on-dark using `#dce8e0` and `#b6dcc7` over `var(--forest-block)`. Keep the dark evidence block — it is a deliberate, bounded accent and it still reads on paper — but take its colours from tokens:

```css
  .event-page-body :global(h2:nth-of-type(5) ~ *) { margin-top: 0; margin-bottom: 0; padding: 0 var(--space-6) var(--space-4); background: var(--forest-block); color: var(--paper-tint); }
  .event-page-body :global(h2:nth-of-type(5) ~ * a) { color: var(--status-preview); text-decoration: underline; }
```

- [ ] **Step 4: Fix the two FeedCard status rails**

`site/src/components/FeedCard.astro` lines 63-64 hardcode the rail colours. Replace with the status tokens:

```css
  .feed-card[data-status="verified"] { --rail: var(--status-shipped); }
  .feed-card[data-status="signal"] { --rail: var(--status-degraded); }
```

- [ ] **Step 5: Fix the hardcoded border on `pre`**

`site/src/styles/global.css:124` is a hardcoded hex inside the stylesheet itself:

```css
pre { overflow-x: auto; padding: var(--space-4); border: 1px solid #486052; border-radius: var(--radius-sm); background: var(--forest-block); color: var(--paper-high); }
```

Keep the dark treatment — a code block reads well dark, and this plan already decided the event page's evidence block stays dark — but take the border from a token so the palette lives in one place:

```css
pre { overflow-x: auto; padding: var(--space-4); border: 1px solid var(--forest-block); border-radius: var(--radius-sm); background: var(--forest-block); color: var(--paper-tint); }
```

- [ ] **Step 6: Verify no hardcoded colour remains, then build**

The plan's Global Constraints forbid hardcoded hex outside `:root`. Checking only `src/components`, `src/layouts` and `src/pages` cannot see `global.css`, where the `pre` rule above lives — so check the stylesheet too, excluding its `:root` block, where hex values are the whole point:

```bash
cd site
echo "— components, layouts, pages —"
grep -rn "#[0-9a-fA-F]\{3,6\}\b" src/components src/layouts src/pages
echo "— global.css outside :root —"
awk '/^:root \{/{inroot=1} inroot&&/^\}/{inroot=0; next} !inroot' src/styles/global.css | grep -n "#[0-9a-fA-F]\{3,6\}\b"
```

Expected: no output from either. Any hit is a colour that will not follow the palette.

Then run: `npm run check:tokens && npm run check && npm run build`
Expected: all clean, 215 pages.

- [ ] **Step 7: Commit**

```bash
cd ~/Documents/Claude/Skills/ai-ecosystem-tracker
git add site/src/styles/global.css site/src/pages/index.astro \
        site/src/pages/events/\[slug\].astro site/src/components/FeedCard.astro
git commit -m "feat: restyle nav and footer, remove hardcoded colours

The masthead gains a full-ink hairline rule and a serif wordmark. The
homepage lead block drops its dark panel for type on paper with a heavy
top rule, which is how Editorial carries emphasis. All thirteen hex
values outside :root now come from tokens, so the palette is in one
place."
```

---

### Task 3: Component style pass

Nine components carry scoped style blocks written for Field Ledger's dense, mono-labelled look. Under Editorial tokens they will render in the right colours but the wrong register: heavy borders where there should be hairlines, mono uppercase where there should be small-caps serif or plain sans, and tight leading.

**Files:**
- Modify: `site/src/components/DevelopmentCard.astro`
- Modify: `site/src/components/FeedCard.astro`
- Modify: `site/src/components/FrontCard.astro`
- Modify: `site/src/components/TrackTag.astro`
- Modify: `site/src/components/HealthStrip.astro`
- Modify: `site/src/components/InsightThreadCard.astro`
- Modify: `site/src/components/TrendTable.astro`
- Modify: `site/src/components/EvidenceRail.astro`
- Modify: `site/src/components/IntelligenceIssue.astro`
- Modify: `site/src/pages/index.astro` (Step 6 only — two legacy-alias text colours)
- Modify: `site/src/pages/subscribe.astro` (Step 6 only — one legacy-alias text colour)
- Modify: `site/src/pages/reading/index.astro` (Step 6 only — one legacy-alias text colour)
- Modify: `site/src/pages/reading/[week].astro` (Step 6 only — one legacy-alias text colour)

**Interfaces:**
- Consumes: the Editorial tokens from Task 1; the hardcoded-colour removals from Task 2
- Produces: no new exports; visual only

- [ ] **Step 1: Apply these four rules to every component's style block, one component at a time**

Work through the nine files in the order listed. For each, apply the same four transformations and nothing else — do not restructure markup, rename classes, or change what data a component renders:

1. **Headings to the serif.** Any `h2`/`h3`/`h4` or title-ish class whose `font` shorthand names `var(--font-display)` keeps it (that token is now the serif). Any that names `var(--font-body)` or a sans stack for a *heading* switches to `var(--font-display)` with `font-weight: 400`.
2. **Labels from mono to sans.** Field Ledger set small uppercase labels in `var(--font-mono)`. Editorial sets them in `var(--font-body)` at `0.72rem`, `letter-spacing: 0.08em`, `text-transform: uppercase`, `color: var(--ink-faint)`. Keep `var(--font-mono)` only where the content is genuinely machine data: timestamps, counts, evidence ids, slugs.
3. **Borders to hairlines.** `2px`/`3px` borders become `1px solid var(--rule)`, except a single deliberate emphasis rule per component (a card's top rule, a table's header rule), which becomes `1px solid var(--ink)` or keeps a 3px left rail where it encodes status.
4. **Status chips to capsules.** Any status pill or tag gets `border-radius: 9px` and a token background from the `--status-*` set. Spec §8.2 requires status to be distinguishable without hue alone, so a chip must also differ in text weight or lightness, not only fill colour.

**Worked example — `TrackTag.astro`.** This is the highest-traffic component (it renders on nearly every card), and it shows all four rules at once. Its current style block is:

```css
  .track-tag {
    display: inline-flex;
    align-items: center;
    min-height: 25px;
    padding: 3px 8px;
    border: 1px solid var(--border-strong);
    border-radius: 2px;
    background: transparent;
    color: var(--ink-muted);
    font: 500 0.61rem/1.2 var(--font-mono);
    letter-spacing: 0.015em;
  }
  a.track-tag:hover { color: var(--clay-marker); border-color: var(--clay-marker); }
```

Replace it with:

```css
  .track-tag {
    display: inline-flex;
    align-items: center;
    min-height: 24px;
    padding: 3px 10px;
    border: 1px solid var(--rule);
    border-radius: 9px;
    background: var(--paper-high);
    color: var(--ink-muted);
    font: 400 0.74rem/1.2 var(--font-body);
    letter-spacing: 0.01em;
    white-space: nowrap;
  }
  a.track-tag:hover { color: var(--accent); border-color: var(--accent-soft); }
```

The changes, rule by rule: mono becomes sans at a readable size (0.61rem in a mono face is a machine label; 0.74rem in Plex Sans is a word a reader can take in); the border drops from `--border-strong` to a hairline `--rule`; the radius becomes the 9px capsule spec §8.2 locks in; and a paper-white fill separates the tag from the page ground now that the ground is warm rather than white. Apply the same reasoning to the other eight components.

- [ ] **Step 2: After each component, run the checker and build**

Run after every single file, not once at the end: `cd site && npm run check:tokens && npm run build`
Expected: clean each time. Building after each component means a regression is attributable to one file instead of nine.

- [ ] **Step 3: Confirm the two preserved concessions survived**

Spec §8.2 locks two details that already shipped. Verify both still hold after your pass:

```bash
cd site && npm run build
grep -o 'border-radius:9px\|border-radius: 9px' dist/intelligence/2026-W35/index.html | head -2
grep -c 'class="track-tag"' dist/intelligence/2026-W35/index.html
```

Expected: capsule radius present on status chips, and the track-tag count on that page is still **9** — the count sub-project 1 restored. A drop to 7 means a style change broke the render condition.

- [ ] **Step 4: Re-run the standing output checks**

```bash
cd site
for f in dist/intelligence/*/index.html; do printf "%s %s\n" "$(basename $(dirname $f))" "$(grep -c 'class="track-tag"' $f)"; done
printf "access-discovery %s\n" "$(grep -c 'class="development-card"' dist/fronts/access-discovery/index.html)"
printf "agents-identity  %s\n" "$(grep -c 'class="development-card"' dist/fronts/agents-identity/index.html)"
```

Expected: six issues at 9 each; 16 and 14 cards. These are the numbers the branch established — a change here means a restyle broke a filter or a guard.

- [ ] **Step 5: Fix five legacy-alias text colours that fail contrast on the new ground**

Task 1 retained the Field Ledger token names as aliases pointing at Editorial values. Where those aliases feed a *border*, the new values are fine — a hairline rule needs no text contrast. Where they feed `color` on a light ground, five sites now fail WCAG. These were measured against `--bg` (`#fbfaf6`), and the two offending tokens resolve to `--evidence-mint` → `#7aa88b` (2.58:1) and `--pillar-agent` → `#dbb987` (1.78:1):

| File and line | Rule | Current ratio |
|---|---|---|
| `site/src/pages/subscribe.astro:105` | `.form-status[data-state="ok"] { color: var(--pillar-agent); }` | **1.78:1** |
| `site/src/pages/index.astro:190` | `.lead-reading .utility-label { color: var(--evidence-mint); }` | 2.58:1 |
| `site/src/pages/index.astro:183` | `.lead-meta span + span::before { … color: var(--evidence-mint); content: "·"; }` | 2.58:1 |
| `site/src/pages/reading/[week].astro:84` | `.item-tag { color: var(--pillar-agent); … }` | 1.78:1 |
| `site/src/pages/reading/index.astro:147` | `color: var(--pillar-agent);` | 1.78:1 |

Repoint each `color` to a token that clears 4.5:1 on `--bg`, choosing by what the element means rather than by what looks closest:

- `subscribe.astro:105` is a success message a reader must read → `var(--status-shipped)` (#2f6b4e, 6.03:1).
- `index.astro:190` is a label → `var(--accent)` (#9c3a1e, 6.62:1), which is the Editorial accent and already used for labels elsewhere in that block.
- `index.astro:183` is a decorative `·` separator, not meaningful text, so WCAG does not require 4.5:1 — but an invisible separator makes the meta line run together. Use `var(--rule-strong)`, which is the token for visible-but-quiet marks.
- Both `reading/*` sites are tags → `var(--status-shipped)` (6.03:1).

**On touching `reading/*`:** this plan treats those pages as frozen archive and does not restyle their layouts. Changing one `color` property is not a layout change, and leaving 1.78:1 text on a route that is still served would be the worse outcome. Change only the `color` value on the two lines named above; touch nothing else in those files.

**Fix exactly the five lines in the table above and nothing else.** Do not run a repository-wide contrast sweep to find more: a blanket "every `color:` token must clear 4.5:1 against `--bg`" check is background-blind and wrong here. Several elements deliberately sit on dark panels — the event page's evidence block (`events/[slug].astro:168-171`) and part of `subscribe.astro` are light-on-dark by design, and Task 2 kept them that way — so such a sweep inverts their verdict and reports them as failures. Acting on it would turn readable light-on-dark text into dark-on-dark. The five sites in the table were identified by hand, each classified by the CSS property it feeds and by its element's actual background.

Verify your five changes by resolving each new token and computing its ratio against `#fbfaf6`, and paste the result into your report:

```bash
cd ~/Documents/Claude/Skills/ai-ecosystem-tracker/site
python3 - <<'PY'
import re
def lin(c):
    c/=255
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def lum(h):
    r,g,b=(int(h[i:i+2],16) for i in (1,3,5))
    return 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b)
def ratio(a,b):
    x,y=lum(a),lum(b); hi,lo=max(x,y),min(x,y)
    return (hi+0.05)/(lo+0.05)
css=open('src/styles/global.css').read()
def resolve(n,d=0):
    m=re.search(rf'^\s*--{re.escape(n)}:\s*([^;]+);',css,re.M)
    if not m or d>6: return None
    v=m.group(1).strip()
    if v.startswith('#'): return v
    a=re.match(r'var\(\s*--([\w-]+)\s*\)',v)
    return resolve(a.group(1),d+1) if a else None
for t in ('status-shipped','accent','rule-strong'):
    v=resolve(t)
    print(f"  --{t:14} {v}  {ratio(v,'#fbfaf6'):5.2f}:1  on --bg")
PY
```

Expected: `--status-shipped` and `--accent` both clear 4.5:1; `--rule-strong` does not, which is correct for the decorative `·` separator and must be stated as such in your report rather than silently accepted.

Then confirm the two tokens you removed no longer appear as a `color` anywhere:

```bash
cd ~/Documents/Claude/Skills/ai-ecosystem-tracker/site
grep -rn "color:[[:space:]]*var(--evidence-mint)\|color:[[:space:]]*var(--pillar-agent)" src/
```

Expected: no output. Both tokens stay defined in `:root` — they are still used for borders, which need no text contrast.

- [ ] **Step 6: Commit**

```bash
cd ~/Documents/Claude/Skills/ai-ecosystem-tracker
git add site/src/components/ site/src/pages/index.astro site/src/pages/subscribe.astro \
        site/src/pages/reading/index.astro site/src/pages/reading/\[week\].astro
git commit -m "feat: move component styles into the Editorial register

Headings to the serif, small labels from mono to sans except where the
content is machine data, heavy borders down to hairlines with one
deliberate emphasis rule per component, status chips to capsules that
differ in weight as well as hue. No markup or data changes."
```

---

### Task 4: Stop the homepage leading with nothing

The site reads empty on a quiet day because the first thing on the homepage is `Today's Brief` followed by "No material development cleared the bar today." That is accurate and it is the least informative sentence available, sitting in the most prominent position. 40 feed cards sit below it.

Spec §8.1's dual-entry homepage fixes this structurally with a persistent field-state band, but that band needs `positions.json`, which does not exist until sub-project 2. This task is the interim fix within the existing data.

**Files:**
- Modify: `site/src/pages/index.astro`

**Interfaces:**
- Consumes: the Editorial tokens and the reworked `.lead-signal` from Tasks 1-2
- Produces: no new exports

- [ ] **Step 1: Read the existing data flow**

The relevant lines in `site/src/pages/index.astro` are already known:

```js
const events = (await loadCurrentEvents()).filter((event) => event.data.change_kind === "material");  // line 21
const feedItems = await loadFeedItems();                                                              // line 22
const dailyItems = brief ? /* today's edition, mapped to feed records */ : feedItems.filter((item) => !item.data.backfilled).slice(0, 5);
const lead = dailyItems[0];                                                                           // line 29
```

(The `dailyItems` ternary is abbreviated above for readability — read lines 24-29 in the file for its real body. You do not need to change it.)

and the branch at lines 105-110:

```astro
    ) : (
      <section class="quiet-edition">
        <div><p class="utility-label">Quiet edition</p><h2>No material development cleared the bar today.</h2></div>
        <p>{brief?.note ?? "The monitoring window is open. New items will appear after the next successful source check."} Recent signals and developing insights remain available below.</p>
      </section>
    )}
```

So `lead` is `undefined` whenever today's edition has no items, and `feedItems` — all 49 published records — is already in scope. No new data source is needed.

- [ ] **Step 2: Add the fallback lead**

After `const lead = dailyItems[0];` (line 29), add:

```js
// Quiet-day fallback: when today's edition is empty, lead with the most
// recent published record instead of a notice. The page otherwise opens on
// "nothing happened" while 40 live records sit below it.
const fallbackLead = lead
  ? undefined
  : (feedItems.find((item) => !item.data.backfilled) ?? feedItems[0]);
const displayLead = lead ?? fallbackLead;
const isQuietDay = !lead && Boolean(displayLead);
```

Then repoint the template at `displayLead`: change `{lead ? (` to `{displayLead ? (` and every `lead.data.…` inside that branch to `displayLead.data.…`. **`statusLabel` is derived from `lead` further up the file — find it and repoint it at `displayLead` too**, or the status chip will render from the wrong record.

Inside the lead block, above the `<h2>`, add the quiet-day note so the reader is never misled into thinking a three-day-old development is today's news:

```astro
          {isQuietDay && (
            <p class="quiet-note">
              No new material development today · leading with the most recent, from <TimeAgo date={displayLead.data.event_date} />
            </p>
          )}
```

`TimeAgo` is already imported in this file; confirm the import exists before using it, and check whether its prop is named `date` by reading `site/src/components/TimeAgo.astro` — use whatever name that component actually declares.

Style the note alongside the other `.lead-*` rules:

```css
  .quiet-note { margin: 0 0 var(--space-3); color: var(--ink-faint); font: 400 0.78rem var(--font-body); letter-spacing: 0.02em; }
```

Keep the existing `quiet-edition` section as the final fallback for when `displayLead` is also undefined — that is the genuinely empty case, and it should still say so.

- [ ] **Step 3: Verify both branches render**

```bash
cd site && npm run build
grep -o "No new material development today[^<]*" dist/index.html | head -1
grep -c 'class="development-card"\|class="feed-card"' dist/index.html
```

Expected: the one-line note appears (today is a quiet day, so this is the branch under test), and the homepage card count is at least as high as before — 40 feed cards was the pre-change figure.

- [ ] **Step 4: Commit**

```bash
cd ~/Documents/Claude/Skills/ai-ecosystem-tracker
git add site/src/pages/index.astro
git commit -m "feat: lead the homepage with the latest development on quiet days

The quiet-day edition put 'No material development cleared the bar
today' in the most prominent position on the page, above 40 live feed
items, so the publication read empty whenever a day was slow. The lead
now falls back to the most recent material development with its real
date, and the quiet state becomes a one-line note."
```

---

### Task 5: Clear the degraded health notice

The homepage carries a visible `Updates delayed` notice because pipeline health is `degraded`, and it has been every day since 2026-09-04. The cause is five `xai_search` sources whose `XAI_API_KEY` was never set: `discovery` reports `status: unavailable, sources_configured: 5, sources_completed: 0, sources_failed: 5`, with 36+ consecutive failures each. The project owner decided to shelve the X discovery lane, so the honest configuration is to disable those sources rather than leave them failing.

This is config, not styling, but it belongs to the same goal: a visitor currently reads that the publication is degraded before reading any of its content.

**Files:**
- Modify: `sources.yaml`

**Interfaces:**
- Consumes: nothing
- Produces: no code interfaces; health returns to `healthy` on the next run if no other stage degrades

- [ ] **Step 1: Confirm the five sources and the current health state**

```bash
cd ~/Documents/Claude/Skills/ai-ecosystem-tracker
.venv/bin/python -c "
import json; d=json.load(open('data/health.json'))
print('status:', d.get('status')); print('discovery:', d.get('discovery'))"
grep -n "x-access-discovery\|x-agents-discovery\|x-rights-discovery\|x-governance-discovery\|x-measurement-discovery" sources.yaml
```

Expected: `status: degraded`, `discovery.sources_failed: 5`, and five source slugs listed.

- [ ] **Step 2: Disable the five sources**

For each of the five `xai_search` entries in `sources.yaml` — `x-access-discovery`, `x-agents-discovery`, `x-rights-discovery`, `x-governance-discovery`, `x-measurement-discovery` — add `enabled: false` as a sibling of `slug`. Leave every other field in place, including `shadow: true`, `query`, and `x_handles`: the lane is being switched off, not deleted, so it can be re-enabled by flipping one line per source once an `XAI_API_KEY` exists.

Add a comment above the group recording why:

```yaml
  # Disabled 2026-10-11: XAI_API_KEY was never configured, so these five
  # sources failed on every run from 2026-09-04 onward and held pipeline
  # health at `degraded`, which surfaces an "Updates delayed" notice to
  # readers. Re-enable by setting the secret and flipping `enabled`.
```

- [ ] **Step 3: Verify the config still loads and the source count drops**

```bash
cd ~/Documents/Claude/Skills/ai-ecosystem-tracker
uv run python -c "
from pipeline.sources import load_sources
s = load_sources('sources.yaml')
on = [x for x in s if x.enabled]
print('total:', len(s), 'enabled:', len(on))
print('xai still enabled:', [x.slug for x in on if x.type == 'xai_search'])"
uv run pytest -q 2>&1 | tail -1
```

Expected: the loader accepts the file, `xai still enabled` is an empty list, and the Python suite still passes. If `load_sources` takes different arguments, adapt the call — read its signature rather than guessing.

- [ ] **Step 4: Commit**

```bash
git add sources.yaml
git commit -m "chore: disable the five X discovery sources

XAI_API_KEY was never configured, so all five xai_search sources failed
on every run from 2026-09-04 onward, holding health at degraded and
showing readers an 'Updates delayed' notice. Config, query and handle
lists are preserved so the lane can be re-enabled by setting the secret
and flipping one line per source."
```

---

## Verification

The whole restyle is green when all of these pass from the repository root:

```bash
uv run pytest -q
uv run ruff check pipeline tests
cd site && npm run check:tokens && npm run check && npm run build
```

Plus the output checks that guard against silent regressions:

```bash
cd site
grep -rn "#[0-9a-fA-F]\{3,6\}\b" src/components src/layouts src/pages | grep -v "^src/styles"   # expect nothing
for f in dist/intelligence/*/index.html; do grep -c 'class="track-tag"' $f; done                 # expect 9 six times
grep -c 'class="development-card"' dist/fronts/access-discovery/index.html                       # expect 16
grep -c 'class="development-card"' dist/fronts/agents-identity/index.html                        # expect 14
```

And one judgement that no script can make: open the built site and look at it. `npm run dev` serves at `http://localhost:4321`. A restyle is not done because the build is green; it is done when the pages read as one publication.

## What this plan deliberately does not do

- No matrix page, protocol page, or player page — those need `positions.json` from sub-project 2.
- No persistent field-state band on the homepage — same dependency. Task 4 is the interim fix for the same symptom.
- No reading-layer rendering — sub-project 2 produces the readings.
- No content or pipeline changes beyond disabling five dead sources.
- The `reading/*` legacy archive pages are restyled only by token inheritance; their layouts are frozen archive material and are not touched.
