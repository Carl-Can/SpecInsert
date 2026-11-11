# Requirements: Bio-House 赛博豪斯 MVP

## 1. 预置剧本加载

WHEN 用户打开应用
THE SYSTEM SHALL 从后端 `/api/scenarios` 接口加载 4 个预置剧本列表并展示在侧边栏

WHEN 用户点击侧边栏中的某个剧本
THE SYSTEM SHALL 将该剧本的默认输入文本填入底部输入框，并清空当前白板状态

WHEN 用户点击"新建自由推演"
THE SYSTEM SHALL 清空输入框与白板，聚焦输入框等待用户输入

## 2. 三智能体推理流水线

WHEN 用户点击"启动会诊"或按 Ctrl+Enter
THE SYSTEM SHALL 通过 SSE 流式接口依次触发 House → Cameron → Cuddy 三个 Agent 推理阶段

WHEN House Agent 推理完成
THE SYSTEM SHALL 在白板上实时渲染 3~4 张假说卡片，每张含假说标题、生化机制、初始置信度和 House 俏皮话

WHEN Cameron Agent 推理完成
THE SYSTEM SHALL 在白板上展示每个假说的证据强度、生化因果链（`A → B → C` 格式）、支持证据列表和潜在漏洞

WHEN Cameron 返回 `metabolic_cascade_nodes` 数据
THE SYSTEM SHALL 渲染 SVG 生化因果拓扑图，用绿色箭头表示激活、红色虚线箭头表示抑制、蓝色箭头表示转化

WHEN Cuddy Agent 推理完成
THE SYSTEM SHALL 对每个假说展示 CES 双侧证据集（支持集 + 反驳集），更新置信度，并渲染最终裁决面板

WHEN 某假说被 Cuddy 判定为 `REFUTED`
THE SYSTEM SHALL 在假说卡片上叠加红色对角划线动效并降低卡片透明度

WHEN 某假说被判定为 `CONFIRMED` 或 `PROBABLE`
THE SYSTEM SHALL 对该卡片施加青绿色荧光动效并置顶显示

## 3. CES 双侧证据集仲裁

WHEN Cuddy 对任意假说分析时
THE SYSTEM SHALL 强制生成 support_set（支持证据列表）和 refute_set（反驳证据列表），不允许单边输出

WHEN 假说存在与实验室数据直接矛盾的证据
THE SYSTEM SHALL 将其 verdict 标记为 `REFUTED` 并填写 `refute_reason`

WHEN 所有假说分析完毕
THE SYSTEM SHALL 输出 `final_diagnosis`，包含确诊假说 ID、完整生化机制总结、临床干预建议和安全警示

## 4. 生化因果拓扑图

WHEN Cameron 输出 `metabolic_cascade_nodes` 且节点数 ≥ 2
THE SYSTEM SHALL 渲染 SVG 拓扑图，节点为生化实体，边为有向箭头带标注

WHEN 边类型为 `inhibits`
THE SYSTEM SHALL 使用红色虚线箭头（strokeDasharray）表示抑制关系

WHEN 节点名称超过 12 个字符
THE SYSTEM SHALL 截断并追加省略号显示

## 5. 后端健康与 LLM 配置检查

WHEN 应用启动时
THE SYSTEM SHALL 请求 `/api/health` 并在顶部状态栏显示后端在线/离线状态

WHEN LLM_API_KEY 未配置，或仍是占位符（空字符串、`demo-key`、`your_api_key_here`、`sk-xxxxxxxxxxxxxxxx`）
THE SYSTEM SHALL 在状态栏显示"LLM 未配置"，并且 `POST /api/diagnose/stream` 返回 503，不向模型供应商发请求

WHEN 后端不可达
THE SYSTEM SHALL 禁用"启动会诊"按钮，并提示当前配置的 API 基址（`VITE_API_BASE_URL`，默认 `http://localhost:8000`）

## 6. 自由输入推演

WHEN 用户在输入框中输入自定义病例描述
THE SYSTEM SHALL 允许启动推演，scenario_id 传递为 "custom"

WHEN scenario_id 为 "custom"
THE SYSTEM SHALL 用病例原文和实体列表对整理过的教学笔记做关键词重叠，最多返回 3 条；没有任何重叠时返回空列表

WHEN 自定义病例没有命中教学笔记
THE SYSTEM SHALL 告诉 Cameron 本次没有整理过的笔记，并禁止把该轮说成文献检索或向量检索

## 7. 错误处理

WHEN 任意 Agent 推理阶段发生异常
THE SYSTEM SHALL 在白板上显示错误阶段名称和错误信息，停止流式输出

WHEN 推理正在进行中
THE SYSTEM SHALL 禁止用户重复提交，"启动会诊"按钮替换为旋转加载状态

## 8. 知识库与数据

WHEN 后端收到 `scenario_id` 为已知剧本的请求
THE SYSTEM SHALL 从知识库检索对应的生化文献片段并注入 Cameron Agent 的上下文

WHEN 知识库片段注入 Cameron
THE SYSTEM SHALL 在每条笔记前加上 `[ILLUSTRATIVE / to-be-verified]`，并要求 Cameron 把依据标成“示意/待核验”，不得把笔记里的期刊名、统计量或监管编号写成已核实文献

## 9. 教学免责声明

WHEN 用户打开应用
THE SYSTEM SHALL 在界面上同时展示英文和中文说明：这是教学沙盒，不是医疗器械，不能用于诊断、治疗或给药；House / Cameron / Cuddy 是非官方致敬，不是官方衍生

WHEN 最终裁决面板出现
THE SYSTEM SHALL 再次展示同一条教学免责声明，并把干预文案标成讨论，而不是医嘱

## 10. 可配置的 API 基址与 CORS

WHEN 构建或开发前端时设置了 `VITE_API_BASE_URL`
THE SYSTEM SHALL 用该地址请求后端；未设置时使用 `http://localhost:8000`

WHEN 后端设置了 `CORS_ORIGINS`（逗号分隔）
THE SYSTEM SHALL 只允许这些来源；未设置时允许本地 Vite 与 `localhost:3000`。值为 `*` 时允许任意来源并关闭 credentials

## 11. 可复现启动

WHEN 贡献者在干净克隆上运行 `./start.sh` 且 `backend/.env` 不存在
THE SYSTEM SHALL 从 `backend/.env.example` 复制出 `.env`（该文件被 gitignore），创建尚不存在的 venv，并在 key 仍是占位符时以非零状态退出，且不启动服务、不打印 key

WHEN key 已是真实值
THE SYSTEM SHALL 安装后端依赖，在缺少 `node_modules` 时安装前端依赖，然后启动 API 与 Vite
