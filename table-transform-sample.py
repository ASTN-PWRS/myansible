#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# uv add torch pillow transformers
# uv add torch pillow transformers numpy huggingface_hub

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForObjectDetection

# ---------------------------------------------------------
#  Table Transformer モデル読み込み
# ---------------------------------------------------------
MODEL_ID = "microsoft/table-transformer-detection"
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForObjectDetection.from_pretrained(MODEL_ID)

# ---------------------------------------------------------
#  入力画像
# ---------------------------------------------------------
IMAGE_PATH = "static/sample_pdf_04.webp"
image = Image.open(IMAGE_PATH).convert("RGB")

# ---------------------------------------------------------
#  推論（テーブル検出）
# ---------------------------------------------------------
inputs = processor(images=image, return_tensors="pt")
with torch.no_grad():
    outputs = model(**inputs)

result = processor.post_process_object_detection(
    outputs,
    threshold=0.5,
    target_sizes=[image.size[::-1]]
)[0]

print("=== Table Detection Result ===")
for score, label, box in zip(result["scores"], result["labels"], result["boxes"]):
    box = [round(float(x), 2) for x in box]
    print(f"label={label}, score={float(score):.3f}, box={box}")

# ---------------------------------------------------------
#  Structure Recognition モデル
# ---------------------------------------------------------
STRUCT_MODEL_ID = "microsoft/table-transformer-structure-recognition"
struct_model = AutoModelForObjectDetection.from_pretrained(STRUCT_MODEL_ID)

inputs2 = processor(images=image, return_tensors="pt")
with torch.no_grad():
    outputs2 = struct_model(**inputs2)

structure = processor.post_process_object_detection(
    outputs2,
    threshold=0.5,
    target_sizes=[image.size[::-1]]
)[0]

print("\n=== Structure Result (rows, columns, spanning) ===")
for score, label, box in zip(structure["scores"], structure["labels"], structure["boxes"]):
    box = [round(float(x), 2) for x in box]
    print(f"label={label}, score={float(score):.3f}, box={box}")

# ---------------------------------------------------------
#  bbox の交差領域を計算する関数
# ---------------------------------------------------------
def intersect_bbox(row, col):
    x1 = max(row[0], col[0])
    y1 = max(row[1], col[1])
    x2 = min(row[2], col[2])
    y2 = min(row[3], col[3])
    if x2 > x1 and y2 > y1:
        return [round(x1,2), round(y1,2), round(x2,2), round(y2,2)]
    return None

# ---------------------------------------------------------
#  行・列・結合セルを分類
# ---------------------------------------------------------
rows = []
cols = []
spanning = []

for score, label, box in zip(structure["scores"], structure["labels"], structure["boxes"]):
    box = [float(x) for x in box]
    if label == 2:
        rows.append(box)
    elif label == 1:
        cols.append(box)
    elif label == 5:
        spanning.append(box)

print("\n=== Rows ===")
for r in rows:
    print(r)

print("\n=== Columns ===")
for c in cols:
    print(c)

print("\n=== Spanning Cells ===")
for s in spanning:
    print(s)

# ---------------------------------------------------------
#  行 × 列 → セル bbox を生成
# ---------------------------------------------------------
cells = []

for r in rows:
    for c in cols:
        cell = intersect_bbox(r, c)
        if cell:
            cells.append({
                "cell_bbox": cell,
                "type": "cell"
            })

# 結合セルも追加
for s in spanning:
    cells.append({
        "cell_bbox": [round(x,2) for x in s],
        "type": "spanning"
    })

# ---------------------------------------------------------
#  セルを上から下、左から右にソート
# ---------------------------------------------------------
cells_sorted = sorted(
    cells,
    key=lambda x: (x["cell_bbox"][1], x["cell_bbox"][0])
)

# ---------------------------------------------------------
#  最終出力
# ---------------------------------------------------------
print("\n=== Final Cells (Generated from row × col) ===")
for i, c in enumerate(cells_sorted):
    print(f"{i}: {c['type']}  bbox={c['cell_bbox']}")
