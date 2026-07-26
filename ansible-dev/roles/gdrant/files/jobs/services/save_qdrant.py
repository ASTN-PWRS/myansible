# services/save_qdrant.py
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

qdrant = QdrantClient(url="http://localhost:6333")

def save_vectors(vectors, payloads, prefix):
    points = []
    for idx, (vec, payload) in enumerate(zip(vectors, payloads)):
        points.append(
            PointStruct(
                id=f"{prefix}{idx}",
                vector=vec,
                payload=payload
            )
        )
    qdrant.upsert(collection_name="asao_docs", points=points)
