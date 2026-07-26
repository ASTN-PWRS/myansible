# services/search_qdrant.py

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

qdrant = QdrantClient(url="http://localhost:6333")


def search_qdrant(queries, not_queries, must_filters, must_not_filters, top_k):

    must_conditions = []
    for f in must_filters:
        must_conditions.append(
            FieldCondition(
                key=f["key"],
                match=MatchValue(value=f["match"]["any"])
            )
        )

    must_not_conditions = []
    for f in must_not_filters:
        must_not_conditions.append(
            FieldCondition(
                key=f["key"],
                match=MatchValue(value=f["match"]["any"])
            )
        )

    flt = Filter(
        must=must_conditions,
        must_not=must_not_conditions
    )

    # NOT 条件の file_id を除外
    exclude_file_ids = set()
    for nq in not_queries:
        res = qdrant.search(
            collection_name="asao_docs",
            query_vector=nq["vector"],
            limit=nq["top"],
            with_payload=True,
            with_vector=False
        )
        for p in res:
            exclude_file_ids.add(p.payload["file_id"])

    # AND 条件の検索
    all_results = []
    for q in queries:
        res = qdrant.search(
            collection_name="asao_docs",
            query_vector=q["vector"],
            limit=q["top"],
            with_payload=True,
            with_vector=False,
            filter=flt
        )
        for p in res:
            if p.payload["file_id"] in exclude_file_ids:
                continue
            all_results.append({
                "payload": p.payload,
                "score": p.score
            })

    return all_results
