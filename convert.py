import os
import json
import subprocess
import pypdfium2 as pdfium
from PIL import Image
import base64
import ollama
from datetime import datetime


# ------------------------------------------------------------
# OCR ダミー関数（ここを差し替える）
# ------------------------------------------------------------
def run_ocr_dummy(pil_image):
    return "DUMMY_OCR_TEXT"


# ------------------------------------------------------------
# Word → PDF 変換（LibreOffice）
# ------------------------------------------------------------
def convert_word_to_pdf(input_path, output_path):
    subprocess.run([
        "soffice", "--headless", "--convert-to", "pdf",
        input_path, "--outdir", os.path.dirname(output_path)
    ])
    return output_path


# ------------------------------------------------------------
# 入力ファイルが Word か PDF か判定
# ------------------------------------------------------------
def ensure_pdf(input_path):
    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".pdf":
        return input_path
    elif ext in [".docx", ".doc"]:
        pdf_path = os.path.splitext(input_path)[0] + ".pdf"
        return convert_word_to_pdf(input_path, pdf_path)
    else:
        raise ValueError("Unsupported file type")


# ------------------------------------------------------------
# qwen3-vl（ollama）で画像意味抽出
# ------------------------------------------------------------
def extract_image_meaning(image_bytes):
    prompt = """
    この画像の内容を説明し、以下を返してください:
    - caption（1文）
    - tags（5個）
    - category（1語）
    JSONで返してください。
    """

    res = ollama.chat(
        model="qwen3-vl",
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [image_bytes]
            }
        ]
    )

    try:
        data = json.loads(res["message"]["content"])
        return data.get("caption"), data.get("tags"), data.get("category")
    except:
        return None, None, None


# ------------------------------------------------------------
# PDF → 座標抽出 → OCR → 画像意味抽出 → JSON
# ------------------------------------------------------------
def extract_pdf_structure(pdf_path, doc_id):
    pdf = pdfium.PdfDocument(pdf_path)
    results = []

    for page_index in range(len(pdf)):
        page = pdf[page_index]
        page_height = page.get_height()

        # テキストレイヤー判定
        textpage = page.get_textpage()
        text = textpage.get_text_range().strip()
        text_blocks = textpage.get_text_bboxes()

        # ページ画像（OCR用）
        bitmap = page.render(scale=2)
        pil_image = bitmap.to_pil()

        # テキスト抽出 or OCR（ダミー）
        if len(text_blocks) == 0:
            page_text = run_ocr_dummy(pil_image)
            text_source = "ocr"
        else:
            page_text = text
            text_source = "text_layer"

        # ページ要約（qwen3-vl）
        summary_prompt = "このテキストの内容を短く要約してください。"
        summary_res = ollama.chat(
            model="qwen3-vl",
            messages=[{"role": "user", "content": summary_prompt + "\n" + page_text}]
        )
        page_summary = summary_res["message"]["content"]

        # ------------------------------------------------------------
        # テキストレコード
        # ------------------------------------------------------------
        text_record = {
            "id": f"{doc_id}_page{page_index+1}_text",
            "type": "text",
            "doc_id": doc_id,
            "source_file": pdf_path,
            "page": page_index + 1,
            "text": page_text,
            "text_summary": page_summary,
            "text_source": text_source,
            "lang": "ja",
            "created_at": datetime.now().isoformat(),
            "vectors": {
                "semantic": None
            }
        }
        results.append(text_record)

        # ------------------------------------------------------------
        # 画像レコード
        # ------------------------------------------------------------
        for idx, img in enumerate(page.get_images()):
            x0, y0, x1, y1 = img.bbox

            crop_box = (
                int(x0 * 2),
                int((page_height - y1) * 2),
                int(x1 * 2),
                int((page_height - y0) * 2),
            )

            cropped = pil_image.crop(crop_box)
            img_bytes = pil_image_to_bytes(cropped)

            caption, tags, category = extract_image_meaning(img_bytes)

            image_record = {
                "id": f"{doc_id}_page{page_index+1}_img{idx+1}",
                "type": "image",
                "doc_id": doc_id,
                "source_file": pdf_path,
                "page": page_index + 1,
                "bbox_pdf": [x0, y0, x1, y1],
                "bbox_pixel": list(crop_box),
                "image_caption": caption,
                "image_tags": tags,
                "image_category": category,
                "page_text_summary": page_summary,
                "text_source": text_source,
                "lang": "ja",
                "created_at": datetime.now().isoformat(),
                "vectors": {
                    "semantic": None
                }
            }

            results.append(image_record)

    return results


# ------------------------------------------------------------
# PIL → bytes
# ------------------------------------------------------------
def pil_image_to_bytes(img):
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ------------------------------------------------------------
# メイン処理
# ------------------------------------------------------------
def process_file(input_path, doc_id):
    pdf_path = ensure_pdf(input_path)
    records = extract_pdf_structure(pdf_path, doc_id)

    json_path = os.path.splitext(input_path)[0] + "_structure.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    return json_path


# ------------------------------------------------------------
# 実行例
# ------------------------------------------------------------
if __name__ == "__main__":
    output = process_file("input.docx", doc_id="doc1")
    print("JSON 出力:", output)
