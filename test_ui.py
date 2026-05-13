#!/usr/bin/env python3
"""
测试 UI HTML 是否正确加载
"""
from app.api.ui_html import INDEX_HTML

print("=" * 60)
print("🧪 测试 UI HTML 模板")
print("=" * 60)

# 检查 HTML 长度
print(f"✅ HTML 长度: {len(INDEX_HTML)} 字符")

# 检查关键元素
checks = [
    ("<!DOCTYPE html>", "HTML 文档类型"),
    ("<title>紫微斗数", "页面标题"),
    ("renderAstrolabe", "星盘渲染函数"),
    ("switchTab", "标签切换函数"),
    ("/api/report/generate", "API 端点"),
    ("/api/astrolabe", "星盘数据端点"),
    ("star-major", "主星样式"),
    ("star-mutagen", "四化样式"),
    ("center-palace", "中宫样式"),
]

print("\n🔍 检查关键元素:")
all_passed = True
for keyword, description in checks:
    if keyword in INDEX_HTML:
        print(f"  ✅ {description}")
    else:
        print(f"  ❌ {description} - 未找到")
        all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("🎉 所有检查通过！UI HTML 模板正常")
else:
    print("⚠️  部分检查失败，请检查 HTML 内容")
print("=" * 60)
