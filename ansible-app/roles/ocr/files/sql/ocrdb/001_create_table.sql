-- 拡張は最初にまとめて
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_bigm;

-- テーブル
CREATE TABLE IF NOT EXISTS document_pages (
    id            SERIAL PRIMARY KEY,
    file_name     TEXT NOT NULL,
    file_hash     TEXT,              -- PDF 全体のハッシュ
    page_number   INTEGER NOT NULL,
    content       TEXT,
    content_hash  TEXT,              -- ページ単位のハッシュ
    embedding     VECTOR(1024),      -- Jina v3
    created_at    TIMESTAMP DEFAULT now()
);

CREATE TABLE tasks (
    task_id      TEXT PRIMARY KEY,
    file_name    TEXT,
    status       TEXT,        -- pending / processing / done / error
    progress     INTEGER,     -- 0〜100
    total_pages  INTEGER,
    processed_pages INTEGER,
    error_message TEXT,
    created_at   TIMESTAMP DEFAULT now(),
    updated_at   TIMESTAMP DEFAULT now()
);

-- 日本語キーワード検索（pg_bigm）
CREATE INDEX IF NOT EXISTS idx_content_bigm
ON document_pages USING GIN (content gin_bigm_ops);

-- embedding 検索用（pgvector）
CREATE INDEX IF NOT EXISTS idx_embedding
ON document_pages USING ivfflat (embedding vector_cosine)
WITH (lists = 100);
