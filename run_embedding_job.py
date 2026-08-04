import json
import ollama
import base64
import os


# ------------------------------------------------------------
# 画像 embedding（jina-v5-omni-small）
# ------------------------------------------------------------
def embed_image_jina(image_bytes):
    res = ollama.embeddings(
        model="jina-v5-omni-small",
        images=[image_bytes]
    )
    return res["embedding"]


# ------------------------------------------------------------
# テキスト embedding（jina-v5-omni-small）
# ------------------------------------------------------------
def embed_text_jina(text):
    res = ollama.embeddings(
        model="jina-v5-omni-small",
        prompt=text
    )
    return res["embedding"]


# ------------------------------------------------------------
# JSON を読み込み → embedding を埋める → JSON を保存
# ------------------------------------------------------------
def run_embedding_job(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    updated = []

    for rec in records:
        # すでに埋められている場合はスキップ
        if rec["vectors"]["semantic"] is not None:
            updated.append(rec)
            continue

        if rec["type"] == "text":
            vec = embed_text_jina(rec["text"])
            rec["vectors"]["semantic"] = vec

        elif rec["type"] == "image":
            # 画像は bytes を JSON に含めていないので、
            # 必要なら別途保存してある画像を読み込む設計にする。
            # ここではダミーとして caption を embedding する。
            vec = embed_text_jina(rec["image_caption"] or "")
            rec["vectors"]["semantic"] = vec

        updated.append(rec)

    # JSON を上書き保存
    out_path = json_path.replace(".json", "_embedded.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)

    return out_path


# ------------------------------------------------------------
# 実行例
# ------------------------------------------------------------
if __name__ == "__main__":
    output = run_embedding_job("input_structure.json")
    print("embedding 完了:", output)
