import os
import json
from paddleocr import PaddleOCR
from libs.pdf_to_images import pdf_to_images

MODEL_DIR = "/opt/models/ocr"

# モデルキャッシュディレクトリを指定
os.environ["PADDLE_PDX_CACHE_HOME"] = MODEL_DIR

ocr = PaddleOCR(
    lang="japan",
    use_textline_orientation=True
)

for i, img in enumerate(pdf_to_images("EO SPACE 取扱説明書.pdf"), start=1):
    result = ocr.ocr(img)

    out_path = f"page_{i}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Saved: {out_path}")
