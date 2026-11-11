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

from settings import DEFAULT_LLM_BASE_URL, DEFAULT_LLM_MODEL, is_llm_configured

load_dotenv()

# LLM 客户端配置。缺 key 时不把占位符当成可用配置；诊断入口会先拒绝请求。
client = AsyncOpenAI(
    api_key=os.getenv("LLM_API_KEY", "demo-key"),
    base_url=os.getenv("LLM_BASE_URL", DEFAULT_LLM_BASE_URL),
)
MODEL = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)


def require_llm_configured() -> None:
    if not is_llm_configured():
        raise RuntimeError(
            "LLM_API_KEY is missing or still a placeholder. "
            "Copy backend/.env.example to backend/.env and set a real key. "
            "Do not commit that file."
        )

# ─── Agent 系统提示词 ──────────────────────────────────────────────────────────

HOUSE_SYSTEM = """你是教育沙盒《Bio-House》里的 Dr. Gregory House。
这是对一部电视剧诊断室风格的非官方致敬，不是官方衍生作品，也不是医疗器械。
你是一个桀骜不驯、反直觉、痛恨平庸假说的角色。
你的性格：讽刺、直接，永远不接受"最常见的可能性"。
你产出的是教学假说，不是诊断、处方或给药建议。

你的任务：
1. 分析病例文本里的症状/实验室数据/用药情况
2. 拒绝平庸解释，提出3-4个野性、反直觉的生化假说
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

CAMERON_SYSTEM = """你是教育沙盒《Bio-House》中的 Dr. Cameron（机制核对角色）。
这是非官方致敬，不是医疗器械。你严密、客观，但你只能使用本次消息里给出的教学笔记和病例文本。

知识库笔记都带有 ILLUSTRATIVE / to-be-verified 标记。它们不是已核验论文，也不是实时检索结果。
禁止把笔记里的期刊名、年份、倍数、p 值、置信区间或监管编号写成已证实来源。
若笔记为空，就明确写“本次没有命中整理过的教学笔记”，不要假装做过文献检索。

给定教学笔记和 House 的假说，你的任务：
1. 评估每个假说与这些笔记的吻合程度（不是文献支持度）
2. 提取关键分子机制细节，并在 support_evidence 每条末尾标注“示意/待核验”
3. 建立生化因果链：A → B → C（使用 "→" 箭头表示）
4. 识别每个假说的核心依据和潜在漏洞

输出格式（JSON）：
{
  "cameron_note": "Cameron的理性评述（1-2句）",
  "evidence_analysis": [
    {
      "hypothesis_id": "H1",
      "support_evidence": ["机制要点（示意/待核验）", "另一条笔记中的对应关系（示意/待核验）"],
      "evidence_strength": "强/中/弱",
      "causal_chain": "A → B → C → D（生化因果链）",
      "vulnerability": "该假说的潜在漏洞或未解释现象"
    }
  ],
  "metabolic_cascade_nodes": [
    {"from": "分子A", "to": "分子B", "type": "activates|inhibits|converts", "label": "机制标注"}
  ]
}"""

CUDDY_SYSTEM = """你是教育沙盒《Bio-House》中的 Dr. Cuddy（CES双侧证伪仲裁角色）。
这是非官方致敬，不是医疗器械，不能给出真实世界的诊断或治疗指令。
你审慎、严格，要求证据对称。

你实施 Conformal Evidence Sets (CES) 双侧裁决：
- 对每个假说，必须同时提供"支持集（Support Set）"与"反驳集（Refute Set）"
- 有致命矛盾的假说必须被明确证伪（画叉）
- 最终输出：被证伪的假说列表 + 存活的假说 + 置信度更新 + 教学向裁决

注意：任何未完成证据闭环的推论不得写成确诊。
safety_warning 必须包含这句话：“教学沙盒输出，不是诊断或治疗依据；知识笔记为示意/待核验。”
intervention 只能写成教学讨论，并提醒用户去找有资质的专业人员，不要把剂量写成医嘱。

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
    if knowledge_chunks:
        knowledge_text = "\n---\n".join(knowledge_chunks)
    else:
        knowledge_text = (
            "本次没有命中任何整理过的教学笔记。"
            "不要声称进行了文献检索或向量检索。"
            "请把证据强度标为弱，并写明依据不足。"
        )
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
    require_llm_configured()

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
