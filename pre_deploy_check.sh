#!/bin/bash

echo "🔍 部署前检查..."
echo ""

# 检查必要文件
echo "📁 检查必要文件:"
files=(
    "api/index.py"
    "app/main.py"
    "app/api/routes.py"
    "app/api/ui_html.py"
    "requirements.txt"
    "vercel.json"
)

all_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - 文件不存在"
        all_exist=false
    fi
done

echo ""

# 检查 Python 语法
echo "🐍 检查 Python 语法:"
python_files=(
    "api/index.py"
    "app/main.py"
    "app/api/routes.py"
    "app/api/ui_html.py"
)

syntax_ok=true
for file in "${python_files[@]}"; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - 语法错误"
        syntax_ok=false
    fi
done

echo ""

# 检查依赖
echo "📦 检查依赖文件:"
if [ -f "requirements.txt" ]; then
    echo "  ✅ requirements.txt 存在"
    echo "  📋 依赖列表:"
    cat requirements.txt | sed 's/^/    /'
else
    echo "  ❌ requirements.txt 不存在"
fi

echo ""

# 测试 UI HTML
echo "🎨 测试 UI HTML 模板:"
if python3 test_ui.py > /dev/null 2>&1; then
    echo "  ✅ UI HTML 模板正常"
else
    echo "  ❌ UI HTML 模板测试失败"
    syntax_ok=false
fi

echo ""
echo "=" * 60
if [ "$all_exist" = true ] && [ "$syntax_ok" = true ]; then
    echo "✅ 所有检查通过！可以部署到 Vercel"
    echo ""
    echo "运行以下命令部署:"
    echo "  ./deploy.sh       # 部署到预览环境"
    echo "  ./deploy.sh prod  # 部署到生产环境"
else
    echo "❌ 检查失败，请修复错误后再部署"
    exit 1
fi
echo "=" * 60
