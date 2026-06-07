import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
  publicDir: "dummy",

  resolve: {
    alias: {
      "@awesome.me/webawesome/dist-cdn": path.resolve(
        __dirname,
        "node_modules/@awesome.me/webawesome/dist-cdn",
      ),
    },
  },

  optimizeDeps: {
    // ← これが無いと dist-cdn が external 扱いされる
    exclude: ["@awesome.me/webawesome"],
  },

  build: {
    outDir: "public/webawesome",
    emptyOutDir: false,

    lib: {
      entry: "./src/main.js",
      name: "WebAwesomeBundle",
      formats: ["iife"],
      fileName: () => "webawesome.js",
    },

    rollupOptions: {
      external: [],

      output: {
        entryFileNames: "webawesome.js",
        assetFileNames: "webawesome[extname]",
      },
    },
  },
});
