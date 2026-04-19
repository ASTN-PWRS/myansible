#!/usr/bin/env python3
import os
import json
import redis
import subprocess
import hashlib
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

# ================================
# Redis (Garnet)
# ================================
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# ================================
# OCR モデル準備
# ================================
def ensure_ocr_model():
    """
    PaddleOCR の日本語モデルがローカルに存在しなければ
    初回だけダウンロードする。
    """
    model_dir = os.path.expanduser("~/.paddleocr/whl/japan")
    if not os.path.exists(model_dir):
        print("[OCR] 日本語モデルが見つかりません → 初回ダウンロード開始")
        _ = PaddleOCR(use_angle_cls=True, lang='japan', show_log=False)
        print("[OCR] 日本語モデルのダウンロード完了")
    else:
        print("[OCR] 日本語モデルは既に存在します")

def load_ocr_engine():
    """
    キャッシュ済みモデルをロードして OCR エンジンを返す。
    """
    print("[OCR] モデルロード中…")
    engine = PaddleOCR(
        use_angle_cls=True,
        lang='japan',
        show_log=False
    )
    print("[OCR] モデルロード完了")
    return engine

# ================================
# PDF → PNG（mutool）
# ================================
def pdf_to_images(pdf_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    subprocess.run([
        "mutool", "convert",
        "-o", f"{out_dir}/page-%d.png",
        pdf_path
    ], check=True)

    files = sorted([
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.endswith(".png")
    ])
    return files

# ================================
# OCR 実行
# ================================
def sha256(data: bytes):
    return hashlib.sha256(data).hexdigest()

def run_ocr(ocr_engine, image_path):
    img = Image.open(image_path)
    np_img = np.array(img)

    result = ocr_engine.ocr(np_img, cls=True)

    lines = []
    if result:
        for line in result:
            lines.append(line[1][0])

    text = "\n".join(lines)
    text_hash = sha256(text.encode())
    return text, text_hash

# ================================
# メインループ
# ================================
def main():
    print("[OCR worker] 起動")

    # モデル準備（初回のみダウンロード）
    ensure_ocr_model()

    # モデルロード（毎回ではなく起動時に1回）
    ocr_engine = load_ocr_engine()

    print("[OCR worker] タスク待機中…")

    while True:
        # queue:ocr からタスクを受け取る
        task_id = r.brpop("queue:ocr")[1]
        print(f"[OCR worker] タスク開始: {task_id}")

        r.hset(f"task:{task_id}", "status", "processing")

        pdf_path = f"/tmp/tasks/{task_id}/input.pdf"
        out_dir = f"/tmp/tasks/{task_id}/pages"

        # PDF → PNG
        image_files = pdf_to_images(pdf_path, out_dir)
        total = len(image_files)

        r.hset(f"task:{task_id}", "total_pages", total)

        # 各ページ OCR
        for i, img_path in enumerate(image_files):
            text, text_hash = run_ocr(ocr_engine, img_path)

            # OCR結果を保存
            with open(f"/tmp/tasks/{task_id}/{i+1}.json", "w") as f:
                json.dump({"text": text, "hash": text_hash}, f)

            # embedding worker に渡す
            r.lpush("queue:embed", json.dumps({
                "task_id": task_id,
                "page": i+1
            }))

        print(f"[OCR worker] タスク完了: {task_id}")

if __name__ == "__main__":
    main()
