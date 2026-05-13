"""
Vercel serverless function entry point
"""
from app.main import app

# Vercel 会自动处理这个 app 对象
handler = app
