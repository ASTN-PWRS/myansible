#!/usr/bin/env python3
import os
import subprocess
import json
import redis
import hashlib
import numpy as np
from PIL import Image
from pdf2image import convert_from_path

# ================================
# Redis (Garnet)
# ================================
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# ================================
# PDF → PNG（pdf2image）
# ================================
def pdf_to_images(pdf_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    # PDF → PIL.Image のリスト
    pages = convert_from_path(pdf_path, dpi=300)

    image_files = []
    for i, page in enumerate(pages, start=1):
        out_path = os.path.join(out_dir, f"page-{i}.png")
        page.save(out_path, "PNG")
        image_files.append(out_path)

    return image_files

# ================================
# OCR 実行
# ================================

def sha256(data: bytes):
    return hashlib.sha256(data).hexdigest()

def run_ocr(image_path):
    """
    /usr/local/bin/paddleocr を subprocess で実行して OCR を行う。
    CLI は JSON を返す前提。
    """
    try:
        result = subprocess.run(
            ["/usr/local/bin/paddleocr", "--input", image_path, "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("[OCR] CLI 実行エラー:", e.stderr)
        return "", sha256(b"")

    # JSON パース
    try:
        data = json.loads(result.stdout)
        text = data.get("text", "")
    except Exception as e:
        print("[OCR] JSON パースエラー:", e)
        text = ""

    text_hash = sha256(text.encode())
    return text, text_hash

# ================================
# メインループ
# ================================
def main():
    print("[OCR worker] 起動")

    print("[OCR worker] タスク待機中…")

    while True:
        task_id = r.brpop("queue:ocr")[1]
        print(f"[OCR worker] タスク開始: {task_id}")

        pdf_path = f"/tmp/tasks/{task_id}/input.pdf"
        out_dir = f"/tmp/tasks/{task_id}/pages"

        # PDF → PNG
        image_files = pdf_to_images(pdf_path, out_dir)

        # 各ページ OCR（CLI 呼び出し）
        for i, img_path in enumerate(image_files):
            text, text_hash = run_ocr(img_path)

            with open(f"/tmp/tasks/{task_id}/{i+1}.json", "w") as f:
                json.dump({"text": text, "hash": text_hash}, f)

            r.lpush("queue:embed", json.dumps({
                "task_id": task_id,
                "page": i+1
            }))

        print(f"[OCR worker] タスク完了: {task_id}")

if __name__ == "__main__":
    main()
