---
inclusion: always
---

# Bio-House 赛博豪斯 — 项目全局规范

## 项目定位

Bio-House 是一个**教育向机理沙盒**：三个 Agent 做假说、对照整理笔记、再双侧证伪，  
配一块有动效的白板。它致敬诊断室剧集的角色分工，不是官方衍生，也不是诊断设备。

知识库是 `backend/knowledge_base.py` 里的整理笔记，外加自定义病例的关键词重叠。  
不要把它写成向量 RAG、GraphRAG 或实时文献检索，除非代码里真的接上了这些组件。

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
| 知识库 | 进程内整理笔记 + 关键词重叠。不是向量库 |

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
- 教学笔记必须能被识别为示意文本。返回给模型的每条笔记以 `[ILLUSTRATIVE / to-be-verified]` 开头
- 不把占位 API key 或真实 `.env` 提交进 git
- `.kiro` 留在仓库根目录并且可被公开看到。hook 命令使用仓库相对路径
