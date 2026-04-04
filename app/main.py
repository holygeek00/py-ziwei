"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api.routes import router

app = FastAPI(
    title="紫微斗数排盘 API",
    description="Python 版紫微斗数排盘后端，移植自 iztro",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Zi Wei Dou Shu API is running", "status": "online"}

@app.get("/report")
async def report_page():
    html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../public/index.html"))
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"error": "UI file not found"}
