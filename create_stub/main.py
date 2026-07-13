#!/usr/bin/env python3
import os
from pathlib import Path
import uuid
from psycopg import connect
from psycopg.extras import execute_values
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from dotenv import load_dotenv

# ===== .env 読み込み =====
load_dotenv()

BASE_DIR = Path(os.getenv("BASE_DIR"))
PG_CONN_INFO = os.getenv("PG_CONN_INFO")

STUB_PDF_NAME = os.getenv("STUB_PDF_NAME", "stub.pdf")
STUB_CATEGORY = os.getenv("STUB_CATEGORY", "unknown")
STUB_TITLE = os.getenv("STUB_TITLE", "Stub PDF")
STUB_PAGE_COUNT = int(os.getenv("STUB_PAGE_COUNT", "3"))

# ===== スタブPDF生成 =====
def create_stub_pdf(pdf_path: Path):
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    w, h = A4

    # page 1 (日本語＋図)
    c.setFont("Helvetica", 14)
    c.drawString(50, h - 80, "温度センサーの校正方法")
    c.drawString(50, h - 110, "図1 温度センサーの構造")
    c.rect(50, h - 350, 300, 200)
    c.showPage()

    # page 2 (英語＋図)
    c.setFont("Helvetica", 14)
    c.drawString(50, h - 80, "Calibration procedure for temperature sensors.")
    c.drawString(50, h - 110, "Figure 2: Internal structure of the sensor.")
    c.circle(200, h - 250, 80)
    c.showPage()

    # page 3 (日本語＋英語＋表)
    c.setFont("Helvetica", 14)
    c.drawString(50, h - 80, "表1 校正結果一覧")
    c.drawString(50, h - 110, "Calibration Results Table")
    top = h - 200
    left = 50
    width = 400
    height = 200
    c.rect(left, top - height, width, height)
    for i in range(1, 4):
        c.line(left, top - i * (height / 4), left + width, top - i * (height / 4))
    for j in range(1, 4):
        c.line(left + j * (width / 4), top, left + j * (width / 4), top - height)
    c.showPage()

    c.save()

# ===== ダミー画像生成 =====
def create_dummy_image(path: Path, size=(800, 1131)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, (240, 240, 240))
    img.save(path)

# ===== URL生成 =====
def doc_base_url(doc_id: str) -> str:
    return f"http://localhost:8000/documents/{doc_id}"

# ===== メイン処理 =====
def main():
    # ★ uuid7 を doc_id に採用
    doc_id = str(uuid.uuid7())
    print(f"doc_id = {doc_id}")

    doc_dir = BASE_DIR / doc_id
    pdf_path = doc_dir / "original.pdf"

    # PDF生成
    create_stub_pdf(pdf_path)

    # ダミー画像生成（pages）
    page1_img = doc_dir / "pages" / "page_1.png"
    page2_img = doc_dir / "pages" / "page_2.png"
    page3_img = doc_dir / "pages" / "page_3.png"
    create_dummy_image(page1_img)
    create_dummy_image(page2_img)
    create_dummy_image(page3_img)

    # ダミー画像生成（chunks）
    c11_img = doc_dir / "chunks" / "page_1_chunk_1.png"
    c12_img = doc_dir / "chunks" / "page_1_chunk_2.png"
    c21_img = doc_dir / "chunks" / "page_2_chunk_1.png"
    c31_img = doc_dir / "chunks" / "page_3_chunk_1.png"
    create_dummy_image(c11_img, size=(300, 200))
    create_dummy_image(c12_img, size=(400, 300))
    create_dummy_image(c21_img, size=(380, 280))
    create_dummy_image(c31_img, size=(450, 250))

    base_url = doc_base_url(doc_id)

    # DB insert (psycopg3)
    with connect(PG_CONN_INFO) as conn:
        with conn.cursor() as cur:

            # pdf_documents
            cur.execute(
                """
                INSERT INTO pdf_documents (
                  doc_id, file_name, file_url, file_hash, title, page_count, category
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    doc_id,
                    STUB_PDF_NAME,
                    f"{base_url}/original.pdf",
                    "stubhash123",
                    STUB_TITLE,
                    STUB_PAGE_COUNT,
                    STUB_CATEGORY,
                ),
            )

            # pdf_pages
            pages_rows = [
                (doc_id, 1, f"{base_url}/pages/page_1.png", "温度センサーの校正方法", True, False, False, "{}"),
                (doc_id, 2, f"{base_url}/pages/page_2.png", "Calibration procedure", True, False, False, "{}"),
                (doc_id, 3, f"{base_url}/pages/page_3.png", "校正結果一覧", False, True, False, "{}"),
            ]
            execute_values(
                cur,
                """
                INSERT INTO pdf_pages (
                  doc_id, page_number, page_image_url,
                  summary, has_figure, has_table, has_photo, sections
                )
                VALUES %s
                """,
                pages_rows,
            )

            # pdf_chunks
            chunks_rows = [
                # page 1 text
                (
                    doc_id, 1, 1,
                    "温度センサーの校正方法",
                    "温度 センサー 校正 方法",
                    "text",
                    '{"x":10,"y":20,"w":300,"h":80}',
                    f"{base_url}/chunks/page_1_chunk_1.png",
                    [0.1, 0.2, 0.3],
                    '{"order":1}',
                ),
                # page 1 figure
                (
                    doc_id, 1, 2,
                    "図1 温度センサーの構造",
                    "図 温度 センサー 構造",
                    "figure",
                    '{"x":50,"y":150,"w":400,"h":300}',
                    f"{base_url}/chunks/page_1_chunk_2.png",
                    [0.2, 0.1, 0.4],
                    '{"order":2}',
                ),
                # page 2 figure (English)
                (
                    doc_id, 2, 1,
                    "Figure 2: Internal structure of the sensor.",
                    "figure internal structure sensor",
                    "figure",
                    '{"x":40,"y":120,"w":380,"h":280}',
                    f"{base_url}/chunks/page_2_chunk_1.png",
                    [0.3, 0.3, 0.1],
                    '{"order":1}',
                ),
                # page 3 table
                (
                    doc_id, 3, 1,
                    "表1 校正結果一覧 / Calibration Results Table",
                    "校正 結果 一覧 calibration results table",
                    "table",
                    '{"x":30,"y":100,"w":450,"h":250}',
                    f"{base_url}/chunks/page_3_chunk_1.png",
                    [0.4, 0.2, 0.2],
                    '{"order":1}',
                ),
            ]

            execute_values(
                cur,
                """
                INSERT INTO pdf_chunks (
                  doc_id, page_number, chunk_index,
                  text, text_tsv, chunk_type,
                  bbox, bbox_image_url, embedding, meta
                )
                VALUES %s
                """,
                chunks_rows,
            )

        conn.commit()

    print("Stub PDF & DB records created.")
    print(f"doc_id = {doc_id}")
    print(f"PDF    = {pdf_path}")
    print(f"Base   = {base_url}")


if __name__ == "__main__":
    main()
