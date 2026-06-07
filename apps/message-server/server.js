import express from "express";
import { createServer } from "node:http";
import { Server } from "socket.io";
import nunjucks from "nunjucks";
import dotenvFlow from "dotenv-flow";
import path from "node:path";
import { fileURLToPath } from "node:url";

import routes from "./routes/index.js";
import messageSocket from "./socket/message.js";

dotenvFlow.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const server = createServer(app);
const io = new Server(server);

// Nunjucks
nunjucks.configure(path.join(__dirname, "views"), {
  autoescape: true,
  express: app,
});

// 静的ファイル
app.use(express.static(path.join(__dirname, "public")));

// ルート登録
app.use("/", routes);

// Socket.IO イベント登録
messageSocket(io);

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`server running at http://localhost:${PORT}`);
});
