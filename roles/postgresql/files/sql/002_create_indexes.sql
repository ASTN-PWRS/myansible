CREATE INDEX idx_ocr_text_tsv
    ON ocr_documents USING GIN (text_tsv);
