from transformers import AutoModelForCausalLM, AutoProcessor
from peft import PeftModel
from PIL import Image
import torch

base_model_path = "/data/models/qwen3.5VL"

# 複数 LoRA のパス
lora_paths = [
    "./qwen-logo-lora-toyota",
    "./qwen-logo-lora-honda",
    "./qwen-logo-lora-nissan"
]

# 1) 元モデル
model = AutoModelForCausalLM.from_pretrained(
    base_model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

# 2) LoRA を順番に apply
for lp in lora_paths:
    print(f"Loading LoRA: {lp}")
    model = PeftModel.from_pretrained(model, lp)

model.eval()

# 3) Processor
processor = AutoProcessor.from_pretrained(base_model_path)

# 4) 推論
img = Image.open("test.jpg").convert("RGB")

prompt = "<image>\nLocate all logos in this image."

inputs = processor.from_list_format([
    {"image": img},
    {"text": prompt}
])

with torch.no_grad():
    out = model.generate(**inputs, max_new_tokens=256)

print(processor.decode(out[0], skip_special_tokens=True))
