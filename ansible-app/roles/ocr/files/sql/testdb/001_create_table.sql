-- 拡張は最初にまとめて
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_bigm;

-- テーブル
CREATE TABLE IF NOT EXISTS document_pages (
    id            SERIAL PRIMARY KEY,
    file_name     TEXT NOT NULL,
    page_number   INTEGER NOT NULL,
    content       TEXT,
    embedding     VECTOR(1536),
    created_at    TIMESTAMP DEFAULT now()
);

-- インデックス（冪等）
CREATE INDEX IF NOT EXISTS idx_content_bigm
ON document_pages
USING GIN (content gin_bigm_ops);
