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
- CORS 来自环境变量 `CORS_ORIGINS`（逗号分隔）。未设置时默认 `http://localhost:5173`、`http://127.0.0.1:5173`、`http://localhost:3000`
- `CORS_ORIGINS=*` 时关闭 `allow_credentials`
- 占位 API key（空、`demo-key`、`your_api_key_here`、`sk-xxxxxxxxxxxxxxxx`）视为未配置；诊断接口返回 503

## Agent 调用约定

- 使用 `AsyncOpenAI`，从 `.env` 读取 `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`
- 所有 Agent 调用必须加 `response_format={"type": "json_object"}`
- 返回值用 `json.loads(response.choices[0].message.content)` 解析
- 异常用 `try/except Exception as e` 捕获，yield `{"stage": "error", "message": str(e)}` 后 `return`

## 知识库扩展规则

新增知识片段时：
1. 在 `KNOWLEDGE_CHUNKS` 字典中添加条目，key 为 `snake_case` 描述
2. 片段写成教学笔记，并在 `CHUNK_KEYWORDS` 里加上中英文关键词，供 `custom` 病例重叠匹配
3. 不要写看起来像真实论文的 `[文献来源: 期刊 年份]`。`retrieve_knowledge()` 会自动加上 illustrative / to-be-verified 前缀
4. 预置剧本放进 `PRESET_CHUNK_IDS`。每个场景控制在 3~5 条，避免超出上下文
5. 数字、监管编号和页码如果没有核对过，就不要写成已证实结果

## 禁止事项

- 禁止在代码中硬编码 API Key
- 禁止 `import *`
- 禁止在同步函数中调用 `AsyncOpenAI`（必须在 `async def` 中使用 `await`）
- 禁止修改 `.env` 中已有的字段名（会破坏 `agents.py` 的 `os.getenv` 调用）
