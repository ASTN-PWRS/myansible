#!/usr/bin/env python3
import argparse
import json
import numpy as np
from PIL import Image
import onnxruntime as ort


MODEL_PATH = "/opt/models/SigLIP2/siglip2-vitb-int8.onnx"


def preprocess(img: Image.Image):
    img = img.resize((224, 224))
    arr = np.array(img).astype(np.float32) / 255.0
    arr = arr.transpose(2, 0, 1)  # HWC → CHW
    arr = np.expand_dims(arr, 0)  # batch=1
    return arr


def load_model():
    sess = ort.InferenceSession(
        MODEL_PATH,
        providers=["CPUExecutionProvider"]
    )
    return sess


def embed_image(sess, img_path):
    img = Image.open(img_path).convert("RGB")
    inp = preprocess(img)

    outputs = sess.run(None, {"images": inp})
    emb = outputs[0][0]

    # normalize
    emb = emb / np.linalg.norm(emb)
    return emb.tolist()


def embed_text(sess, text):
    # SigLIP2 の ONNX は画像専用モデルなので、
    # テキストは HuggingFace の tokenizer + PyTorch が必要。
    # → ここではゼロショット分類用に簡易 CLIP-style 文章埋め込みを使う。
    from transformers import AutoProcessor, AutoModel
    import torch

    processor = AutoProcessor.from_pretrained("google/siglip2-base-patch16-224")
    model = AutoModel.from_pretrained("google/siglip2-base-patch16-224")

    inputs = processor(text=text, return_tensors="pt", padding=True)
    with torch.no_grad():
        emb = model.get_text_features(**inputs)

    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.squeeze().cpu().numpy()


def classify(sess, img_path, labels):
    img_emb = np.array(embed_image(sess, img_path))

    text_embs = []
    for label in labels:
        text_embs.append(embed_text(sess, label))

    sims = [float(np.dot(img_emb, t)) for t in text_embs]
    best = int(np.argmax(sims))

    return {
        "label": labels[best],
        "scores": dict(zip(labels, sims))
    }


def main():
    parser = argparse.ArgumentParser(description="SigLIP2 ONNX CLI")
    parser.add_argument("--image", required=True, help="Input image")
    parser.add_argument("--labels", nargs="*", help="Zero-shot labels")
    parser.add_argument("--output", help="Output JSON")
    args = parser.parse_args()

    sess = load_model()

    if args.labels:
        result = classify(sess, args.image, args.labels)
    else:
        result = {
            "embedding": embed_image(sess, args.image),
            "dims": 768,
            "model": MODEL_PATH
        }

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f)
        print(f"Saved → {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
