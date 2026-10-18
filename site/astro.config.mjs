// @ts-check
import { defineConfig } from "astro/config";

export default defineConfig({
  output: "static",
  outDir: "./dist",
  site: "https://crawlerpolicy.com",
  trailingSlash: "ignore",
  // Feed slugs come from the analysis title, so re-analyzing an item renames
  // it. Keep published links working.
  redirects: {
    "/events/x-discovery-google-expands-news-ai-pilot-to-over-400-outlets":
      "/events/x-discovery-google-expands-news-ai-pilot-licensing-to-over-400-publishers",
    "/events/x-discovery-web-services-block-autonomous-ai-agents-from-openai-meta-and-google":
      "/events/x-discovery-major-web-platforms-and-banks-ramp-up-blocks-against-autonomous-ai-agents",
    "/events/x-discovery-meta-revises-terms-to-remove-clause-interpreted-as-permitting-ai-scraping-of-new":
      "/events/x-discovery-meta-strips-contested-ai-training-language-from-commercial-terms-following-publi",
  },
  build: {
    // 'directory' produces /reading/index.html — plays clean with Vercel's
    // default static serving, which maps /reading → /reading/index.html.
    // 'file' mode required a vercel.json with cleanUrls: true.
    format: "directory",
  },
  vite: {
    server: {
      fs: {
        // Allow reading ../content and ../data (outside site/ subdir).
        allow: [".."],
      },
    },
  },
});
