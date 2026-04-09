# app/views/search_page.py
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/search_page")
def search_page(request: Request):
    return templates.TemplateResponse(
        "search.html",
        context={"request": request}
    )
