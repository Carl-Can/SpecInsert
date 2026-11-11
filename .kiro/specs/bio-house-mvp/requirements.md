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

WHEN LLM_API_KEY 未配置（值为 "demo-key"）
THE SYSTEM SHALL 在状态栏显示"LLM 未配置"黄色警告图标

WHEN 后端不可达
THE SYSTEM SHALL 禁用"启动会诊"按钮，并提示用户启动后端服务

## 6. 自由输入推演

WHEN 用户在输入框中输入自定义病例描述
THE SYSTEM SHALL 允许启动推演，scenario_id 传递为 "custom"

WHEN scenario_id 为 "custom"
THE SYSTEM SHALL 不检索预置知识片段，让大模型基于自身知识生成假说

## 7. 错误处理

WHEN 任意 Agent 推理阶段发生异常
THE SYSTEM SHALL 在白板上显示错误阶段名称和错误信息，停止流式输出

WHEN 推理正在进行中
THE SYSTEM SHALL 禁止用户重复提交，"启动会诊"按钮替换为旋转加载状态

## 8. 知识库与数据

WHEN 后端收到 `scenario_id` 为已知剧本的请求
THE SYSTEM SHALL 从知识库检索对应的生化文献片段并注入 Cameron Agent 的上下文

WHEN 知识库片段注入 Cameron
THE SYSTEM SHALL 在 Cameron 的系统提示和用户消息中包含完整的文献来源标注
