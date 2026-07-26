# worker/search_workflow.py

from services.embed_text_jina import embed_text
from services.embed_siglip2 import embed_image_query
from services.search_qdrant import search_qdrant


def run_search_workflow(params: dict):
    """
    複合検索:
    - テキスト意味検索 (Jina v3)
    - OCRテキスト検索 (Gemini OCR結果もテキストとしてJinaで検索)
    - 画像意味検索 (SigLIP2)
    - 画像分類フィルタ (Florence2 image_type)
    - NOT 条件 (犬の画像など)
    """

    text_query = params.get("text_query")
    image_query = params.get("image_query")
    include_image_types = params.get("include_image_types") or []
    exclude_image_types = params.get("exclude_image_types") or []
    ocr_query = params.get("ocr_query")
    not_image_query = params.get("not_image_query")
    top_k = params.get("top_k", 20)

    # -----------------------------
    # ベクトル生成
    # -----------------------------
    text_vector = embed_text(text_query) if text_query else None
    ocr_vector = embed_text(ocr_query) if ocr_query else None
    image_vector = embed_image_query(image_query) if image_query else None
    not_image_vector = embed_image_query(not_image_query) if not_image_query else None

    # -----------------------------
    # Qdrant 検索条件構築
    # -----------------------------
    must_filters = []
    must_not_filters = []

    if include_image_types:
        must_filters.append({
            "key": "image_type",
            "match": {"any": include_image_types}
        })

    if exclude_image_types:
        must_not_filters.append({
            "key": "image_type",
            "match": {"any": exclude_image_types}
        })

    # -----------------------------
    # ベクトル検索の組み合わせ
    # -----------------------------
    queries = []

    if text_vector is not None:
        queries.append({"name": "text", "vector": text_vector, "top": top_k})

    if ocr_vector is not None:
        queries.append({"name": "text", "vector": ocr_vector, "top": top_k})

    if image_vector is not None:
        queries.append({"name": "image", "vector": image_vector, "top": top_k})

    not_queries = []
    if not_image_vector is not None:
        not_queries.append({"name": "image", "vector": not_image_vector, "top": top_k})

    # -----------------------------
    # Qdrant 検索実行
    # -----------------------------
    results = search_qdrant(
        queries=queries,
        not_queries=not_queries,
        must_filters=must_filters,
        must_not_filters=must_not_filters,
        top_k=top_k
    )

    # -----------------------------
    # 文書単位にまとめる
    # -----------------------------
    docs: dict[int, dict] = {}
    for r in results:
        payload = r["payload"]
        file_id = payload["file_id"]
        filename = payload.get("filename")
        file_url = payload.get("file_url")  # ★ 追加
        page = payload.get("page")
        score = r["score"]
        image_type = payload.get("image_type")
        caption = payload.get("caption")
        text = payload.get("text")

        if file_id not in docs:
            docs[file_id] = {
                "file_id": file_id,
                "filename": filename,
                "file_url": file_url,  # ★ 追加
                "pages": [],
                "scores": [],
                "image_types": [],
                "captions": [],
                "texts": []
            }

        docs[file_id]["pages"].append(page)
        docs[file_id]["scores"].append(score)
        if image_type:
            docs[file_id]["image_types"].append(image_type)
        if caption:
            docs[file_id]["captions"].append(caption)
        if text:
            docs[file_id]["texts"].append(text)

    sorted_docs = sorted(
        docs.values(),
        key=lambda d: max(d["scores"]) if d["scores"] else 0.0,
        reverse=True
    )

    return sorted_docs
