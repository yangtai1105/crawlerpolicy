import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { cp, mkdir, readFile, rm } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = resolve(siteRoot, "..");
const fixture = resolve(siteRoot, "test/fixtures/reported-feed-item.md");
const feedDir = resolve(repoRoot, "content/feed");
const feedItem = resolve(feedDir, "2026-08-30-test-source-agent-access-market.md");

before(async () => {
  await mkdir(feedDir, { recursive: true });
  await cp(fixture, feedItem);
  const build = spawnSync("npm", ["run", "build"], {
    cwd: siteRoot,
    encoding: "utf8",
  });
  assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);
});

after(async () => {
  await rm(feedItem, { force: true });
});

test("reported feed item is readable without becoming a verified development", async () => {
  const home = await readFile(resolve(siteRoot, "dist/index.html"), "utf8");
  const detail = await readFile(
    resolve(siteRoot, "dist/events/test-source-agent-access-market/index.html"),
    "utf8",
  );
  const developments = await readFile(
    resolve(siteRoot, "dist/developments/index.html"),
    "utf8",
  );
  const rss = await readFile(resolve(siteRoot, "dist/feed.xml"), "utf8");

  assert.match(home, /Agent access develops a market layer/);
  assert.match(home, /\breported\b/i);
  assert.match(detail, /Crawler control is expanding beyond allow and block decisions/);
  assert.match(detail, /Why it matters/);
  assert.doesNotMatch(developments, /Agent access develops a market layer/);
  assert.match(rss, /\[Reported\] Agent access develops a market layer/);
});
