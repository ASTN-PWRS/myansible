#!/usr/bin/env python3
import argparse
import json
import numpy as np
from PIL import Image
import torch
from transformers import AutoModel, AutoProcessor


MODEL_ID = "google/siglip2-base-patch16-224"


def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = AutoModel.from_pretrained(MODEL_ID).to(device)
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    return model, processor, device


def embed_image(model, processor, device, img_path):
    img = Image.open(img_path).convert("RGB")
    inputs = processor(images=img, return_tensors="pt").to(device)

    with torch.no_grad():
        emb = model.get_image_features(**inputs)

    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.squeeze().cpu().tolist()


def embed_text(model, processor, device, text):
    inputs = processor(text=text, return_tensors="pt", padding=True).to(device)

    with torch.no_grad():
        emb = model.get_text_features(**inputs)

    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.squeeze().cpu().numpy()


def classify(model, processor, device, img_path, labels):
    img_emb = np.array(embed_image(model, processor, device, img_path))

    text_embs = [embed_text(model, processor, device, label) for label in labels]
    sims = [float(np.dot(img_emb, t)) for t in text_embs]

    best = int(np.argmax(sims))
    return {
        "label": labels[best],
        "scores": dict(zip(labels, sims))
    }


def main():
    parser = argparse.ArgumentParser(description="SigLIP2 CLI (PyTorch)")
    parser.add_argument("--image", required=True)
    parser.add_argument("--labels", nargs="*")
    parser.add_argument("--output")
    args = parser.parse_args()

    model, processor, device = load_model()

    if args.labels:
        result = classify(model, processor, device, args.image, args.labels)
    else:
        result = {
            "embedding": embed_image(model, processor, device, args.image),
            "dims": 768,
            "model": MODEL_ID
        }

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f)
        print(f"Saved → {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
