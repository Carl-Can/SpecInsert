"""
Bio-House curated teaching notes.

These are hand-written mechanism sketches for four preset cases. They are not
a vector index and not verified citations. Every chunk returned to an agent is
prefixed so the model must treat it as illustrative / to-be-verified.

Custom cases (scenario_id "custom") get up to three notes whose keywords
overlap the free-text input. If nothing overlaps, the list is empty and the
model is told it has no curated notes.
"""

SCENARIOS = {
    "biohacker": {
        "id": "biohacker",
        "title": "硅谷生物黑客猝死疑案",
        "emoji": "🔥",
        "description": "雷帕霉素 + 二甲双胍 + 司美格鲁肽叠服致高乳酸血症",
        "input": """患者：35岁男性，硅谷工程师，自行叠服以下方案：
- 雷帕霉素 (Rapamycin) 5mg/周（抗衰延寿方案）
- 二甲双胍 (Metformin) 1000mg/天
- 司美格鲁肽 (Semaglutide) 0.5mg/周
- NMN 1000mg/天

症状：突发极度虚弱、全身肌肉酸痛、体温37.1°C（正常），
实验室：乳酸 6.2 mmol/L（正常<2.0），肝酶 ALT 68 U/L（轻度升高），
CK 正常，肾功能轻度下降。请展开鉴别诊断。""",
        "entities": ["雷帕霉素", "二甲双胍", "司美格鲁肽", "NMN", "mTOR", "AMPK", "线粒体复合物I", "乳酸"],
    },
    "grapefruit": {
        "id": "grapefruit",
        "title": "餐桌上的隐形杀手",
        "emoji": "💊",
        "description": "西柚汁 CYP3A4 抑制 + 他汀类药物致横纹肌溶解",
        "input": """患者：62岁女性，高脂血症患者，规律服用阿托伐他汀 20mg/天 已2年。
近1周开始每天饮用1瓶"天然健康混合果汁"（含西柚成分）。
症状：严重肌肉无力、酱油色尿（肌红蛋白尿），
实验室：CK 12,000 U/L（正常<200），肌酐升高，肝酶异常。
无剧烈运动史，无病毒感染症状。请展开鉴别诊断。""",
        "entities": ["阿托伐他汀", "西柚汁", "呋喃香豆素", "CYP3A4", "P-gp", "肌红蛋白", "横纹肌溶解"],
    },
    "methanol": {
        "id": "methanol",
        "title": "以毒攻毒：医用乙醇解甲醇",
        "emoji": "🍷",
        "description": "甲醇中毒急救中乙醇脱氢酶竞争性抑制原理",
        "input": """患者：28岁男性，夜市聚餐后2小时就医。
症状：视物模糊（雪盲感）、恶心呕吐、严重头痛、呼吸急促，
实验室：pH 7.15（严重代谢性酸中毒），阴离子间隙 28（升高），
甲醇血液浓度 0.08%，同伴反映饮用了低价散装白酒。
急诊科考虑给予医用乙醇治疗，请解释其生化机理并评估风险。""",
        "entities": ["甲醇", "乙醇", "醇脱氢酶ADH", "甲醛", "甲酸", "线粒体细胞色素c氧化酶", "视网膜"],
    },
    "thalidomide": {
        "id": "thalidomide",
        "title": "幽灵档案：沙利度胺老药新用反转",
        "emoji": "✨",
        "description": "从致畸恶魔到多发性骨髓瘤分子胶靶向降解神药",
        "input": """查询：沙利度胺（Thalidomide）1950-60年代因导致"海豹儿"（海豹肢症）
被全球禁用。然而1998年FDA重新批准其用于麻风结节性红斑，
2006年批准联合地塞米松用于多发性骨髓瘤一线治疗。
请从分子机制层面解释：
1. 其致畸机制（血管新生抑制）
2. 为何同一机制反而在骨髓瘤中有治疗价值？
3. Cereblon (CRBN) 蛋白与IKZF1/IKZF3降解的分子胶机制是什么？""",
        "entities": ["沙利度胺", "Cereblon/CRBN", "IKZF1", "IKZF3", "E3泛素连接酶", "血管新生", "蛋白降解靶向(PROTAC/分子胶)"],
    },
}

ILLUSTRATIVE_PREFIX = (
    "[ILLUSTRATIVE / to-be-verified — curated teaching note, not a verified citation. "
    "Do not treat journal names, years, statistics, or report IDs below as confirmed sources.]\n"
)

# Teaching sketches. Headers used to look like papers; they are not citations.
KNOWLEDGE_CHUNKS = {
    "metformin_mtor": """
[Illustrative sketch only — not a citable paper]
二甲双胍常被描述为抑制线粒体复合物 I（NADH:泛醌氧化还原酶），从而降低 ATP/ADP 比值并激活 AMPK。
雷帕霉素同时抑制 mTORC1 时，能量感知与自噬信号可能叠在一起：
- 二甲双胍：复合物 I 抑制 → AMP 升高 → AMPK 激活 → 自噬启动信号
- 雷帕霉素：mTORC1 抑制 → 自噬通量增加
教学推演：在能量已经不足时，两药叠用可能让线粒体产能下降、糖酵解代偿、乳酸升高。
数字未核验：本仓库没有核实过“乳酸升高倍数、置信区间或 p 值”，不要把任何具体统计量写成实验结果。
""",
    "rapamycin_autophagy": """
[Illustrative sketch only — not a citable paper]
雷帕霉素作为 mTOR 抑制剂的教学路径：
1. mTORC1 抑制 → S6K1/4E-BP1 去磷酸化 → 蛋白质合成减少
2. ULK1 激活 → 自噬启动（线粒体质量控制的常用讲法）
3. 长期或高剂量时，mTORC2 也可能间接受影响 → AKT 信号下调，这一步争议更大，必须标成待核验
反例也要保留：有动物研究讨论过雷帕霉素与二甲双胍的寿命相关组合，但那些方案不是本病例里的急性自行叠服。
具体“乳酸清除率下降百分之多少”未在本仓库核验。
""",
    "semaglutide_gut": """
[Illustrative sketch only — not a citable paper]
司美格鲁肽（GLP-1 受体激动剂）会延迟胃排空，这是较公认的药理作用方向。
教学推演：二甲双胍若因此在小肠停留更久，吸收达峰可能改变，个体差异很大。
本片段不引用任何监管病例编号。不要发明 MedWatch / FAERS ID。
是否因此造成乳酸酸中毒，要当成待核验的风险假说，而不是已证实的不良反应系列。
""",
    "cyp3a4_grapefruit": """
[Illustrative sketch only — not a citable paper]
西柚中的呋喃香豆素（包括 bergamottin 与 6',7'-dihydroxybergamottin）可以抑制肠道 CYP3A4，
这是真实且写进许多药品说明书的相互作用方向。部分呋喃香豆素被称为机制性（自杀性）抑制剂。
阿托伐他汀的首过代谢部分依赖 CYP3A4，肠道酶被抑制后暴露量可以上升，并可能连带影响 P-gp。
后果链教学：他汀暴露升高 → 骨骼肌毒性风险上升 → 严重时可至横纹肌溶解。
具体升高倍数因药物、果汁剂量和个体而差很多。不要把“8–12 倍”或“Cmax +770%”写成已核实数字；
辛伐他汀通常比阿托伐他汀对西柚更敏感，本病例写的是阿托伐他汀。
""",
    "methanol_adh": """
[Illustrative sketch only — not a citable paper]
甲醇本身不是主要毒物，其代谢产物才是。教学路径：
甲醇 → 醇脱氢酶 ADH → 甲醛 → 醛脱氢酶 ALDH → 甲酸。
甲酸可抑制线粒体细胞色素 c 氧化酶；视网膜富含这一酶，所以视力损伤被放在机制链条的末端。
乙醇解毒的教学讲法是竞争性底物：乙醇对 ADH 的亲和力高于甲醇，维持一定血乙醇浓度可以让甲醇暂时不被代谢，
再以原形经肾或经透析清除。叶酸常被写成帮助甲酸代谢的辅助措施。
甲吡唑（fomepizole）是更特异的 ADH 抑制剂。Km 的具体毫摩尔数未在本仓库逐条核对，引用时标为待核验。
""",
    "thalidomide_crbn": """
[Illustrative sketch only — not a citable paper]
方向性背景（仍需回原论文核对，不要把本段当参考文献）：
沙利度胺结合 Cereblon（CRBN）。CRBN 是 CRL4 E3 连接酶的底物受体。
常被提到的原始靶点论文是 Ito et al., Science 2010（沙利度胺致畸与 CRBN）。
IKZF1/IKZF3 在多发性骨髓瘤中被降解，常被追溯到 2014 年的 Science 论文（Krönke et al.; Lu et al.），
而不是一份笼统的“Cell 2023 / Nature 2024”引文。本仓库没有核对页码。
教学双面性：
- 肢芽发育中，相关底物包括 SALL4 等转录因子，降解后肢体发育受损（海豹肢的分子讲法之一）
- 浆细胞中，同一 CRBN 结合可以招募 IKZF1（Ikaros）和 IKZF3（Aiolos），进而压低 IRF4/MYC 生存程序
来那度胺、泊马度胺是后续类似物。这是分子胶降解剂的教学例子，不是本沙盒算出的治疗方案。
""",
}

PRESET_CHUNK_IDS = {
    "biohacker": ["metformin_mtor", "rapamycin_autophagy", "semaglutide_gut"],
    "grapefruit": ["cyp3a4_grapefruit"],
    "methanol": ["methanol_adh"],
    "thalidomide": ["thalidomide_crbn"],
}

# Lowercased substring match against the custom-case text and entity list.
CHUNK_KEYWORDS = {
    "metformin_mtor": [
        "二甲双胍", "metformin", "雷帕霉素", "rapamycin", "mtor", "ampk",
        "乳酸", "lactate", "nmn", "线粒体",
    ],
    "rapamycin_autophagy": [
        "雷帕霉素", "rapamycin", "mtor", "自噬", "autophagy", "ulk1",
    ],
    "semaglutide_gut": [
        "司美格鲁肽", "semaglutide", "glp-1", "glp1", "胃排空",
    ],
    "cyp3a4_grapefruit": [
        "西柚", "grapefruit", "他汀", "statin", "阿托伐他汀", "atorvastatin",
        "cyp3a4", "横纹肌", "rhabdomyolysis",
    ],
    "methanol_adh": [
        "甲醇", "methanol", "乙醇", "ethanol", "fomepizole", "甲吡唑",
        "甲酸", "视物模糊",
    ],
    "thalidomide_crbn": [
        "沙利度胺", "thalidomide", "cereblon", "crbn", "ikzf",
        "骨髓瘤", "myeloma", "来那度胺", "lenalidomide",
    ],
}

MAX_CUSTOM_CHUNKS = 3


def get_scenario(scenario_id: str) -> dict:
    return SCENARIOS.get(scenario_id, {})


def get_all_scenarios() -> list:
    return list(SCENARIOS.values())


def _label(chunk: str) -> str:
    text = chunk.strip()
    if text.startswith("[ILLUSTRATIVE"):
        return text
    return ILLUSTRATIVE_PREFIX + text


def retrieve_knowledge(
    entities: list[str] | None,
    scenario_id: str,
    case_input: str = "",
) -> list[str]:
    """Return labeled teaching notes for a preset case or a keyword-overlap custom case."""
    preset_ids = PRESET_CHUNK_IDS.get(scenario_id)
    if preset_ids is not None:
        return [_label(KNOWLEDGE_CHUNKS[chunk_id]) for chunk_id in preset_ids]

    haystack = " ".join(entities or [])
    if case_input:
        haystack = f"{haystack}\n{case_input}"
    haystack = haystack.lower()

    scored: list[tuple[int, str]] = []
    for chunk_id, keywords in CHUNK_KEYWORDS.items():
        hits = sum(1 for keyword in keywords if keyword.lower() in haystack)
        if hits:
            scored.append((hits, chunk_id))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [
        _label(KNOWLEDGE_CHUNKS[chunk_id])
        for _, chunk_id in scored[:MAX_CUSTOM_CHUNKS]
    ]
