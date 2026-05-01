from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

MODEL = "BAAI/bge-m3"

# モデルとトークナイザをロード
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModel.from_pretrained(MODEL).to("cpu")

texts = [
    "富士山は日本で最も高い山です。",
    "昨日は箱根に旅行に行きました。",
    "機械学習モデルを使って文章を検索します。"
]

def embed(texts):
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    with torch.no_grad():
        out = model(**inputs)
        vec = out.last_hidden_state[:, 0]  # CLS ベクトル
        vec = F.normalize(vec, p=2, dim=1)  # pgvector向けに正規化
    return vec

emb = embed(texts)

print("shape:", emb.shape)
print(emb)
