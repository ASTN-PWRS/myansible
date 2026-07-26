from services.md_utils import extract_headings, markdown_to_plain, extract_md_images

def index_markdown(file_path, file_id, filename, file_url):

    md_text = open(file_path, "r", encoding="utf-8").read()

    # 見出し抽出
    headings = extract_headings(md_text)

    # プレーンテキスト化
    plain = markdown_to_plain(md_text)

    # チャンク化
    chunks = chunk_text(plain)

    vectors = []
    payloads = []
    meta_rows = []

    for idx, chunk in enumerate(chunks):
        vector = embed_text_v5_text_small(chunk)

        meta_rows.append({
            "file_id": file_id,
            "chunk_index": idx,
            "text": chunk
        })

        payloads.append({
            "file_id": file_id,
            "filename": filename,
            "file_url": file_url,
            "type": "markdown",
            "chunk_index": idx,
            "headings": headings,
            "text": chunk
        })

        vectors.append(vector)

    save_text_chunks(meta_rows)
    save_vectors(vectors, payloads, prefix=f"md_{file_id}_")
