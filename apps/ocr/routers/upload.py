from fastapi import APIRouter, UploadFile, File
from db import pool
from ocr import pdf_ocr

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    file_name = file.filename

    ocr_results = pdf_ocr(pdf_bytes)

    with pool.connection() as conn:
        with conn.cursor() as cur:
            for item in ocr_results:
                cur.execute("""
                    INSERT INTO document_pages (file_name, page_number, content)
                    VALUES (%s, %s, %s)
                """, (file_name, item["page"], item["text"]))

    return {"status": "ok", "pages": len(ocr_results)}
