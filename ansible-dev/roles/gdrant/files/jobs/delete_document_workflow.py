# worker/delete_document_workflow.py

from services.delete_postgres import (
    delete_file_meta,
    delete_image_meta,
    delete_text_chunks
)
from services.delete_qdrant import delete_document_from_qdrant


def run_delete_document_workflow(file_id: int):
    """
    文書削除ワークフロー
    - PostgreSQL の正本データ削除
    - Qdrant のインデックス削除
    """

    # PostgreSQL 削除
    delete_file_meta(file_id)
    delete_image_meta(file_id)
    delete_text_chunks(file_id)

    # Qdrant 削除
    delete_document_from_qdrant(file_id)

    return {
        "status": "ok",
        "deleted_file_id": file_id
    }
