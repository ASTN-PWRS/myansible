#!/usr/bin/env python3
import os
import json
import redis
import psycopg
from psycopg.rows import dict_row
from transformers import AutoTokenizer, AutoModel
import torch

# ================================
# Redis (Garnet)
# ================================
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# ================================
# PostgreSQL
# ================================
conn = psycopg.connect(
    "postgresql://user:pass@localhost/dbname",
    row_factory=dict_row
)

# ================================
# Jina Embeddings v3 モデル準備
# ================================
def ensure_embedding_model():
    """
    Jina Embeddings v3 のモデルキャッシュが無ければ
    初回だけダウンロードする。
    """
    model_dir = os.path.expanduser("~/.cache/huggingface/hub")
    if not os.path.exists(model_dir):
        print("[Embedding] モデルキャッシュがありません → 初回ダウンロード開始")
        _ = AutoTokenizer.from_pretrained("jinaai/jina-embeddings-v3")
        _ = AutoModel.from_pretrained("jinaai/jina-embeddings-v3")
        print("[Embedding] モデルダウンロード完了")
    else:
        print("[Embedding] モデルキャッシュは既に存在します")

def load_embedding_model():
    """
    モデルをロードして tokenizer と model を返す。
    """
    print("[Embedding] モデルロード中…")
    tokenizer = AutoTokenizer.from_pretrained("jinaai/jina-embeddings-v3")
    model = AutoModel.from_pretrained("jinaai/jina-embeddings-v3")
    print("[Embedding] モデルロード完了")
    return tokenizer, model

# ================================
# embedding 生成
# ================================
def embed_text(tokenizer, model, text: str) -> list[float]:
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    emb = outputs.last_hidden_state.mean(dim=1)
    return emb[0].tolist()

# ================================
# PostgreSQL upsert
# ================================
def upsert_page(task_id: str, page: int, text: str, text_hash: str, emb: list[float]):
    sql = """
    INSERT INTO document_pages (
        file_name,
        page_number,
        content,
        content_hash,
        embedding
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (file_name, page_number)
    DO UPDATE SET
        content = EXCLUDED.content,
        content_hash = EXCLUDED.content_hash,
        embedding = EXCLUDED.embedding,
        created_at = now();
    """
    with conn.cursor() as cur:
        cur.execute(sql, (task_id, page, text, text_hash, emb))
    conn.commit()

# ================================
# メインループ
# ================================
def main():
    print("[Embedding worker] 起動")

    # モデル準備（初回のみダウンロード）
    ensure_embedding_model()

    # モデルロード（毎回ではなく起動時に1回）
    tokenizer, model = load_embedding_model()

    print("[Embedding worker] タスク待機中…")

    while True:
        raw = r.brpop("queue:embed")[1]
        job = json.loads(raw)

        task_id = job["task_id"]
        page = job["page"]

        # OCR worker が作った JSON を読む
        json_path = f"/tmp/tasks/{task_id}/{page}.json"
        with open(json_path) as f:
            data = json.load(f)

        text = data["text"]
        text_hash = data["hash"]

        # embedding 生成
        emb = embed_text(tokenizer, model, text)

        # DB upsert
        upsert_page(task_id, page, text, text_hash, emb)

        # 進捗更新
        processed = int(r.hget(f"task:{task_id}", "processed_pages")) + 1
        total = int(r.hget(f"task:{task_id}", "total_pages"))

        r.hset(f"task:{task_id}", mapping={
            "processed_pages": processed,
            "progress": int(processed * 100 / total)
        })

        if processed == total:
            r.hset(f"task:{task_id}", "status", "done")
            print(f"[Embedding worker] タスク完了: {task_id}")

if __name__ == "__main__":
    main()
