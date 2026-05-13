"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
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

# 静态文件服务 - 在非 Vercel 环境下挂载
# Vercel 会自动处理 public 目录的静态文件
if not os.environ.get("VERCEL"):
    public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
    if os.path.exists(public_dir):
        app.mount("/static", StaticFiles(directory=public_dir), name="static")

@app.get("/")
async def root():
    """API 根路径"""
    return {"message": "Zi Wei Dou Shu API is running", "status": "online"}

@app.get("/report")
async def report_page():
    """排盘界面"""
    index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "index.html")
    
    # 尝试读取文件内容
    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
            return HTMLResponse(content=content)
        except Exception:
            pass
    
    # 降级到旧的 HTML
    from app.api.ui_html import INDEX_HTML
    return HTMLResponse(content=INDEX_HTML)
