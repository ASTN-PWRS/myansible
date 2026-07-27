#!/usr/bin/env python3
import argparse
import json
import numpy as np
from PIL import Image
import torch
from transformers import AutoModel, AutoProcessor

# ★ ローカルキャッシュされたモデルを使う
MODEL_DIR = "/opt/models/siglip2"


def load_model(device, dtype):
    # ★ HuggingFace ではなくローカルからロード
    model = AutoModel.from_pretrained(MODEL_DIR).to(device)
    processor = AutoProcessor.from_pretrained(MODEL_DIR)

    if dtype == "float16":
        model = model.half()
    elif dtype == "bfloat16":
        model = model.to(torch.bfloat16)

    return model, processor


def preprocess_image(img_path, resize=None, center_crop=False):
    img = Image.open(img_path).convert("RGB")

    if resize:
        img = img.resize((resize, resize))

    if center_crop:
        w, h = img.size
        s = min(w, h)
        left = (w - s) // 2
        top = (h - s) // 2
        img = img.crop((left, top, left + s, top + s))

    return img


def embed_image(model, processor, device, img_path, normalize=True, resize=None, center_crop=False):
    img = preprocess_image(img_path, resize, center_crop)
    inputs = processor(images=img, return_tensors="pt").to(device)

    with torch.no_grad():
        emb = model.get_image_features(**inputs)

    if normalize:
        emb = emb / emb.norm(dim=-1, keepdim=True)

    return emb.squeeze().cpu().tolist()


def embed_image_batch(model, processor, device, img_paths, normalize=True, resize=None, center_crop=False):
    imgs = [preprocess_image(p, resize, center_crop) for p in img_paths]
    inputs = processor(images=imgs, return_tensors="pt").to(device)

    with torch.no_grad():
        embs = model.get_image_features(**inputs)

    if normalize:
        embs = embs / em.norm(dim=-1, keepdim=True)

    return embs.cpu().tolist()


def embed_text(model, processor, device, text, normalize=True):
    inputs = processor(text=text, return_tensors="pt", padding=True).to(device)

    with torch.no_grad():
        emb = model.get_text_features(**inputs)

    if normalize:
        emb = emb / emb.norm(dim=-1, keepdim=True)

    return emb.squeeze().cpu().numpy()


def classify(model, processor, device, img_path, labels, normalize=True):
    img_emb = np.array(embed_image(model, processor, device, img_path, normalize))

    text_embs = [embed_text(model, processor, device, label, normalize) for label in labels]
    sims = [float(np.dot(img_emb, t)) for t in text_embs]

    best = int(np.argmax(sims))
    return {
        "label": labels[best],
        "scores": dict(zip(labels, sims))
    }


def main():
    parser = argparse.ArgumentParser(description="SigLIP2 CLI (Local Cached Model)")

    parser.add_argument("--image", help="Single image path")
    parser.add_argument("--batch", nargs="*", help="Batch image paths")
    parser.add_argument("--labels", nargs="*", help="Classification labels")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--output-format", choices=["json", "npy", "raw"], default="json")

    parser.add_argument("--normalize", action="store_true", default=False)
    parser.add_argument("--dtype", choices=["float32", "float16", "bfloat16"], default="float32")
    parser.add_argument("--device", choices=["cuda", "cpu", "mps"], default=None)

    parser.add_argument("--resize", type=int, help="Resize image")
    parser.add_argument("--center-crop", action="store_true", help="Center crop image")

    args = parser.parse_args()

    # device
    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")

    # ★ ローカルモデルをロード
    model, processor = load_model(device, args.dtype)

    # -----------------------------
    # Classification mode
    # -----------------------------
    if args.labels and args.image:
        result = classify(model, processor, device, args.image, args.labels, args.normalize)

    # -----------------------------
    # Batch embedding mode
    # -----------------------------
    elif args.batch:
        embs = embed_image_batch(
            model, processor, device,
            args.batch,
            normalize=args.normalize,
            resize=args.resize,
            center_crop=args.center_crop
        )
        result = {
            "embeddings": embs,
            "dims": len(embs[0]),
            "model": MODEL_DIR
        }

    # -----------------------------
    # Single image embedding mode
    # -----------------------------
    else:
        emb = embed_image(
            model, processor, device,
            args.image,
            normalize=args.normalize,
            resize=args.resize,
            center_crop=args.center_crop
        )
        result = {
            "embedding": emb,
            "dims": len(emb),
            "model": MODEL_DIR
        }

    # -----------------------------
    # Output
    # -----------------------------
    if args.output:
        if args.output_format == "json":
            with open(args.output, "w") as f:
                json.dump(result, f)
        elif args.output_format == "npy":
            np.save(args.output, np.array(result["embeddings"] if "embeddings" in result else result["embedding"]))
        else:
            with open(args.output, "w") as f:
                f.write(str(result))

        print(f"Saved → {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
