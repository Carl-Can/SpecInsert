"""
Bio-House 三智能体推理引擎
Agent 1: Dr. House  - 野性假说生成（PatternBloom 风格）
Agent 2: Cameron   - 循证检索与证据绑定（SkinMind 风格）
Agent 3: Cuddy     - CES 双侧证伪仲裁（Conformal Evidence Sets）
"""

import json
import os
from typing import AsyncGenerator
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# LLM 客户端配置
client = AsyncOpenAI(
    api_key=os.getenv("LLM_API_KEY", "demo-key"),
    base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
)
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# ─── Agent 系统提示词 ──────────────────────────────────────────────────────────

HOUSE_SYSTEM = """你是《Bio-House 赛博豪斯》中的 Dr. Gregory House。
你是一个桀骜不驯、反直觉、痛恨平庸假说的顶级诊断学家。
你的性格：讽刺、直接、天才，永远不接受"最常见的可能性"。

你的任务：
1. 分析患者症状/实验室数据/用药情况
2. 拒绝平庸诊断，提出3-4个野性、反直觉的生化假说
3. 每个假说必须有明确的生化机制猜想（即便还未验证）
4. 给每个假说打一个初始置信度（0-100%）
5. 识别最需要被验证的关键生化节点

输出格式（JSON）：
{
  "house_comment": "House的毒舌评语（1-2句，体现其个性）",
  "hypotheses": [
    {
      "id": "H1",
      "title": "假说标题",
      "mechanism": "生化机制简述（1-2句）",
      "confidence": 75,
      "key_biomarker": "需要验证的关键生物标志物或指标",
      "house_quip": "House对此假说的俏皮话"
    }
  ],
  "priority_investigation": "最优先需要调查的核心问题"
}"""

CAMERON_SYSTEM = """你是《Bio-House 赛博豪斯》中的 Dr. Cameron（循证医学侦探）。
你严密、客观、信奉数据与文献证据。你的工作是用真实生化知识为假说找证据。

给定知识库片段和House的假说，你的任务：
1. 评估每个假说的证据强度（文献支持度）
2. 提取关键分子机制细节
3. 建立生化因果链：A → B → C（使用 "→" 箭头表示）
4. 识别每个假说的核心证据支柱和潜在漏洞

输出格式（JSON）：
{
  "cameron_note": "Cameron的理性评述（1-2句）",
  "evidence_analysis": [
    {
      "hypothesis_id": "H1",
      "support_evidence": ["证据1（附来源标注）", "证据2"],
      "evidence_strength": "强/中/弱",
      "causal_chain": "A → B → C → D（生化因果链）",
      "vulnerability": "该假说的潜在漏洞或未解释现象"
    }
  ],
  "metabolic_cascade_nodes": [
    {"from": "分子A", "to": "分子B", "type": "activates|inhibits|converts", "label": "机制标注"}
  ]
}"""

CUDDY_SYSTEM = """你是《Bio-House 赛博豪斯》中的 Dr. Cuddy（CES双侧证伪仲裁官）。
你审慎、严格，代表患者安全与证据对称性。

你实施 Conformal Evidence Sets (CES) 双侧裁决：
- 对每个假说，必须同时提供"支持集（Support Set）"与"反驳集（Refute Set）"
- 有致命矛盾的假说必须被明确证伪（画叉）
- 最终输出：被证伪的假说列表 + 存活的假说 + 置信度更新 + 临床裁决

注意：你代表科学严谨性，任何未完成证据闭环的推论不得作为最终诊断依据。

输出格式（JSON）：
{
  "cuddy_verdict": "Cuddy的裁决宣言（1-2句，体现其权威性）",
  "ces_analysis": [
    {
      "hypothesis_id": "H1",
      "support_set": ["支持证据1", "支持证据2"],
      "refute_set": ["反驳证据1", "反驳证据2"],
      "verdict": "CONFIRMED|PROBABLE|REFUTED|INSUFFICIENT_EVIDENCE",
      "updated_confidence": 85,
      "refute_reason": "若被证伪，说明致命矛盾原因"
    }
  ],
  "final_diagnosis": {
    "confirmed_hypothesis": "最终确诊假说ID",
    "mechanism_summary": "完整生化机制总结（3-5句，严谨）",
    "intervention": "临床/生化干预建议",
    "safety_warning": "安全警示（如适用）"
  },
  "whiteboard_summary": "白板最终呈现的一句话诊断结论"
}"""

# ─── Agent 调用函数 ────────────────────────────────────────────────────────────

async def run_house(case_input: str, context: str = "") -> dict:
    """Agent 1: Dr. House 野性假说生成"""
    messages = [
        {"role": "system", "content": HOUSE_SYSTEM},
        {
            "role": "user",
            "content": f"病例输入：\n{case_input}\n\n背景上下文：\n{context}\n\n请以JSON格式输出你的鉴别诊断假说。",
        },
    ]
    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.8,  # House 需要创意
        max_tokens=1500,
    )
    return json.loads(response.choices[0].message.content)


async def run_cameron(
    case_input: str, house_output: dict, knowledge_chunks: list[str]
) -> dict:
    """Agent 2: Cameron 循证检索与证据分析"""
    knowledge_text = "\n---\n".join(knowledge_chunks) if knowledge_chunks else "暂无检索到的相关文献。"
    messages = [
        {"role": "system", "content": CAMERON_SYSTEM},
        {
            "role": "user",
            "content": f"""病例：
{case_input}

House的假说：
{json.dumps(house_output, ensure_ascii=False, indent=2)}

知识库检索结果：
{knowledge_text}

请分析每个假说的证据强度，并建立生化因果链。以JSON格式输出。""",
        },
    ]
    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.3,  # Cameron 需要严谨
        max_tokens=2000,
    )
    return json.loads(response.choices[0].message.content)


async def run_cuddy(
    case_input: str, house_output: dict, cameron_output: dict
) -> dict:
    """Agent 3: Cuddy CES 双侧证伪仲裁"""
    messages = [
        {"role": "system", "content": CUDDY_SYSTEM},
        {
            "role": "user",
            "content": f"""病例：
{case_input}

House假说：
{json.dumps(house_output, ensure_ascii=False, indent=2)}

Cameron证据分析：
{json.dumps(cameron_output, ensure_ascii=False, indent=2)}

请实施CES双侧证伪裁决，确定哪些假说被证伪，哪些保留，并给出最终诊断。以JSON格式输出。""",
        },
    ]
    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,  # Cuddy 需要最严谨
        max_tokens=2000,
    )
    return json.loads(response.choices[0].message.content)


async def run_pipeline_stream(
    case_input: str,
    knowledge_chunks: list[str],
    scenario_id: str = "custom",
) -> AsyncGenerator[dict, None]:
    """
    完整三智能体推理流水线（流式 SSE 输出）
    每个阶段完成后 yield 一个事件
    """
    # 阶段 1: House
    yield {"stage": "house_thinking", "message": "Dr. House 正在分析病例，准备提出反直觉假说..."}
    try:
        house_result = await run_house(case_input)
        yield {"stage": "house_done", "data": house_result}
    except Exception as e:
        yield {"stage": "error", "message": f"House Agent 错误: {str(e)}"}
        return

    # 阶段 2: Cameron
    yield {"stage": "cameron_thinking", "message": "Cameron 正在搜索文献证据，建立生化因果链..."}
    try:
        cameron_result = await run_cameron(case_input, house_result, knowledge_chunks)
        yield {"stage": "cameron_done", "data": cameron_result}
    except Exception as e:
        yield {"stage": "error", "message": f"Cameron Agent 错误: {str(e)}"}
        return

    # 阶段 3: Cuddy
    yield {"stage": "cuddy_thinking", "message": "Cuddy 正在实施 CES 双侧证伪仲裁，剔除错误假说..."}
    try:
        cuddy_result = await run_cuddy(case_input, house_result, cameron_result)
        yield {"stage": "cuddy_done", "data": cuddy_result}
    except Exception as e:
        yield {"stage": "error", "message": f"Cuddy Agent 错误: {str(e)}"}
        return

    # 最终汇总
    yield {
        "stage": "complete",
        "data": {
            "house": house_result,
            "cameron": cameron_result,
            "cuddy": cuddy_result,
        },
    }
