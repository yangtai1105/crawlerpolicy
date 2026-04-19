// @ts-check
import { defineConfig } from "astro/config";

export default defineConfig({
  output: "static",
  outDir: "./dist",
  site: "https://tracker.example.com",
  trailingSlash: "never",
  build: {
    format: "file",
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
