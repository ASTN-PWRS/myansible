# pip install weaviate-client pillow opencv-python transformers peft datasets accelerate

import argparse
import os
import json
import weaviate
from PIL import Image, ImageOps

from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoProcessor, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model
import torch

# ---------- Weaviate ----------

client = weaviate.Client("http://localhost:8080")

def fetch_images_by_class(class_name):
    query = f"""
    {{
      Get {{
        {class_name} {{
          image_path
          name
        }}
      }}
    }}
    """
    res = client.query.raw(query)
    return res["data"]["Get"][class_name]

# ---------- Data building (bbox = full image) ----------

def full_image_bbox(img: Image.Image):
    w, h = img.size
    return [0, 0, w, h]

def augment_image_and_bbox(img):
    w, h = img.size
    aug = []

    # scale
    for scale in [0.8, 1.0, 1.2]:
        new_img = img.resize((int(w*scale), int(h*scale)))
        new_bbox = full_image_bbox(new_img)
        aug.append((new_img, new_bbox))

    # rotate
    for angle in [0, 15, -15, 30, -30]:
        new_img = img.rotate(angle, expand=True)
        new_bbox = full_image_bbox(new_img)
        aug.append((new_img, new_bbox))

    # grayscale
    gray = ImageOps.grayscale(img).convert("RGB")
    new_bbox = full_image_bbox(gray)
    aug.append((gray, new_bbox))

    return aug

def make_grounding_item(image_path, bbox, label):
    return {
        "image": image_path,
        "conversations": [
            {
                "from": "human",
                "value": f"<image>\nLocate the logo '{label}' in this image."
            },
            {
                "from": "gpt",
                "value": f"<bbox>[{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}]</bbox>"
            }
        ]
    }

def build_dataset_jsonl(class_name, jsonl_path="train.jsonl"):
    items = fetch_images_by_class(class_name)

    os.makedirs("aug", exist_ok=True)

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in items:
            path = item["image_path"]
            label = class_name

            img = Image.open(path).convert("RGB")
            bbox = full_image_bbox(img)

            # original
            f.write(json.dumps(make_grounding_item(path, bbox, label), ensure_ascii=False) + "\n")

            # aug
            aug_list = augment_image_and_bbox(img)
            base = os.path.splitext(os.path.basename(path))[0]

            for idx, (aug_img, aug_bbox) in enumerate(aug_list):
                aug_path = f"aug/{base}_{idx}.jpg"
                aug_img.save(aug_path)
                f.write(json.dumps(make_grounding_item(aug_path, aug_bbox, label), ensure_ascii=False) + "\n")

    print("dataset saved:", jsonl_path)

# ---------- Qwen3.5-VL + LoRA training ----------

def train_qwen_lora(jsonl_path, out_dir):
    model_id = "/data/models/qwen3.5VL"

    print("loading model:", model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    processor = AutoProcessor.from_pretrained(model_id)

    # LoRA config
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "down_proj", "up_proj"
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)

    # dataset
    dataset = load_dataset("json", data_files=jsonl_path)

    def preprocess(example):
        messages = example["conversations"]
        image_path = example["image"]

        img = Image.open(image_path).convert("RGB")

        inputs = processor.from_list_format([
            {"image": img},
            {"text": messages[0]["value"]}
        ])

        label_text = messages[1]["value"]
        labels = processor.tokenizer(
            label_text,
            return_tensors="pt"
        ).input_ids[0]

        inputs["labels"] = labels
        return inputs

    dataset = dataset["train"].map(preprocess)

    args = TrainingArguments(
        output_dir=out_dir,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=3,
        fp16=True,
        logging_steps=10,
        save_steps=500,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset
    )

    trainer.train()

    # ★ LoRA をマージして単体モデル化 ★
    print("Merging LoRA into base model...")
    merged = model.merge_and_unload()

    merged_dir = out_dir + "_merged"
    merged.save_pretrained(merged_dir)
    processor.save_pretrained(merged_dir)

    print("Merged model saved:", merged_dir)

# ---------- CLI ----------
# python train_qwen_logo.py --class_name LogoClass --out_dir qwen-logo-lora

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--class_name", required=True, help="Weaviate class name (logo class)")
    parser.add_argument("--jsonl_path", default="train.jsonl")
    parser.add_argument("--out_dir", default="./qwen-logo-lora")
    args = parser.parse_args()

    build_dataset_jsonl(args.class_name, args.jsonl_path)
    train_qwen_lora(args.jsonl_path, args.out_dir)

if __name__ == "__main__":
    main()
