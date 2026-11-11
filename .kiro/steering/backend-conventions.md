---
inclusion: fileMatch
fileMatchPattern: "backend/**/*.py"
---

# 后端开发规范

## 环境

- Python 版本：3.12（`backend/venv` 中的解释器）
- 安装依赖：`backend/venv/bin/pip install -r backend/requirements.txt`
- 运行服务：`cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000`
- 导入验证：`backend/venv/bin/python -c "import main, agents, knowledge_base"`

## FastAPI 约定

- 路由统一加 `/api/` 前缀（除根路径 `/` 和 `/api/health`）
- 请求体用 Pydantic `BaseModel` 定义，字段加 `Optional` 时提供默认值
- SSE 路由返回 `StreamingResponse(generator, media_type="text/event-stream")`
- SSE 每条事件格式严格为：`f"data: {json.dumps(event, ensure_ascii=False)}\n\n"`
- CORS 白名单：`http://localhost:5173`、`http://localhost:3000`、`http://127.0.0.1:5173`

## Agent 调用约定

- 使用 `AsyncOpenAI`，从 `.env` 读取 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`
- 所有 Agent 调用必须加 `response_format={"type": "json_object"}`
- 返回值用 `json.loads(response.choices[0].message.content)` 解析
- 异常用 `try/except Exception as e` 捕获，yield `{"stage": "error", "message": str(e)}` 后 `return`

## 知识库扩展规则

新增知识片段时：
1. 在 `KNOWLEDGE_CHUNKS` 字典中添加条目，key 为 `snake_case` 描述
2. 片段首行必须包含 `[文献来源: 期刊名 年份]` 标注
3. 在 `retrieve_knowledge()` 函数的对应 `scenario_id` 分支中引用
4. 每个场景的知识片段控制在 3~5 条，避免超出 LLM 上下文窗口

## 禁止事项

- 禁止在代码中硬编码 API Key
- 禁止 `import *`
- 禁止在同步函数中调用 `AsyncOpenAI`（必须在 `async def` 中使用 `await`）
- 禁止修改 `.env` 中已有的字段名（会破坏 `agents.py` 的 `os.getenv` 调用）
