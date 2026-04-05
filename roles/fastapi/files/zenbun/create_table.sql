CREATE TABLE ocr_documents (
    id          SERIAL PRIMARY KEY,
    filename    TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    text        TEXT NOT NULL,
    text_tsv    tsvector GENERATED ALWAYS AS (
        to_tsvector('japanese', text)
    ) STORED,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ocr_text_tsv
    ON ocr_documents USING GIN (text_tsv);
