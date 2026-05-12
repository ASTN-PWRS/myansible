import { Client } from "pg";

const client = new Client({
  connectionString: process.env.DATABASE_URL,
});

await client.connect();

client.on("notification", (msg) => {
  console.log("Channel name", msg.channel);
  console.log("Users table updated:", msg.payload);

  // JSON に変換
  const data = JSON.parse(msg.payload);

  // ここで好きな処理を実行
  // 例: worker に渡す、キャッシュ更新、WebSocket 送信など
});

// チャンネルを LISTEN
await client.query("LISTEN users_updated");

console.log("Waiting for users table updates...");
