#!/usr/bin/env python3
import sys
import argparse
import json
from pathlib import Path
import tempfile

from paddleocr_vl import VLModel


def read_stdin_to_tempfile():
    """stdin のバイナリを一時ファイルに保存してパスを返す"""
    data = sys.stdin.buffer.read()
    if not data:
        return None

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")
    tmp.write(data)
    tmp.close()
    return tmp.name


def main():
    parser = argparse.ArgumentParser(
        description="PaddleOCR-VL CLI — OCR + Layout + Table + VLM Document Parsing",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # 入力
    parser.add_argument(
        "image",
        nargs="?",
        help="Input image file (omit when piping binary data via stdin)"
    )

    # モデル選択
    parser.add_argument(
        "--model",
        default="PaddleOCR-VL-1.6-base",
        help="Model name (base / large)"
    )

    # 出力フォーマット
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "markdown", "text"],
        help="Output format"
    )

    # 出力ファイル
    parser.add_argument(
        "--output", "-o",
        help="Write output to file instead of stdout"
    )

    # レイアウト解析
    parser.add_argument(
        "--layout",
        default="true",
        choices=["true", "false"],
        help="Enable layout analysis"
    )

    # テーブル解析
    parser.add_argument(
        "--table",
        default="true",
        choices=["true", "false"],
        help="Enable table recognition"
    )

    # 数式解析
    parser.add_argument(
        "--math",
        default="false",
        choices=["true", "false"],
        help="Enable math (LaTeX) recognition"
    )

    # LLM パラメータ
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Max tokens for LLM output"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="LLM temperature (0.0 recommended for OCR)"
    )

    # ログ
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-essential logs"
    )

    args = parser.parse_args()

    # ============================
    # 1) stdin → tempfile
    # ============================
    img_path = None
    if not sys.stdin.isatty():
        img_path = read_stdin_to_tempfile()

    # 引数が優先
    if args.image:
        img_path = args.image

    if not img_path:
        print("No input image. Provide file or pipe binary data.", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"[INFO] Loading model: {args.model}", file=sys.stderr)

    # ============================
    # 2) モデルロード
    # ============================
    model = VLModel.from_pretrained(args.model)

    # ============================
    # 3) 推論
    # ============================
    if args.verbose:
        print(f"[INFO] Running inference on: {img_path}", file=sys.stderr)

    result = model.predict(
        img_path,
        layout=(args.layout == "true"),
        table=(args.table == "true"),
        math=(args.math == "true"),
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        output_format=args.format,
    )

    # ============================
    # 4) 出力
    # ============================
    if args.output:
        Path(args.output).write_text(
            json.dumps(result, ensure_ascii=False, indent=2)
            if args.format == "json"
            else result
        )
    else:
        if args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(result)


if __name__ == "__main__":
    main()
