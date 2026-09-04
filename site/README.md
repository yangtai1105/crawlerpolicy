# Crawler Policy site

Astro static publication for [crawlerpolicy.com](https://crawlerpolicy.com). Its home page is a date-led reading product: a selective Daily Brief, persistent developing insights, the broader evidence ledger, five intelligence fronts, and weekly synthesis. The Legacy Archive remains clearly separated.

## Local development

Run from this directory:

```bash
npm ci
npm run check
npm run dev
```

The dev server opens at `http://localhost:4321`. Production verification is:

```bash
npm run check
npm run build
npm run preview
```

## Data boundaries

- `../content/events` supplies current developments.
- `../content/legacy-events` supplies archive pages only.
- `../data/intelligence` supplies completed weekly issues.
- `../data/daily` supplies the latest dated Daily Brief, including quiet editions.
- `../data/insight-threads.json` supplies evidence-linked interpretations that persist across daily runs.
- `../data/trends.json` supplies persistent trend state.
- `../data/health.json` supplies stage-aware pipeline status.
- `../sources.yaml` supplies source metadata and coverage.

Do not merge legacy events into current counts, front pages, trend calculations, or intelligence issues. If health is stale or not schema-compatible, render it as `unknown`; the footer only shows a timestamp for the last fully successful run.

## Main routes

- `/` — latest Daily Brief, developing insights, and recent evidence
- `/intelligence` and `/intelligence/{week}` — weekly issues
- `/fronts/{front}` — exactly five canonical fronts
- `/developments` — current schema-v2 developments
- `/sources` and `/sources/{slug}` — coverage and evidence context
- `/archive` — preserved schema-v1 events and old reading dispatches
- `/about` — methodology and editorial model
