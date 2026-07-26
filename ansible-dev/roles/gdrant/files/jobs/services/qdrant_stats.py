# services/qdrant_stats.py

from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

def get_point_count_by_file_id():
    """
    Qdrant の asao_docs コレクションから
    file_id 別のポイント数を集計する
    """

    # 全ポイントを取得（大量なら scroll API に変更）
    all_points = client.scroll(
        collection_name="asao_docs",
        limit=100000
    )[0]

    stats = {}

    for p in all_points:
        file_id = p.payload.get("file_id")
        if file_id is None:
            continue

        stats[file_id] = stats.get(file_id, 0) + 1

    return stats

def get_all_points():
    """
    scroll API を使って Qdrant の全ポイントを取得する
    """

    all_points = []
    next_page_offset = None

    while True:
        points, next_page_offset = client.scroll(
            collection_name="asao_docs",
            limit=1000,  # 1回で1000件ずつ取得
            offset=next_page_offset
        )

        all_points.extend(points)

        if next_page_offset is None:
            break

    return all_points
