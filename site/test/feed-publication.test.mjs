import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = resolve(siteRoot, "..");
const feedDir = resolve(repoRoot, "content/feed");
const fixtures = [
  ["reported-feed-item.md", "2026-08-30-test-source-agent-access-market.md"],
  ["verified-backfilled-item.md", "2026-07-28-older-verified-protocol-release.md"],
];
const feedItems = fixtures.map(([, destination]) => resolve(feedDir, destination));
const derivedFixtures = [
  ["daily-brief.json", resolve(repoRoot, "data/daily/2026-09-03.json")],
  ["insight-threads.json", resolve(repoRoot, "data/insight-threads.json")],
];
const originalDerived = new Map();

before(async () => {
  await mkdir(feedDir, { recursive: true });
  await mkdir(resolve(repoRoot, "data/daily"), { recursive: true });
  await Promise.all(
    fixtures.map(([source, destination]) =>
      cp(resolve(siteRoot, "test/fixtures", source), resolve(feedDir, destination)),
    ),
  );
  for (const [fixture, destination] of derivedFixtures) {
    try {
      originalDerived.set(destination, await readFile(destination));
    } catch {
      originalDerived.set(destination, null);
    }
    await cp(resolve(siteRoot, "test/fixtures", fixture), destination);
  }
  const build = spawnSync("npm", ["run", "build"], {
    cwd: siteRoot,
    encoding: "utf8",
  });
  assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);
});

after(async () => {
  await Promise.all(feedItems.map((feedItem) => rm(feedItem, { force: true })));
  for (const [, destination] of derivedFixtures) {
    const original = originalDerived.get(destination);
    if (original === null) await rm(destination, { force: true });
    else await writeFile(destination, original);
  }
});

test("reported feed item is readable without becoming a verified development", async () => {
  const home = await readFile(resolve(siteRoot, "dist/index.html"), "utf8");
  const detail = await readFile(
    resolve(siteRoot, "dist/events/test-source-agent-access-market/index.html"),
    "utf8",
  );
  const olderDetail = await readFile(
    resolve(siteRoot, "dist/events/older-verified-protocol-release/index.html"),
    "utf8",
  );
  const developments = await readFile(
    resolve(siteRoot, "dist/developments/index.html"),
    "utf8",
  );
  const rss = await readFile(resolve(siteRoot, "dist/feed.xml"), "utf8");

  assert.match(home, /Agent access develops a market layer/);
  assert.match(home, /Field Ledger/);
  assert.match(home, /Original publication/);
  assert.match(home, /Backfilled/);
  assert.ok(
    home.indexOf("Agent access develops a market layer") <
      home.indexOf("Older verified protocol release"),
    "newer reported item must appear before an older high-importance item",
  );
  assert.match(home, /\breported\b/i);
  assert.match(home, /Today(?:'|’)s Brief/);
  assert.match(home, /September 3, 2026/);
  assert.match(home, /Developing insights/);
  assert.match(home, /Verifiable Agent Identity/);
  assert.match(home, /1 verified development/);
  assert.match(home, /Latest from the field/);
  assert.doesNotMatch(home, /&lt;a href=/);
  assert.doesNotMatch(home, /\]\(https?:\/\//);
  assert.ok(
    home.indexOf("Today’s Brief") < home.indexOf("Latest from the field"),
    "the dated daily brief must precede the historical feed",
  );
  assert.match(home, />Feed</);
  assert.match(home, />Weekly</);
  assert.match(home, />Themes</);
  assert.doesNotMatch(home, /The control plane/);
  assert.match(detail, /Crawler control is expanding beyond allow and block decisions/);
  assert.match(detail, /Why it matters/);
  assert.match(olderDetail, /Backfilled/);
  assert.match(olderDetail, /July 28, 2026/);
  assert.doesNotMatch(developments, /Agent access develops a market layer/);
  assert.match(rss, /\[Backfilled\] Agent access develops a market layer/);
  assert.match(rss, /\[Backfilled\] Older verified protocol release/);
});
