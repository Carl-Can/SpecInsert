# Technical Design: Bio-House 赛博豪斯 MVP

## Overview

Bio-House 是一个模拟《豪斯医生》诊断室的多智能体对抗性 Agentic RAG 系统。  
用户输入生物医药疑案，系统依次触发三个 LLM Agent 进行假说生成、循证检索与双侧证伪，  
结果通过 SSE 流式推送到前端动态白板展示。

**设计核心约束：**
- MVP 阶段无向量数据库，知识库以 Python 字典硬编码，可后续替换为 RAG 管道
- 前端无额外可视化库依赖，拓扑图用纯 SVG 手写实现
- 三 Agent 串行执行，每阶段完成后立即推送 SSE 事件，不等待全部完成

---

## Architecture

```
Browser (React + Vite)
  │
  │  SSE stream  (text/event-stream)
  │  POST /api/diagnose/stream
  │
FastAPI (Python 3.12)
  ├── main.py          — 路由、CORS、SSE 包装
  ├── agents.py        — 三 Agent 流水线（AsyncOpenAI）
  └── knowledge_base.py — 预置剧本 + 生化知识片段
        │
        │  OpenAI-compatible HTTP API
        │
LLM Provider (DeepSeek / OpenAI / Qwen / 本地 vLLM)
```

### 请求生命周期

```
用户点击"启动会诊"
  → POST /api/diagnose/stream  {case_input, scenario_id}
  → retrieve_knowledge(entities, scenario_id)   # 知识检索
  → run_house(case_input)                        # Agent 1：假说生成
  → SSE: {stage: "house_done", data: HouseOutput}
  → run_cameron(case_input, house_result, chunks) # Agent 2：循证
  → SSE: {stage: "cameron_done", data: CameronOutput}
  → run_cuddy(case_input, house_result, cameron_result) # Agent 3：证伪
  → SSE: {stage: "cuddy_done", data: CuddyOutput}
  → SSE: {stage: "complete", data: {house, cameron, cuddy}}
```

---

## Data Models

### SSE 事件结构

```typescript
interface SSEEvent {
  stage: 'house_thinking' | 'house_done' | 'cameron_thinking' |
         'cameron_done' | 'cuddy_thinking' | 'cuddy_done' |
         'complete' | 'error';
  message?: string;   // 状态描述文字
  data?: HouseOutput | CameronOutput | CuddyOutput | FullResult;
}
```

### Agent 输出结构

**HouseOutput**（Agent 1）
```typescript
interface HouseOutput {
  house_comment: string;         // House 毒舌评语
  hypotheses: Array<{
    id: string;                  // "H1", "H2", ...
    title: string;               // 假说标题
    mechanism: string;           // 生化机制摘要
    confidence: number;          // 初始置信度 0-100
    key_biomarker: string;       // 关键验证指标
    house_quip: string;          // House 俏皮话
  }>;
  priority_investigation: string; // 最优先调查方向
}
```

**CameronOutput**（Agent 2）
```typescript
interface CameronOutput {
  cameron_note: string;
  evidence_analysis: Array<{
    hypothesis_id: string;
    support_evidence: string[];
    evidence_strength: '强' | '中' | '弱';
    causal_chain: string;         // "A → B → C → D"
    vulnerability: string;
  }>;
  metabolic_cascade_nodes: Array<{
    from: string;
    to: string;
    type: 'activates' | 'inhibits' | 'converts';
    label: string;
  }>;
}
```

**CuddyOutput**（Agent 3）
```typescript
interface CuddyOutput {
  cuddy_verdict: string;
  ces_analysis: Array<{
    hypothesis_id: string;
    support_set: string[];
    refute_set: string[];
    verdict: 'CONFIRMED' | 'PROBABLE' | 'REFUTED' | 'INSUFFICIENT_EVIDENCE';
    updated_confidence: number;
    refute_reason?: string;
  }>;
  final_diagnosis: {
    confirmed_hypothesis: string;
    mechanism_summary: string;
    intervention: string;
    safety_warning?: string;
  };
  whiteboard_summary: string;
}
```

---

## Frontend Component Architecture

```
App.tsx
├── 状态管理 (useState): diagState, scenarios, caseInput, activeScenario
├── Sidebar.tsx           — 剧本列表 + 新建按钮
├── Whiteboard.tsx        — 主舞台，根据 diagState 渲染各阶段
│   ├── AgentStatus.tsx   — 三 Agent 进度条 + 当前状态消息
│   ├── HypothesisCard.tsx — 假说卡片，含证伪动效
│   ├── MetabolicGraph.tsx — 纯 SVG 拓扑图
│   └── FinalVerdict.tsx  — 最终裁决面板
└── 底部输入区 (inline)   — textarea + 启动按钮
```

### 状态机转换

```
idle
  → (用户提交) → house_thinking
  → (House完成) → house_done
  → (Cameron开始) → cameron_thinking
  → (Cameron完成) → cameron_done
  → (Cuddy开始) → cuddy_thinking
  → (Cuddy完成) → cuddy_done → complete
  → (任意阶段报错) → error
```

---

## Agent System Prompts 设计

### Dr. House（temperature: 0.8）
- 角色定位：反直觉、拒绝平庸假说、天才侦探风格
- 输出约束：JSON `response_format`，3~4 个假说，每个含 `id/title/mechanism/confidence/key_biomarker/house_quip`
- PatternBloom 映射：基于抽象生化拓扑模式（外源物摄入→代谢→靶点损伤）生成候选假说

### Cameron（temperature: 0.3）
- 角色定位：严密、客观、信奉文献证据
- 输出约束：JSON，对每个 House 假说输出 evidence_analysis + metabolic_cascade_nodes
- SkinMind 映射：通过 `causal_chain` 字段模拟 `probe_path`（生化通路最短连通子图）

### Cuddy（temperature: 0.2）
- 角色定位：审慎、安全红线、证据对称性代表
- 输出约束：JSON，强制双侧 CES，`verdict` 四选一，致命矛盾时必须给出 `refute_reason`
- Lightfoot 映射：verdict=REFUTED 的假说对应从白板"擦除"（前端红线划掉 + 透明度降低）

---

## Knowledge Base Design (MVP)

MVP 阶段采用硬编码字典，结构如下：

```python
SCENARIOS = {
  "biohacker": { id, title, emoji, description, input, entities },
  ...
}

KNOWLEDGE_CHUNKS = {
  "metformin_mtor": "...",   # 二甲双胍与 mTOR 交互文献片段
  "rapamycin_autophagy": "...",
  ...
}

def retrieve_knowledge(entities, scenario_id) -> list[str]:
    # 按 scenario_id 返回对应知识片段列表
    # 后续可替换为：embedding 检索 + BM25 混合重排
```

**后续扩展路径：**
1. 接入 PubMed API 实时检索摘要
2. 引入 ChromaDB / Qdrant 向量库，使用 BGE-m3 嵌入
3. BM25 + 向量混合重排（Reciprocal Rank Fusion）

---

## API Endpoints

| Method | Path | 描述 |
|--------|------|------|
| GET | `/` | 服务信息 |
| GET | `/api/health` | 健康检查（含 LLM 配置状态）|
| GET | `/api/scenarios` | 获取所有预置剧本列表 |
| GET | `/api/scenarios/{id}` | 获取剧本详情（含默认输入文本）|
| POST | `/api/diagnose/stream` | **核心**：SSE 流式三 Agent 推理 |

---

## LLM Configuration

通过 `.env` 文件配置，支持所有 OpenAI 兼容接口：

```
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.deepseek.com/v1   # 或 OpenAI / Qwen / 本地 vLLM
LLM_MODEL=deepseek-chat
```

Agent 参数：
- House: `temperature=0.8, max_tokens=1500`
- Cameron: `temperature=0.3, max_tokens=2000`
- Cuddy: `temperature=0.2, max_tokens=2000`
- 全部使用 `response_format={"type": "json_object"}` 保证 JSON 输出

---

## Error Handling

| 错误场景 | 处理方式 |
|---------|---------|
| LLM API 超时/限流 | try/except 捕获，SSE 推送 `{stage: "error", message}` |
| JSON 解析失败 | `json.loads` 异常，推送错误事件，前端显示原始文本 |
| 后端不可达 | 前端 health check 失败，禁用提交按钮 |
| 推理中重复提交 | 前端 `isRunning` 状态锁，按钮不可点击 |

---

## Testing Strategy

**后端：**
- 使用 `pytest` + `httpx.AsyncClient` 测试 API 端点
- Mock `AsyncOpenAI` 客户端测试 Agent 逻辑
- 验证 SSE 事件序列完整性

**前端：**
- 使用 Vitest + React Testing Library
- 测试 `HypothesisCard` 在不同 verdict 下的渲染
- 测试 SSE 事件到 diagState 的状态转换逻辑
