import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { cp, mkdir, readFile, rm } from "node:fs/promises";
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

before(async () => {
  await mkdir(feedDir, { recursive: true });
  await Promise.all(
    fixtures.map(([source, destination]) =>
      cp(resolve(siteRoot, "test/fixtures", source), resolve(feedDir, destination)),
    ),
  );
  const build = spawnSync("npm", ["run", "build"], {
    cwd: siteRoot,
    encoding: "utf8",
  });
  assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);
});

after(async () => Promise.all(feedItems.map((feedItem) => rm(feedItem, { force: true }))));

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
  assert.match(home, /Today in the ecosystem/);
  assert.match(home, /Latest signals/);
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
