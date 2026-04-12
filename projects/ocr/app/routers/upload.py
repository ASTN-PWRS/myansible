# app/routers/upload.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pdf2image import convert_from_bytes
from app.db import pool
from app.ocr import preprocess_image, run_ocr
import psycopg

router = APIRouter()

def insert_page(filename, page_number, text):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ocr_documents (filename, page_number, text)
                VALUES (%s, %s, %s)
                """,
                (filename, page_number, text)
            )
        conn.commit()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()
    pages = convert_from_bytes(content, dpi=300)

    results = []
    for i, page in enumerate(pages, start=1):
        img = preprocess_image(page)
        text = run_ocr(img)
        insert_page(file.filename, i, text)
        results.append({"page": i, "text": text})

    return JSONResponse({"filename": file.filename, "pages": results})
