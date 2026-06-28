#!/usr/bin/env python3
import sys
import argparse
import json
import os
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

# ============================================
# モデルキャッシュディレクトリを強制指定
# ============================================
os.environ["PADDLE_PDX_CACHE_HOME"] = "/opt/models/ocr"

# ============================================
# OCR 実行
# ============================================
def run_ocr(ocr, img):
    np_img = np.array(img)
    result = ocr.ocr(np_img)

    lines = []
    if result:
        for line in result:
            text = line[1][0]
            lines.append(text)

    return lines

# ============================================
# 出力フォーマット
# ============================================
def format_output(lines, fmt):
    if fmt == "json":
        return json.dumps({"text": "\n".join(lines)}, ensure_ascii=False, indent=2)

    if fmt == "markdown":
        md = "# OCR Result\n\n"
        for line in lines:
            md += f"- {line}\n"
        return md

    return "\n".join(lines)

# ============================================
# メイン
# ============================================
def main():
    parser = argparse.ArgumentParser(description="PaddleOCR CLI (VL互換仕様)")

    parser.add_argument("--input", type=str, help="Input image file (optional)")
    parser.add_argument("--model-lang", type=str, default="japan", help="OCR language")
    parser.add_argument("--format", type=str, default="json", choices=["json", "markdown", "text"])
    parser.add_argument("--layout", type=str, default="true")
    parser.add_argument("--table", type=str, default="true")
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--output", type=str, help="Output file")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--quiet", action="store_true")

    args = parser.parse_args()

    # 入力画像
    if args.input:
        img = Image.open(args.input)
    else:
        img = Image.open(sys.stdin.buffer)

    # OCR エンジン
    ocr = PaddleOCR(
        use_textline_orientation=True,
        lang=args.model_lang
    )

    # OCR 実行
    lines = run_ocr(ocr, img)

    # 出力整形
    out = format_output(lines, args.format)

    # 出力先
    if args.output:
        with open(args.output, "w") as f:
            f.write(out)
    else:
        print(out)

if __name__ == "__main__":
    main()
