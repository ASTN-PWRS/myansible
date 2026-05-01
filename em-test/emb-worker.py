from sentence_transformers import SentenceTransformer
import psycopg
from pgvector.psycopg import register_vector
import json
import time

# =========================
# 設定
# =========================
MODEL_PATH = "/opt/models/bge-m3/current"
BATCH_SIZE = 16
QUEUE_NAME = "queue:embedding"

DB_DSN = "dbname=yourdb user=user password=pass host=localhost"

# =========================
# モデルロード（1回だけ）
# =========================
model = SentenceTransformer(MODEL_PATH)

# ウォームアップ
model.encode(["warmup"])

# =========================
# DB接続
# =========================
conn = psycopg.connect(DB_DSN)
conn.autocommit = False

# pgvector対応
register_vector(conn)

# =========================
# queue（ダミー：実装に置き換えて）
# =========================
def garnet_pop(queue_name):
    """
    ここは実際のGarnet/RedisのBLPOP等に置き換える
    例: BLPOP queue:embedding 0
    """
    time.sleep(0.1)
    return None


# =========================
# batch取得
# =========================
def pop_batch(n=BATCH_SIZE):
    jobs = []
    for _ in range(n):
        job = garnet_pop(QUEUE_NAME)
        if not job:
            break
        jobs.append(job)
    return jobs


# =========================
# メイン処理
# =========================
def process_jobs(jobs):
    texts = []
    ids = []

    # --- パース ---
    for job in jobs:
        try:
            data = json.loads(job)
            texts.append(data["text"])
            ids.append(data["id"])
        except Exception as e:
            print(f"[WARN] invalid job: {e}")

    if not texts:
        return

    # --- embedding ---
    embeddings = model.encode(texts, batch_size=BATCH_SIZE)

    # --- DB更新 ---
    try:
        with conn.cursor() as cur:
            cur.executemany(
                """
                UPDATE ocr_pages
                SET embedding = %s,
                    updated_at = now()
                WHERE id = %s
                  AND embedding IS NULL
                """,
                [(emb, doc_id) for emb, doc_id in zip(embeddings, ids)]
            )

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] batch failed: {e}")


# =========================
# メインループ
# =========================
def main():
    print("[INFO] embedding worker started")

    while True:
        try:
            jobs = pop_batch()

            if jobs:
                process_jobs(jobs)
            else:
                time.sleep(0.2)  # 無駄CPU防止

        except Exception as e:
            print(f"[FATAL] loop error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()