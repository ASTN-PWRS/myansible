from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import search, upload
from views import search_page, upload_page

app = FastAPI()

# --- static フォルダを /static にマウント ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# 画面
# app.include_router(search_page.router)
app.include_router(upload_page.router)

# API
# app.include_router(search.router)
app.include_router(upload.router)
