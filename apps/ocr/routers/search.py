from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from db import pool
import requests

router = APIRouter()
templates = Jinja2Templates(directory="templates")

AZURE_SEARCH = False  # True にすると Azure AI Search を使用

# pg_bigm 用スニペット生成
def make_snippet(text: str, keyword: str, radius: int = 30):
    idx = text.find(keyword)
    if idx == -1:
        return text[:radius] + "..."
    start = max(0, idx - radius)
    end = min(len(text), idx + len(keyword) + radius)
    snippet = text[start:end]
    return snippet.replace(keyword, f"<em>{keyword}</em>")


@router.get("/search")
def search(request: Request, q: str = ""):
    results = []

    if q:
        if AZURE_SEARCH:
            # Azure AI Search
            url = f"{SEARCH_ENDPOINT}/indexes/documents/docs/search?api-version=2021-04-30-Preview"
            payload = {
                "search": q,
                "highlight": "content",
                "highlightPreTag": "<em>",
                "highlightPostTag": "</em>",
                "select": "file_name,page_number,content",
                "top": 20
            }
            r = requests.post(url, json=payload, headers=HEADERS)

            for item in r.json()["value"]:
                results.append({
                    "file_name": item["file_name"],
                    "page_number": item["page_number"],
                    "snippet": item["@search.highlights"]["content"][0]
                })

        else:
            # pg_bigm
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT file_name, page_number, content
                        FROM document_pages
                        WHERE content LIKE %s
                        LIMIT 20
                    """, (f"%{q}%",))

                    for file_name, page_number, content in cur.fetchall():
                        results.append({
                            "file_name": file_name,
                            "page_number": page_number,
                            "snippet": make_snippet(content, q)
                        })

    return templates.TemplateResponse(
        "search.html",
        {"request": request, "q": q, "results": results}
    )
