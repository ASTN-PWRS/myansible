from fastapi import APIRouter, UploadFile, File
from uuid6 import uuid7
import os
import json
import redis
from typing import List

router = APIRouter()
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

@router.post("/api/upload")
async def upload_pdf(files: List[UploadFile] = File(...)):
    task_id = str(uuid7())
    base_dir = f"/var/tmp/ocr/{task_id}"
    os.makedirs(base_dir, exist_ok=True)

    saved_files = []

    for file in files:
        file_bytes = await file.read()
        file_name = file.filename
        pdf_path = f"{base_dir}/{file_name}"

        # --- 保存完了を保証する同期 I/O ---
        with open(pdf_path, "wb") as f:
            f.write(file_bytes)
            f.flush()
            os.fsync(f.fileno())  # ← これでディスク書き込み完了を保証

        saved_files.append({
            "file_name": file_name,
            "saved_path": pdf_path
        })

    # --- 保存完了後にのみ rpush ---
    payload = {
        "task_id": task_id,
        "files": saved_files
    }

    r.rpush("queue:ocr", json.dumps(payload))

    return payload
