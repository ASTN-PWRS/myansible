from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()

@router.get("/search")
def search_page(request: Request):
    return templates.TemplateResponse(
        request,
        "search.html", 
        {"request": request, "q": "", "results": []}
    )
