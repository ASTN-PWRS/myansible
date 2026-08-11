# 必要ライブラリ: pypdfium2 pdf2image Pillow requests base64 numpy
import base64, io, json, requests
from pdf2image import convert_from_path
import pypdfium2 as pdfium
from PIL import Image

# Ollama と Weaviate のエンドポイント設定
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
WEAVIATE_URL = "http://localhost:8080"


# ---------------------------------------------------------
# Gemini 2.0 ダミー関数（doc_id 対応版）
# ---------------------------------------------------------
def gemini_process_page_image_dummy(page_number: int, image_base64: str, doc_id: str) -> dict:
    """
    入力: page_number, image_base64, doc_id
    出力: Weaviate投入用の JSON 構造（doc_id を含む）
    """
    return {
        "page_number": page_number,
        "doc_id": doc_id,
        "width": 1240,
        "height": 1754,
        "blocks": [
            {
                "id": f"{doc_id}-p{page_number}-b1",
                "doc_id": doc_id,
                "type": "text",
                "bbox": [100, 120, 1100, 220],
                "text": "ダミーのOCRテキスト",
                "ocr_text": "ダミーのOCRテキスト",
                "caption": "",
                "cells_text": "",
                "image_base64": "",
                "notes": "dummy"
            },
            {
                "id": f"{doc_id}-p{page_number}-fig1",
                "doc_id": doc_id,
                "type": "figure",
                "bbox": [120, 300, 900, 900],
                "text": "",
                "ocr_text": "",
                "caption": "ダミー図",
                "cells_text": "",
                "image_base64": "",  # 実運用では base64 を入れる
                "notes": "dummy"
            }
        ]
    }


# ---------------------------------------------------------
# テキストブロック判定
# ---------------------------------------------------------
def page_has_textblocks(pdf_path, page_index, text_threshold=20):
    pdf = pdfium.PdfDocument(pdf_path)
    page = pdf.get_page(page_index)
    textpage = page.get_textpage()
    blocks = list(textpage.get_text_blocks())
    page.close()
    pdf.close()

    total_chars = sum(len(b[4].strip()) for b in blocks)
    return total_chars >= text_threshold


# ---------------------------------------------------------
# PDFページ → 画像化（Gemini用）
# ---------------------------------------------------------
def page_to_base64_image(pdf_path, page_index, dpi=200):
    images = convert_from_path(pdf_path, dpi=dpi, first_page=page_index+1, last_page=page_index+1)
    buf = io.BytesIO()
    images[0].save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8"), images[0]


# ---------------------------------------------------------
# Gemini 呼び出しラッパー（doc_id 対応）
# ---------------------------------------------------------
def call_gemini_for_page(page_number, image_b64, doc_id):
    # 実運用では Gemini API に POST
    return gemini_process_page_image_dummy(page_number, image_b64, doc_id)


# ---------------------------------------------------------
# Ollama 埋め込み（テキスト）
# ---------------------------------------------------------
def embed_text_with_ollama(text):
    payload = {"model": "jina/omni-v5", "input": text, "mode": "text"}
    r = requests.post(OLLAMA_EMBED_URL, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["embedding"]


# ---------------------------------------------------------
# Ollama 埋め込み（画像 base64）
# ---------------------------------------------------------
def embed_image_with_ollama_base64(image_b64):
    payload = {"model": "jina/omni-v5", "input": image_b64, "mode": "image", "input_type": "base64"}
    r = requests.post(OLLAMA_EMBED_URL, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["embedding"]


# ---------------------------------------------------------
# Weaviate upsert
# ---------------------------------------------------------
def upsert_weaviate_object(class_name, obj_id, properties, vector):
    url = f"{WEAVIATE_URL}/v1/objects"
    payload = {
        "class": class_name,
        "id": obj_id,
        "properties": properties,
        "vector": vector
    }
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------
# メイン処理: PDF をページごとに処理（doc_id 完全対応）
# ---------------------------------------------------------
def process_pdf(pdf_path, doc_id="doc-001"):
    pdf = pdfium.PdfDocument(pdf_path)
    num_pages = len(pdf)
    pdf.close()

    for i in range(num_pages):
        page_number = i + 1

        if page_has_textblocks(pdf_path, i):
            print(f"page {page_number}: text blocks found -> use text path")
            # TODO: pypdfium2 の text block 抽出処理をここに追加
            # embed_text_with_ollama → upsert_weaviate_object
            continue

        # -------------------------
        # テキストなし → Gemini OCR パス
        # -------------------------
        print(f"page {page_number}: no text blocks -> image path")

        image_b64, pil_img = page_to_base64_image(pdf_path, i, dpi=300)

        gemini_json = call_gemini_for_page(page_number, image_b64, doc_id)

        for blk in gemini_json["blocks"]:
            blk_id = blk["id"]

            # block_index の安全抽出
            try:
                block_index = int(blk_id.split("-")[-1].replace("b", "").replace("fig", ""))
            except:
                block_index = 0

            properties = {
                "doc_id": blk["doc_id"],
                "page_number": gemini_json["page_number"],
                "block_index": block_index,
                "type": blk["type"],
                "text": blk.get("text", ""),
                "ocr_text": blk.get("ocr_text", ""),
                "caption": blk.get("caption", ""),
                "cells_text": blk.get("cells_text", ""),
                "bbox": json.dumps(blk.get("bbox", [])),
                "image_base64": blk.get("image_base64", ""),
                "notes": blk.get("notes", "")
            }

            # 埋め込み生成
            if blk["type"] in ("figure", "image", "table") and blk.get("image_base64"):
                emb = embed_image_with_ollama_base64(blk["image_base64"])
            else:
                emb = embed_text_with_ollama(blk.get("text", ""))

            upsert_weaviate_object("Block", blk_id, properties, emb)
