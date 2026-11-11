# 🧬 Bio-House 赛博豪斯 MVP

> "Everybody lies, but metabolic pathways don't."
> 
> 生物医药反直觉疑案与生化毒理证伪沙盒 · Hackathon Edition

## 快速启动

### 第一步：配置 LLM API Key

```bash
# 编辑后端环境变量
nano backend/.env
```

填写你的 API 配置：
```
LLM_API_KEY=sk-xxxxxxxxxxxxxxxx        # DeepSeek / OpenAI / Qwen 均可
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

### 第二步：启动服务

```bash
# 一键启动（前后端同时）
./start.sh
```

或分别启动：

```bash
# 后端（新终端）
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# 前端（新终端）
cd frontend
npm run dev
```

### 第三步：访问

- 前端界面：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## 项目结构

```
SpecInsert/
├── backend/
│   ├── venv/              # Python 虚拟环境（已创建）
│   ├── main.py            # FastAPI 主入口 + SSE 流式接口
│   ├── agents.py          # 三智能体推理引擎
│   │   ├── Dr. House      # 野性假说生成
│   │   ├── Cameron        # 循证检索与证据绑定
│   │   └── Dr. Cuddy      # CES 双侧证伪仲裁
│   ├── knowledge_base.py  # 4 个预置剧本 + 生化知识片段
│   ├── requirements.txt
│   └── .env               # LLM 配置（需填写）
├── frontend/
│   ├── src/
│   │   ├── App.tsx               # 主应用
│   │   ├── types.ts              # TypeScript 类型定义
│   │   ├── api.ts                # 后端通信（SSE 流式）
│   │   └── components/
│   │       ├── Sidebar.tsx       # 剧本选择侧边栏
│   │       ├── Whiteboard.tsx    # 鉴别诊断白板主舞台
│   │       ├── HypothesisCard.tsx # 假说卡片（含证伪动效）
│   │       ├── AgentStatus.tsx   # 三 Agent 进度状态
│   │       ├── MetabolicGraph.tsx # 生化因果 SVG 拓扑图
│   │       └── FinalVerdict.tsx  # 最终裁决面板
│   └── package.json
├── start.sh               # 一键启动脚本
└── BIO_HOUSE_AGENTIC_RAG_PRD.md
```

## 四个预置杀手级场景

| 场景 | 核心机制 |
|------|---------|
| 🔥 硅谷生物黑客猝死疑案 | Rapamycin+Metformin mTOR/AMPK 双锁 → 线粒体能量枯竭 |
| 💊 西柚汁+他汀肌溶解 | 呋喃香豆素 CYP3A4 自杀性抑制 → 血药暴增 → 横纹肌溶解 |
| 🍷 医用乙醇解甲醇机理 | ADH 竞争性底物占位 → 甲醇原形排出 |
| ✨ 沙利度胺分子胶反转 | CRBN-IKZF1/3 靶向降解 → 骨髓瘤细胞凋亡 |

## 支持的 LLM 接口

- **DeepSeek**（推荐）：`https://api.deepseek.com/v1`，模型 `deepseek-chat`
- **OpenAI**：`https://api.openai.com/v1`，模型 `gpt-4o`
- **Qwen**：`https://dashscope.aliyuncs.com/compatible-mode/v1`，模型 `qwen-plus`
- **本地 vLLM**：`http://localhost:8000/v1`，配置本地模型名
