# services/delete_postgres.py

from services.db import execute_query


def delete_file_meta(file_id: int):
    execute_query("DELETE FROM files WHERE id = %s", (file_id,))


def delete_image_meta(file_id: int):
    execute_query("DELETE FROM images WHERE file_id = %s", (file_id,))


def delete_text_chunks(file_id: int):
    execute_query("DELETE FROM text_chunks WHERE file_id = %s", (file_id,))
