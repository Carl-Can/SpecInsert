# Implementation Tasks: Bio-House 赛博豪斯 MVP

## Task 1: 后端项目初始化与依赖配置
- 创建 `backend/` 目录，初始化 Python venv 虚拟环境
- 写入 `requirements.txt`（fastapi, uvicorn, openai, pydantic, python-dotenv, sse-starlette, httpx）
- 创建 `.env.example` 模板文件（LLM_API_KEY / LLM_BASE_URL / LLM_MODEL）
- 在 venv 中执行 `pip install -r requirements.txt`

## Task 2: 知识库与预置剧本数据层
- 实现 `knowledge_base.py`，定义 `SCENARIOS` 字典（4 个剧本：biohacker/grapefruit/methanol/thalidomide）
- 每个剧本包含：id、title、emoji、description、input（默认输入文本）、entities（生化实体列表）
- 实现 `KNOWLEDGE_CHUNKS` 字典，收录 6 条生化文献知识片段（附来源标注）
- 实现 `retrieve_knowledge(entities, scenario_id) -> list[str]` 按剧本返回对应片段
- Depends on: Task 1

## Task 3: 三智能体 Agent 推理引擎
- 实现 `agents.py`，配置 `AsyncOpenAI` 客户端（从环境变量读取 base_url/api_key/model）
- 实现 `HOUSE_SYSTEM`、`CAMERON_SYSTEM`、`CUDDY_SYSTEM` 三个系统提示词
  - House: temperature=0.8，JSON 格式，3~4 假说 + house_comment + priority_investigation
  - Cameron: temperature=0.3，JSON 格式，evidence_analysis + metabolic_cascade_nodes
  - Cuddy: temperature=0.2，JSON 格式，ces_analysis（强制双侧）+ final_diagnosis
- 实现 `run_house(case_input) -> dict`
- 实现 `run_cameron(case_input, house_output, knowledge_chunks) -> dict`
- 实现 `run_cuddy(case_input, house_output, cameron_output) -> dict`
- 实现 `run_pipeline_stream(case_input, knowledge_chunks) -> AsyncGenerator`，每阶段完成后 yield SSE 事件
- Depends on: Task 1

## Task 4: FastAPI 后端主入口与 SSE 接口
- 实现 `main.py`，注册 FastAPI 应用，配置 CORS（允许 localhost:5173/3000）
- 实现 `GET /` 服务信息端点
- 实现 `GET /api/health` 健康检查端点（返回 llm_configured 字段）
- 实现 `GET /api/scenarios` 剧本列表端点
- 实现 `GET /api/scenarios/{scenario_id}` 剧本详情端点
- 实现 `POST /api/diagnose/stream`，接收 `{case_input, scenario_id}`，返回 SSE StreamingResponse
  - SSE 格式：`data: <json>\n\n`
  - 每阶段事件：`house_thinking / house_done / cameron_thinking / cameron_done / cuddy_thinking / cuddy_done / complete / error`
- Depends on: Task 2, Task 3

## Task 5: 前端项目初始化
- 使用 `npm create vite@latest frontend -- --template react-ts` 创建项目
- 执行 `npm install` 安装基础依赖
- 配置 `tsconfig.app.json`（`verbatimModuleSyntax: true`，所有类型导入用 `import type`）
- 验证 `npm run build` 通过
- Depends on: Task 1

## Task 6: 前端类型定义与 API 客户端
- 创建 `src/types.ts`，定义所有接口：Scenario / HouseOutput / CameronOutput / CuddyOutput / DiagnosisState / SSEEvent 等
- 创建 `src/api.ts`，实现：
  - `fetchScenarios()` → GET /api/scenarios
  - `fetchScenario(id)` → GET /api/scenarios/{id}
  - `checkHealth()` → GET /api/health
  - `streamDiagnose(request, onEvent)` → POST /api/diagnose/stream（SSE 解析，`data: ` 前缀处理）
- Depends on: Task 5

## Task 7: 全局样式与动效定义
- 创建 `src/index.css`，定义 CSS 变量（赛博医学深色主题：--bg-primary、--accent-blue、--accent-green 等）
- 实现关键动画 keyframes：
  - `slide-in-up`（卡片浮现）
  - `strike-through`（假说证伪红线划掉）
  - `glow-green`（确认假说荧光）
  - `typing-dot`（Agent 思考中三点动画）
  - `spin`（加载旋转）
- Depends on: Task 5

## Task 8: HypothesisCard 组件
- 实现 `src/components/HypothesisCard.tsx`
- Props: `hypothesis: Hypothesis, cesAnalysis?: CESAnalysis, isAnimating?: boolean`
- 展示：假说 ID 标签、标题、置信度进度条、机制描述、关键生物标志物、House 俏皮话
- 根据 `verdict` 切换视觉状态：
  - `REFUTED`：红线对角划掉动效 + 透明度 0.65 + 标题 line-through
  - `CONFIRMED`：绿色荧光边框 + glow-green 动画
  - `PROBABLE`：琥珀色边框
  - `INSUFFICIENT_EVIDENCE`：紫色边框
- Depends on: Task 6, Task 7

## Task 9: MetabolicGraph SVG 拓扑图组件
- 实现 `src/components/MetabolicGraph.tsx`
- Props: `nodes: CascadeNode[]`
- 收集所有唯一节点，按网格布局（4 列）分配坐标
- 使用 SVG `<defs>` 定义三种箭头 marker（activates/inhibits/converts）
- 节点渲染：圆角矩形 + 居中文字（超 12 字截断 + 省略号）
- 边渲染：二次贝塞尔曲线，`inhibits` 用红色虚线，标注 edge label
- Depends on: Task 6

## Task 10: AgentStatus 进度状态组件
- 实现 `src/components/AgentStatus.tsx`
- Props: `stage: DiagnosisStage, statusMessage: string`
- 展示三个 Agent 卡片（House / Cameron / Cuddy），按 stage 切换状态：
  - idle：灰色边框
  - thinking：蓝色边框 + 脉冲光晕 + 三点 typing 动画
  - done：绿色边框 + 对勾图标
- 展示当前状态消息（旋转加载图标 + 文字）
- Depends on: Task 6, Task 7

## Task 11: FinalVerdict 最终裁决组件
- 实现 `src/components/FinalVerdict.tsx`
- Props: `cuddy: CuddyOutput`
- 展示：Cuddy 裁决宣言（斜体引用样式）、一句话白板总结（大字高亮）、完整生化机制、临床干预建议、安全警示（黄色警告框）
- 整体绿色荧光边框 + glow-green 动画，表示"案件已结案"
- Depends on: Task 6, Task 7

## Task 12: Sidebar 侧边栏组件
- 实现 `src/components/Sidebar.tsx`
- Props: `scenarios, activeId, onSelect, onNewCase`
- 展示 Bio-House Logo、格言、"新建自由推演"按钮、剧本列表
- 激活剧本高亮蓝色边框，悬停微亮效果
- 底部显示版本信息
- Depends on: Task 6

## Task 13: Whiteboard 白板主舞台组件
- 实现 `src/components/Whiteboard.tsx`
- Props: `state: DiagnosisState`
- stage=idle 时渲染引导占位页（Logo + 功能说明 + 四个特性卡片）
- stage 进入 house_done 后渲染 House 假说区（评语 + 卡片横排 + 优先调查方向）
- stage 进入 cameron_done 后追加 Cameron 证据区（评述 + 证据列表 + SVG 拓扑图）
- stage 进入 cuddy_done 后追加 FinalVerdict 组件（使用 `cesMap` 将 CES 分析关联到对应假说卡片）
- 白板区域可纵向滚动
- Depends on: Task 8, Task 9, Task 10, Task 11

## Task 14: App 主应用组装
- 实现 `src/App.tsx`，整合所有状态与组件：
  - `useEffect` 启动时检查后端健康状态
  - `useEffect` 在后端在线后加载剧本列表
  - 顶部状态栏：后端在线/离线指示灯、LLM 配置状态
  - 左侧 `<Sidebar>`，右侧 `<Whiteboard>` + 底部输入区
  - 底部输入区：`<textarea>`（Ctrl+Enter 触发）+ "启动会诊"按钮（推理中显示旋转动画）
  - `streamDiagnose` 回调中按 stage 更新 `DiagnosisState`
- Depends on: Task 12, Task 13

## Task 15: 端到端联调与验证
- 启动后端（`uvicorn main:app --reload`）和前端（`npm run dev`）
- 对 4 个预置剧本分别执行完整三阶段推理，验证 SSE 事件流完整性
- 验证假说卡片动效：证伪红线、确认荧光
- 验证生化拓扑图正确渲染边和节点
- 验证后端不可达时前端正确禁用提交
- 编写 `start.sh` 一键启动脚本
- Depends on: Task 4, Task 14
