# services/delete_qdrant.py

from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")


def delete_document_from_qdrant(file_id: int):
    """
    Qdrant のポイントを file_id で一括削除する
    """

    client.delete(
        collection_name="asao_docs",
        points_selector={
            "filter": {
                "must": [
                    {"key": "file_id", "match": {"value": file_id}}
                ]
            }
        }
    )
