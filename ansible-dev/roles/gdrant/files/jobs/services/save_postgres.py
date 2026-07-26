# services/save_postgres.py
import psycopg

PG_CONN = psycopg.connect(
    dbname="ragdb",
    user="rag",
    password="ragpass",
    host="localhost",
    port=5432
)

def save_file_meta(path, category, department):
    filename = path.split("/")[-1]
    with PG_CONN.cursor() as cur:
        cur.execute("""
            INSERT INTO files (filename, mime, category, department, path)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (filename, "application/pdf", category, department, path))
        file_id = cur.fetchone()[0]
        PG_CONN.commit()
    return file_id

def save_image_meta(rows):
    with PG_CONN.cursor() as cur:
        cur.executemany("""
            INSERT INTO images (file_id, page, image_type, objects, caption, path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [(r["file_id"], r["page"], r["image_type"], r["objects"], r["caption"], r["path"]) for r in rows])
        PG_CONN.commit()

def save_text_chunks(rows):
    with PG_CONN.cursor() as cur:
        cur.executemany("""
            INSERT INTO chunks (file_id, chunk_index, page, text)
            VALUES (%s, %s, %s, %s)
        """, [(r["file_id"], r["chunk_index"], r["page"], r["text"]) for r in rows])
        PG_CONN.commit()
