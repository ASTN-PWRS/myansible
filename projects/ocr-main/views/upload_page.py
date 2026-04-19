from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
import os
print(os.path.exists(BASE_DIR / "templates" / "upload.html"))

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()

@router.get("/")
def show_upload_page(request: Request):
    return templates.TemplateResponse(
        request,
        "upload.html",
        {"request": request}
    )

