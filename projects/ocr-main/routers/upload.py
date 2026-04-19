import os
import json
import uuid
import shutil
import redis

from fastapi import APIRouter, UploadFile, File

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

router = APIRouter()

@router.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    task_id = str(uuid.uuid5())

    # 一時フォルダ: /tmp/{task_id}/
    temp_dir = f"/tmp/{task_id}"
    os.makedirs(temp_dir, exist_ok=True)

    temp_path = f"{temp_dir}/{file.filename}"

    # PDF を保存
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    task_id = str(uuid.uuid4())

    db.execute("""
    INSERT INTO tasks (task_id, file_name, status, progress)
    VALUES (%s, %s, 'pending', 0)
    """, (task_id, file.filename))

    # キューに入れる JSON
    task = {
        "task_id": task_id,
        "filename": file.filename,

        "temp_path": temp_path,
    }

    r.lpush("queue:ocr", json.dumps(task))

    # タスク状態を保存
    r.hset(f"task:{task_id}", mapping={
        "status": "queued",
        "progress": "0",
        "filename": file.filename,
    })

    return {"status": "queued", "task_id": task_id}
