#!/bin/bash

echo "🚀 开始部署 Flask 聊天项目..."

cd "$(dirname "$0")" || exit 1

# 拉取最新代码
echo "📥 正在拉取远程更新..."
git reset --hard
git pull || { echo "❌ 拉取失败"; exit 1; }

# 安装依赖
echo "📦 安装依赖..."
./venv/bin/pip install -r requirements.txt || { echo "❌ pip 安装失败"; exit 1; }

# 重启服务（交给用户手动或使用 supervisor）
echo "🔁 请手动重启您的服务（如使用：supervisorctl restart fink_chat）"
