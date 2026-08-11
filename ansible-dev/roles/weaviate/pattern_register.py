#!/usr/bin/env python3
"""
pattern_register.py
Usage:
  python pattern_register.py --image ./samples/stamp_yamada.png --name "承認印" --category stamp
Environment variables:
  OLLAMA_EMBED_URL, GEMINI_OCR_URL, WEAVIATE_URL
"""

import os
import sys
import json
import base64
import uuid
import argparse
import requests
import time
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Config from env
OLLAMA_EMBED_URL = os.getenv("OLLAMA_EMBED_URL", "http://localhost:11434/api/embed")
GEMINI_OCR_URL = os.getenv("GEMINI_OCR_URL", "http://localhost:11434/api/ocr")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
RETRY_COUNT = int(os.getenv("RETRY_COUNT", "2"))
RETRY_BACKOFF = float(os.getenv("RETRY_BACKOFF", "1.5"))

# Utilities
def gen_id(prefix: str = "pattern") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"

def read_image_as_base64(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    ext = "png" if path.lower().endswith(".png") else "jpeg"
    return f"data:image/{ext};base64," + base64.b64encode(data).decode("utf-8")

def flatten_attributes(attrs: Dict[str, Any]) -> str:
    parts = []
    for k, v in attrs.items():
        if v is None or v == "":
            continue
        if isinstance(v, list):
            parts.append(f"{k}:" + " ".join(map(str, v)))
        elif isinstance(v, dict):
            parts.append(f"{k}:" + " ".join(f"{kk}:{vv}" for kk, vv in v.items()))
        else:
            parts.append(f"{k}:{v}")
    return " ".join(parts)

# HTTP helpers with retry
def post_json(url: str, payload: dict, timeout: int = TIMEOUT) -> dict:
    last_exc = None
    for attempt in range(RETRY_COUNT + 1):
        try:
            r = requests.post(url, json=payload, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_exc = e
            time.sleep(RETRY_BACKOFF * (attempt + 1))
    raise last_exc

# OCR call (best-effort)
def call_ocr(image_base64: str) -> Dict[str, Any]:
    payload = {"image": image_base64, "mode": "stamp_ocr"}
    try:
        j = post_json(GEMINI_OCR_URL, payload)
        return {
            "stamp_name": j.get("stamp_name", "") or "",
            "stamp_department": j.get("stamp_department", "") or "",
            "stamp_date": j.get("stamp_date", "") or "",
            "raw_text": j.get("raw_text", "") or "",
            "confidence": float(j.get("confidence", 0.0))
        }
    except Exception as e:
        print(f"[WARN] OCR failed: {e}", file=sys.stderr)
        return {"stamp_name": "", "stamp_department": "", "stamp_date": "", "raw_text": "", "confidence": 0.0}

# Embedding call
def embed_image(image_base64: str) -> List[float]:
    payload = {"model": "jina/omni-v5", "input": image_base64, "mode": "image", "input_type": "base64"}
    j = post_json(OLLAMA_EMBED_URL, payload)
    if "embedding" in j and isinstance(j["embedding"], list):
        return j["embedding"]
    if "data" in j and isinstance(j["data"], dict) and "embedding" in j["data"]:
        return j["data"]["embedding"]
    raise RuntimeError("Embedding not found in response")

# Weaviate upsert
def upsert_pattern(pattern_id: str, properties: Dict[str, Any], vector: List[float]) -> Dict[str, Any]:
    url = f"{WEAVIATE_URL.rstrip('/')}/v1/objects"
    payload = {"class": "Pattern", "id": pattern_id, "properties": properties, "vector": vector}
    r = requests.post(url, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

# Single-file registration
def register_pattern_from_file(image_path: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    image_base64 = read_image_as_base64(image_path)
    pattern_id = gen_id("pattern")

    # OCR
    ocr = call_ocr(image_base64)

    # Embedding
    embedding = embed_image(image_base64)

    # Build attributes
    attributes = {
        "stamp_name": ocr.get("stamp_name") or meta.get("stamp_name", ""),
        "stamp_department": ocr.get("stamp_department") or meta.get("stamp_department", ""),
        "stamp_date": ocr.get("stamp_date") or meta.get("stamp_date", ""),
        "raw_text": ocr.get("raw_text", ""),
        "stamp_type": meta.get("stamp_type", ""),
        "stamp_shape": meta.get("stamp_shape", ""),
        "stamp_color": meta.get("stamp_color", ""),
        "stamp_layout": meta.get("stamp_layout", "")
    }

    properties = {
        "pattern_id": pattern_id,
        "name": meta.get("name") or pattern_id,
        "category": meta.get("category", "stamp"),
        "description": meta.get("description", ""),
        "image_base64": image_base64,
        "attributes_json": json.dumps(attributes, ensure_ascii=False),
        "attributes_text": flatten_attributes(attributes),
        "tags": meta.get("tags", []),
        "created_by": meta.get("created_by", "cli"),
        "created_at": meta.get("created_at", "")
    }

    res = upsert_pattern(pattern_id, properties, embedding)
    return {"pattern_id": pattern_id, "properties": properties, "weaviate_response": res}

# Batch registration with concurrency
def register_batch(image_paths: List[str], meta_template: Dict[str, Any], max_workers: int = MAX_WORKERS):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(register_pattern_from_file, p, meta_template): p for p in image_paths}
        for fut in as_completed(futures):
            p = futures[fut]
            try:
                out = fut.result()
                print(f"[OK] Registered {p} -> {out['pattern_id']}")
                results.append(out)
            except Exception as e:
                print(f"[ERROR] Failed {p}: {e}", file=sys.stderr)
    return results

# CLI
def main():
    parser = argparse.ArgumentParser(description="Register pattern image(s) to Weaviate")
    parser.add_argument("--image", "-i", help="Single image file")
    parser.add_argument("--dir", "-d", help="Directory of images for batch")
    parser.add_argument("--name", "-n", default=None, help="Pattern name")
    parser.add_argument("--category", "-c", default="stamp", help="Category")
    parser.add_argument("--tags", "-t", nargs="*", default=[], help="Tags")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="Parallel workers for batch")
    args = parser.parse_args()

    meta = {"name": args.name, "category": args.category, "tags": args.tags}

    if args.image:
        out = register_pattern_from_file(args.image, meta)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif args.dir:
        imgs = [os.path.join(args.dir, f) for f in os.listdir(args.dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        register_batch(imgs, meta, max_workers=args.workers)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
