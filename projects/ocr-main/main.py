from fastapi import FastAPI
from routers import upload
# from routers import search
from views import search_page, upload_page

app = FastAPI()

# 画面
# app.include_router(search_page.router)
app.include_router(upload_page.router)

# API
# app.include_router(search.router)
app.include_router(upload.router)
