---
inclusion: always
---

# Bio-House 赛博豪斯 — 项目全局规范

## 项目定位

Bio-House 是一个模拟《豪斯医生》诊断室的**多智能体对抗性 Agentic RAG 系统**，  
面向生物黑客松赛事（Hackathon），核心卖点是三 Agent 假说生成-循证-证伪对抗流水线和  
具备动效的"赛博医学白板"UI。

## 目录结构

```
SpecInsert/
├── backend/           # Python 3.12 + FastAPI 后端
│   ├── venv/          # Python 虚拟环境（pip install 路径：venv/bin/pip）
│   ├── main.py        # FastAPI 主入口
│   ├── agents.py      # 三 Agent 推理引擎
│   ├── knowledge_base.py  # 预置剧本 + 知识片段
│   └── .env           # LLM 配置（不提交 git）
├── frontend/          # React 19 + TypeScript + Vite
│   └── src/
│       ├── types.ts
│       ├── api.ts
│       ├── App.tsx
│       └── components/
├── .kiro/             # Kiro 配置
│   ├── specs/bio-house-mvp/   # Spec 文档
│   ├── steering/      # 引导文件
│   └── hooks/         # 自动化钩子
└── start.sh           # 一键启动脚本
```

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React 19, TypeScript, Vite, 纯 CSS 动效（无额外 UI 库）|
| 后端 | Python 3.12, FastAPI, Uvicorn, Pydantic v2 |
| LLM 通信 | `openai` Python SDK（OpenAI 兼容接口）|
| 流式输出 | SSE（Server-Sent Events），`sse-starlette` |
| 知识库 | MVP 阶段：Python 字典硬编码；后续可替换 ChromaDB |

## 关键约定

### 后端
- 虚拟环境激活：`source backend/venv/bin/activate`
- 所有 Agent 调用使用 `AsyncOpenAI`，`response_format={"type":"json_object"}`
- LLM 配置从 `.env` 读取，绝不硬编码 API Key
- SSE 事件格式固定为 `data: <json>\n\n`，stage 字段为状态机节点

### 前端
- TypeScript 开启 `verbatimModuleSyntax`，类型导入必须用 `import type`
- 不引入 `React` 命名空间（React 19 自动 JSX 转换）
- 组件 props 均用 `interface Props` 定义，不用内联类型
- 样式全部内联 `style={{}}`，不新增 CSS 文件（已有 index.css 管理全局变量和动画）
- 颜色使用 CSS 变量：`var(--accent-blue)` / `var(--accent-green)` 等

### 通用
- 不引入未在 `requirements.txt` / `package.json` 中的新依赖，除非明确必要
- 生化知识片段附文献来源标注格式：`[文献来源: 期刊 年份; ...]`
