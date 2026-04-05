# app/routers/search.py
from fastapi import APIRouter, Query
from app.db import pool
import psycopg

router = APIRouter()

@router.get("/search")
def search(q: str = Query(...), page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page

    sql = """
        SELECT id, filename, page_number, text
        FROM ocr_documents
        WHERE text_tsv @@ plainto_tsquery('japanese', %s)
        ORDER BY id
        LIMIT %s OFFSET %s
    """

    count_sql = """
        SELECT COUNT(*)
        FROM ocr_documents
        WHERE text_tsv @@ plainto_tsquery('japanese', %s)
    """

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (q, per_page, offset))
            rows = cur.fetchall()

            cur.execute(count_sql, (q,))
            total = cur.fetchone()[0]

    return {
        "query": q,
        "page": page,
        "per_page": per_page,
        "total": total,
        "results": [
            {
                "id": r[0],
                "filename": r[1],
                "page_number": r[2],
                "text": r[3],
            }
            for r in rows
        ]
    }
