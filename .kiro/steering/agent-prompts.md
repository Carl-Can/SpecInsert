---
inclusion: auto
name: agent-prompts
description: 三智能体系统提示词设计规范。在修改 agents.py 或调整 House/Cameron/Cuddy 提示词时使用。
---

# Bio-House 三智能体提示词设计规范

## 核心原则

三个 Agent 形成"假说生成 → 循证绑定 → 双侧证伪"的对抗闭环，每个 Agent 的 temperature 和角色定位严格区分：

| Agent | 角色 | Temperature | 核心约束 |
|-------|------|------------|---------|
| Dr. House | 破局先锋，野性猜想 | 0.8 | 拒绝平庸，提出 3~4 个反直觉假说 |
| Cameron | 机制核对 | 0.3 | 只对照本次给出的教学笔记，证据必须标成示意/待核验 |
| Dr. Cuddy | CES 仲裁官 | 0.2 | 强制双侧证据，致命矛盾必须证伪 |

## House 提示词关键要素

- **禁止**：接受"最常见的可能"作为首要假说
- **必须**：每个假说含 `id`（H1/H2...）、`title`、`mechanism`、`confidence`（0-100）、`key_biomarker`、`house_quip`
- **风格**：讽刺、直接，`house_comment` 体现其桀骜性格
- **PatternBloom 映射**：假说应遵循生化拓扑模式，如"外源物摄入 → 酶系竞争 → 底物蓄积 → 靶点损伤"

## Cameron 提示词关键要素

- **必须输出** `metabolic_cascade_nodes`：每条边含 `from`、`to`、`type`（activates/inhibits/converts）、`label`
- **生化因果链格式**：`A → B → C → D`，使用 `→` 箭头，不用其他符号
- **证据强度**：只能是 `强`/`中`/`弱` 三选一（前端按此映射颜色）
- **禁止**：把整理笔记说成已检索到的论文。`support_evidence` 要带“示意/待核验”
- 笔记为空时写明没有命中整理笔记，证据强度用 `弱`
- **SkinMind 映射**：`causal_chain` 字段模拟 `probe_path`，`metabolic_cascade_nodes` 模拟 `probe_relations`

## Cuddy 提示词关键要素

- **强制双侧**：每个假说必须同时有 `support_set`（≥1条）和 `refute_set`（≥1条），单边输出视为违规
- **verdict 四选一**：`CONFIRMED` / `PROBABLE` / `REFUTED` / `INSUFFICIENT_EVIDENCE`
- **REFUTED 时**：必须填写 `refute_reason`，说明与哪条实验数据直接矛盾
- **Lightfoot 映射**：`REFUTED` 假说对应前端红线划掉 + 透明度降低（视觉"从白板擦除"）
- **final_diagnosis 必填字段**：`confirmed_hypothesis`、`mechanism_summary`（3-5句）、`intervention`、`safety_warning`
- `safety_warning` 必须写明教学沙盒、不是诊断或治疗依据
- `intervention` 是教学讨论，不是医嘱；角色是非官方致敬

## 修改提示词时的注意事项

1. 修改后必须保持 `response_format={"type":"json_object"}` 不变
2. 若新增 JSON 字段，同步更新 `src/types.ts` 中对应的 TypeScript 接口
3. House temperature 不得低于 0.7（会丧失创意）
4. Cuddy temperature 不得高于 0.3（会产生迎合偏差）
5. 所有提示词中的 JSON 格式示例必须与 `types.ts` 保持一致
