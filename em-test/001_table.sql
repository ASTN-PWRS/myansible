CREATE TABLE ocr_pages (
  id              BIGSERIAL PRIMARY KEY,

  -- 文書単位のID（同じPDF / 規格書をまとめる）
  document_id     BIGINT NOT NULL,

  -- ページ番号（1始まり）
  page_number     INTEGER NOT NULL,

  -- 元ファイル名やパス（任意）
  source_path     TEXT,

  -- 規格番号など（技術規格なら重要）
  standard_code   TEXT,          -- 例: 'JIS A 1304', 'ISO 834'

  -- OCRテキスト（1ページ分）
  content         TEXT NOT NULL,

  -- ベクトル（bge-m3 / Jina v3 など）
  embedding       VECTOR(1024),  -- モデルに合わせて次元数を変更

  -- タイムスタンプ
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);
