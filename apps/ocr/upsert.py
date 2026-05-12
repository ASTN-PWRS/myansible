import psycopg
import logging

logger = logging.getLogger(__name__)

def upsert_task(conn, job_id, file_name, stage, status, page_number, error_message=None):
  sql = """
    INSERT INTO tasks (
        job_id,
        file_name,
        stage,
        status,
        page_number,
        error_message,
        updated_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, now())
    ON CONFLICT (job_id)
    DO UPDATE SET
        file_name     = EXCLUDED.file_name,
        stage         = EXCLUDED.stage,
        status        = EXCLUDED.status,
        page_number   = EXCLUDED.page_number,
        error_message = EXCLUDED.error_message,
        updated_at    = now();
  """

  try:
    with conn.cursor() as cur:
      cur.execute(sql, (job_id, file_name, stage, status, page_number, error_message))
    conn.commit()

  except psycopg.Error as e:
    logger.error(f"[DB ERROR] job_id={job_id} stage={stage} status={status} error={e}")
    conn.rollback()
    # 呼び出し元にも例外を返す
    raise
