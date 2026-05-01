query_text = "温泉で有名な観光地は？"
keywords = []  # 空でもOK

q_vec = embed([query_text])[0].tolist()

cur.execute(
    """
    WITH query AS (
      SELECT
        %s::text      AS q_text,
        %s::vector    AS q_vec,
        %s::text[]    AS q_keywords
    ),
    candidates AS (
      SELECT
        p.id,
        p.document_id,
        p.page_number,
        p.content,
        (p.embedding <-> q.q_vec) AS vec_dist,
        CASE
          WHEN array_length(q.q_keywords, 1) IS NULL THEN FALSE
          ELSE EXISTS (
            SELECT 1
            FROM unnest(q.q_keywords) kw
            WHERE p.content LIKE '%' || kw || '%'
          )
        END AS kw_match
      FROM ocr_pages p
      CROSS JOIN query q
    )
    SELECT
      id,
      document_id,
      page_number,
      content,
      vec_dist,
      kw_match,
      (vec_dist + CASE WHEN kw_match THEN 0.0 ELSE 0.3 END) AS hybrid_score
    FROM candidates
    ORDER BY hybrid_score ASC
    LIMIT 20;
    """,
    (query_text, q_vec, keywords)
)

rows = cur.fetchall()
