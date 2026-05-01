-- ベクトル検索用（pgvector）
CREATE INDEX ocr_pages_embedding_hnsw_idx
  ON ocr_pages
  USING hnsw (embedding vector_cosine_ops);

-- 日本語テキスト検索用（pg_bigm）
CREATE EXTENSION IF NOT EXISTS pg_bigm;

CREATE INDEX ocr_pages_content_bigm_idx
  ON ocr_pages
  USING gin (content gin_bigm_ops);

-- 文書単位で絞り込みたい場合
CREATE INDEX ocr_pages_document_idx
  ON ocr_pages (document_id);

-- 規格番号で絞り込みたい場合（技術規格向け）
CREATE INDEX ocr_pages_standard_code_idx
  ON ocr_pages (standard_code);
