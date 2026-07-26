# worker/update_document_workflow.py

from worker.delete_document_workflow import run_delete_document_workflow
from worker.workflow import run_index_workflow   # ← あなたの index_workflow
import os


def run_update_document_workflow(params: dict):
    """
    文書更新（再インデックス）workflow
    - 古い文書を削除
    - 新しい文書を再インデックス
    """

    file_id = params["file_id"]
    new_file_path = params["file_path"]
    category = params["category"]
    department = params["department"]

    # -----------------------------
    # 1. 古い文書を削除
    # -----------------------------
    run_delete_document_workflow(file_id)

    # -----------------------------
    # 2. 新しい文書を再インデックス
    # -----------------------------
    new_params = {
        "file_path": new_file_path,
        "category": category,
        "department": department
    }

    result = run_index_workflow(new_params)

    return {
        "status": "ok",
        "old_file_id": file_id,
        "new_file_id": result["file_id"],
        "filename": result["filename"],
        "file_url": result.get("file_url")
    }
