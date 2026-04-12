# app/main.py
from fastapi import FastAPI
from app.routers import upload, search
from app.views import upload_page, search_page

app = FastAPI()

# API
app.include_router(upload.router)
app.include_router(search.router)

# HTML render
app.include_router(upload_page.router)
app.include_router(search_page.router)
