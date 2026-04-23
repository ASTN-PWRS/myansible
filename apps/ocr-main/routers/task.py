

@router.get("/task/{task_id}")
def get_task_status(task_id: str):
    row = db.fetch("SELECT * FROM tasks WHERE task_id=%s", (task_id,))
    return row
