import datetime
import pytz
import psycopg
from psycopg.rows import dict_row
import json

def get_datetime(format: str, timezone: str):
  try:
    format_map = {
      "yyyy": "%Y",
      "MM": "%m",
      "dd": "%d",
      "HH": "%H",
      "mm": "%M",
      "ss": "%S"
    }

    py_format = format
    for k, v in format_map.items():
      py_format = py_format.replace(k, v)

    tz = pytz.timezone(timezone)
    now = datetime.datetime.now(tz)
    return now.strftime(py_format)

  except Exception as e:
    return json.dumps({"error": str(e)})


def list_documents(category=None, query=None):
  try:
    # psycopg3 接続
    conn = psycopg.connect(
      "postgresql://user:password@localhost:5432/dbname"
    )

    # dict_row により psycopg2.extras.RealDictCursor と同等の dict を返す
    cur = conn.cursor(row_factory=dict_row)

    if category:
      cur.execute("""
        SELECT doc_id, title, file_name, file_url, category
        FROM pdf_documents
        WHERE category = %s
        ORDER BY created_at DESC
      """, (category,))

    elif query:
      cur.execute("""
        SELECT d.doc_id, d.title, d.file_name, d.file_url, d.category
        FROM pdf_documents d
        JOIN pdf_chunks c ON d.doc_id = c.doc_id
        WHERE c.text_tsv @@ plainto_tsquery(%s)
        GROUP BY d.doc_id
        ORDER BY d.created_at DESC
      """, (query,))

    else:
      cur.execute("""
        SELECT doc_id, title, file_name, file_url, category
        FROM pdf_documents
        ORDER BY created_at DESC
      """)

    rows = cur.fetchall()

    return json.dumps([
      {
        "doc_id": r["doc_id"],
        "name": r["title"] or r["file_name"],
        "url": r["file_url"],
        "category": r["category"]
      }
      for r in rows
    ])

  except Exception as e:
    return json.dumps({"error": str(e)})
