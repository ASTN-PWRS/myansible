from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request, "q": "", "results": []})
