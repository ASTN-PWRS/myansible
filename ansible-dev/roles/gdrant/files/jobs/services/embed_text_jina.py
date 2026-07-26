# services/embed_text_jina.py
from jina_embeddings import JinaEmbeddings

# v5-text-small 
emb = JinaEmbeddings(model_name="jina-text-small")

def embed_text(text):
    return emb.encode(text).tolist()
