// @ts-check
import { defineConfig } from "astro/config";

export default defineConfig({
  output: "static",
  outDir: "./dist",
  site: "https://tracker.example.com",
  trailingSlash: "ignore",
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
