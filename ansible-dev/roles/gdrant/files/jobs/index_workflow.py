# worker/workflow.py

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

# PDF画像抽出
from services.extract_images import extract_images
from services.classify_florence2 import classify_image
from services.embed_siglip2 import embed_image

# PDFテキスト抽出
from services.extract_text import extract_text
from services.embed_text_jina import embed_text_v5_text_small

# 保存処理
from services.save_postgres import save_file_meta, save_image_meta, save_text_chunks
from services.save_qdrant import save_vectors

# Markdown utils
from services.md_utils import (
    extract_headings,
    markdown_to_plain,
    extract_md_images
)


# -----------------------------
# 日本語向けチャンク分割
# -----------------------------
def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", "、", " "]
    )
    return splitter.split_text(text)


# -----------------------------
# メイン workflow
# -----------------------------
def run_index_workflow(params):
    file_path = params["file_path"]
    category = params["category"]
    department = params["department"]

    filename = os.path.basename(file_path)
    file_url = f"https://docs.example.com/{filename}"

    # PostgreSQL: files 登録
    file_id = save_file_meta(file_path, category, department)

    # ---------------------------------------------------------
    # ① Markdownファイルの場合（拡張子で判定）
    # ---------------------------------------------------------
    if filename.lower().endswith(".md"):
        md_text = open(file_path, "r", encoding="utf-8").read()

        # 見出し
        headings = extract_headings(md_text)

        # ★ Markdown画像抽出
        md_images = extract_md_images(md_text)

        # -----------------------------
        # Markdown画像 → SigLIP2 / Florence2 / Qdrant
        # -----------------------------
        image_vectors = []
        image_payloads = []
        image_meta_rows = []

        for img in md_images:
            img_path = img["path"]
            alt_text = img["alt"]

            # Florence2 で分類
            meta = classify_image(img_path)

            # SigLIP2 でベクトル
            vector = embed_image(img_path)

            image_meta_rows.append({
                "file_id": file_id,
                "page": None,
                "image_type": meta.get("type"),
                "objects": meta.get("objects"),
                "caption": meta.get("caption") or alt_text,
                "path": img_path
            })

            image_vectors.append(vector)
            image_payloads.append({
                "file_id": file_id,
                "filename": filename,
                "file_url": file_url,
                "type": "image_markdown",
                "page": None,
                "image_type": meta.get("type"),
                "objects": meta.get("objects"),
                "caption": meta.get("caption") or alt_text
            })

        if image_meta_rows:
            save_image_meta(image_meta_rows)
            save_vectors(image_vectors, image_payloads, prefix=f"mdimg_{file_id}_")

        # -----------------------------
        # Markdown本文 → テキストインデックス
        # -----------------------------
        plain = markdown_to_plain(md_text)
        chunks = chunk_text(plain)

        vectors = []
        payloads = []
        meta_rows = []

        for idx, chunk in enumerate(chunks):
            vector = embed_text_v5_text_small(chunk)

            meta_rows.append({
                "file_id": file_id,
                "chunk_index": idx,
                "page": None,
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

        return {"file_id": file_id, "filename": filename, "file_url": file_url}

    # ---------------------------------------------------------
    # ② PDFなど通常ファイルの処理（元の前半を完全復元）
    # ---------------------------------------------------------

    # -----------------------------
    # PDF画像抽出
    # -----------------------------
    images = extract_images(file_path)

    image_vectors = []
    image_payloads = []
    image_meta_rows = []

    for page, img_path in images:
        meta = classify_image(img_path)
        vector = embed_image(img_path)

        image_meta_rows.append({
            "file_id": file_id,
            "page": page,
            "image_type": meta.get("type"),
            "objects": meta.get("objects"),
            "caption": meta.get("caption"),
            "path": img_path
        })

        image_vectors.append(vector)
        image_payloads.append({
            "file_id": file_id,
            "filename": filename,
            "file_url": file_url,
            "type": "image",
            "page": page,
            "image_type": meta.get("type"),
            "objects": meta.get("objects"),
            "caption": meta.get("caption")
        })

    save_image_meta(image_meta_rows)
    save_vectors(image_vectors, image_payloads, prefix=f"img_{file_id}_")

    # -----------------------------
    # PDFテキスト抽出
    # -----------------------------
    text = extract_text(file_path)
    chunks = chunk_text(text)

    text_vectors = []
    text_payloads = []
    text_meta_rows = []

    for idx, chunk in enumerate(chunks):
        vector = embed_text_v5_text_small(chunk)

        text_meta_rows.append({
            "file_id": file_id,
            "chunk_index": idx,
            "page": None,
            "text": chunk
        })

        text_vectors.append(vector)
        text_payloads.append({
            "file_id": file_id,
            "filename": filename,
            "file_url": file_url,
            "type": "text",
            "chunk_index": idx,
            "page": None,
            "text": chunk
        })

    save_text_chunks(text_meta_rows)
    save_vectors(text_vectors, text_payloads, prefix=f"text_{file_id}_")

    return {"file_id": file_id, "filename": filename, "file_url": file_url}
