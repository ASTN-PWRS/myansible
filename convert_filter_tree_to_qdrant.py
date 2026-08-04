from qdrant_client import QdrantClient
from qdrant_client.models import Filter, SearchParams, ScoredPoint
import ollama


# ------------------------------------------------------------
# 1. ネスト対応 filter_tree → Qdrant must/should/must_not
# ------------------------------------------------------------
def convert_filter_tree_to_qdrant(filter_tree):
    qdrant_query = {
        "must": [],
        "should": [],
        "must_not": []
    }

    def convert_condition(cond):
        field = cond["field"]
        op = cond["operator"]
        value = cond["value"]

        if op == "eq":
            return {"key": field, "match": {"value": value}}
        elif op == "not_eq":
            return {"key": field, "match": {"value": value}}
        elif op == "contains":
            return {"key": field, "contains": value}
        elif op == "in":
            return {"key": field, "match": {"any": value}}
        elif op == "gt":
            return {"key": field, "range": {"gt": value}}
        elif op == "lt":
            return {"key": field, "range": {"lt": value}}
        else:
            raise ValueError(f"Unsupported operator: {op}")

    def dfs(node, parent_op=None):
        if "field" in node:
            cond = convert_condition(node)

            if parent_op == "and":
                qdrant_query["must"].append(cond)
            elif parent_op == "or":
                qdrant_query["should"].append(cond)
            elif parent_op == "not":
                qdrant_query["must_not"].append(cond)
            else:
                qdrant_query["must"].append(cond)
            return

        op = node["op"]
        for child in node.get("children", []):
            dfs(child, op)

    dfs(filter_tree)
    return qdrant_query


# ------------------------------------------------------------
# 2. テキスト → embedding（jina-v5-omni-small via ollama）
# ------------------------------------------------------------
def embed_query_text(text):
    res = ollama.embeddings(
        model="jina-v5-omni-small",
        prompt=text
    )
    return res["embedding"]


# ------------------------------------------------------------
# 3. Qdrant 検索実行
# ------------------------------------------------------------
def run_qdrant_query(
    qdrant_host,
    collection_name,
    generic_query
):
    # 1. filter_tree → Qdrant の must/should/must_not に変換
    filter_tree = generic_query["filter_tree"]
    qdrant_filter = convert_filter_tree_to_qdrant(filter_tree)

    # 2. embedding 生成
    query_text = generic_query["vector_query"]["text"]
    top_k = generic_query["vector_query"].get("top_k", 20)
    query_vector = embed_query_text(query_text)

    # 3. Qdrant クライアント
    client = QdrantClient(url=qdrant_host)

    # 4. 検索実行
    result = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        query_filter=Filter(
            must=qdrant_filter["must"],
            should=qdrant_filter["should"],
            must_not=qdrant_filter["must_not"]
        ),
        search_params=SearchParams(hnsw_ef=128)
    )

    return result
