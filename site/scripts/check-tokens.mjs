#!/usr/bin/env node
// Fails when a var(--token) reference has no definition in :root.
// CSS silently ignores undefined custom properties, so a token rename
// breaks styling with a green build and no error. This is the guard.
//
// What this does NOT check: scope. Every "--token:" declaration found in
// any file — whether it sits in :root or inside one component's local,
// scoped selector block — is added to the same single global `defined`
// set. A reference to that name from a completely different component
// will therefore pass this check even though the token would not actually
// resolve at runtime there. This script can only tell you a name was
// declared *somewhere*, never that it is in scope *where it's used*.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, extname } from "node:path";

const ROOT = new URL("../src", import.meta.url).pathname;
const GLOBAL_CSS = join(ROOT, "styles/global.css");

const strip = (t) => t.replace(/\/\*[\s\S]*?\*\//g, "");

function walk(dir) {
  return readdirSync(dir).flatMap((entry) => {
    const full = join(dir, entry);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

const rootBlock = strip(readFileSync(GLOBAL_CSS, "utf8")).match(/:root\s*\{([\s\S]*?)\n\}/);
if (!rootBlock) {
  console.error("Could not find a :root block in styles/global.css");
  process.exit(1);
}
const defined = new Set([...rootBlock[1].matchAll(/(?:^|[{;])\s*(--[\w-]+)\s*:/gm)].map((m) => m[1]));

// Tokens may also be defined locally on a selector, and often on the same
// line as it (`.feed-card { --rail: …; display: grid; … }`), so a
// declaration is anything preceded by line start, `{`, or `;` — not just
// line start.
const files = walk(ROOT).filter((f) => [".astro", ".css", ".ts"].includes(extname(f)));
for (const file of files) {
  const text = strip(readFileSync(file, "utf8"));
  for (const m of text.matchAll(/(?:^|[{;])\s*(--[\w-]+)\s*:/gm)) defined.add(m[1]);
}

const missing = new Map();
for (const file of files) {
  const text = strip(readFileSync(file, "utf8"));
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
