#!/bin/bash

# 紫微斗数 Vercel 部署脚本

echo "🚀 开始部署到 Vercel..."

# 检查是否安装了 Vercel CLI
if ! command -v vercel &> /dev/null
then
    echo "❌ 未检测到 Vercel CLI"
    echo "📦 正在安装 Vercel CLI..."
    npm install -g vercel
fi

# 检查是否已登录
echo "🔐 检查 Vercel 登录状态..."
vercel whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "请先登录 Vercel："
    vercel login
fi

# 部署
echo "📤 开始部署..."
if [ "$1" == "prod" ]; then
    echo "🌟 部署到生产环境..."
    vercel --prod
else
    echo "🔍 部署到预览环境..."
    vercel
fi

echo "✅ 部署完成！"
