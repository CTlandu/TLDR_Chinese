#!/bin/bash

# TLDR Chinese 本地开发启动脚本
# 该脚本会在两个终端窗口中分别启动前端和后端服务器

echo "🚀 启动 TLDR Chinese 本地开发环境"
echo ""

# 获取项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 检查依赖
echo "📦 检查依赖..."
if [ ! -d "$PROJECT_DIR/node_modules" ]; then
    echo "❌ 前端依赖未安装，请先运行: npm install"
    exit 1
fi

if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ 后端依赖未安装，请先运行: pip3 install -r requirements.txt"
    exit 1
fi

echo "✅ 依赖检查完成"
echo ""

# 检查环境变量
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  警告：未找到 .env 文件"
    echo "   某些功能可能无法正常工作"
    echo ""
fi

# 启动后端（在新终端窗口）
echo "🔧 启动后端服务器..."
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$PROJECT_DIR' && echo '🐍 Flask 后端服务器' && echo '==================' && echo '' && python3 run.py"
end tell
EOF

sleep 2

# 启动前端（在新终端窗口）
echo "🎨 启动前端服务器..."
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$PROJECT_DIR' && echo '⚡️ Vite 前端服务器' && echo '==================' && echo '' && npm run dev"
end tell
EOF

echo ""
echo "✅ 启动完成！"
echo ""
echo "📍 前端地址: http://localhost:5173"
echo "📍 后端地址: http://localhost:5000"
echo ""
echo "💡 提示："
echo "   - 两个服务器会在新的终端窗口中运行"
echo "   - 按 Ctrl+C 可以停止相应的服务器"
echo "   - 修改代码会自动重新加载"
echo ""

