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
  build: {
    outDir: "/var/www/share/webawesome",
    emptyOutDir: false,

    lib: {
      entry: "./src/main.js",
      name: "WebAwesomeBundle",
      formats: ["iife"],
      fileName: () => "webawesome.js",
    },

    rollupOptions: {
      external: [], // ← これが重要（強制バンドル）
      output: {
        entryFileNames: "webawesome.js",
        assetFileNames: "webawesome[extname]",
      },
    },
  },

  plugins: [],
});
