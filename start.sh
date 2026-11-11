#!/bin/bash
# Bio-House MVP 一键启动脚本

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "🧬 Bio-House 赛博豪斯 - 启动中..."
echo "========================================"

# 检查 .env
if ! grep -q "your_api_key_here" "$BACKEND_DIR/.env" 2>/dev/null; then
    echo "✅ .env 已配置"
else
    echo "⚠️  请先配置 $BACKEND_DIR/.env 中的 LLM_API_KEY"
    echo "   示例: LLM_API_KEY=sk-xxxxxxxxxxxxxxxx"
    echo "   支持: DeepSeek / OpenAI / Qwen 兼容接口"
fi

echo ""
echo "📡 启动后端 (FastAPI @ :8000)..."
cd "$BACKEND_DIR"
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"

sleep 2

echo ""
echo "🌐 启动前端 (Vite @ :5173)..."
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
echo "   前端 PID: $FRONTEND_PID"

echo ""
echo "========================================"
echo "✅ 启动完成！"
echo "   前端地址: http://localhost:5173"
echo "   后端 API: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 关闭所有服务"
echo "========================================"

# 等待并捕获退出信号
trap "echo ''; echo '🛑 正在关闭...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
