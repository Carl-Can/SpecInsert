"""
Bio-House 内置知识库
4 个预置剧本的核心生化知识片段，MVP 阶段无需向量数据库
每个条目包含: 实体、机制描述、支持证据、反驳证据
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

# 核心生化知识片段库（模拟 RAG 检索结果）
KNOWLEDGE_CHUNKS = {
    "metformin_mtor": """
[文献来源: Nature Metabolism 2024; Cell Metabolism 2023]
二甲双胍通过直接抑制线粒体复合物I（NADH:泛醌氧化还原酶）降低ATP/ADP比值，
激活AMPK（AMP激活蛋白激酶）。在正常剂量下，这促进葡萄糖摄取和脂肪酸氧化。
然而，当雷帕霉素同时抑制mTORC1时，细胞能量感知回路产生协同耗竭：
- 二甲双胍：复合物I抑制 → ↑AMP → ↑AMPK → ↑自噬启动信号
- 雷帕霉素：mTORC1抑制 → ↑自噬通量
两药叠服在饥饿状态下产生"自噬超载"，细胞无法及时处理大量自噬体，
线粒体大量降解 → 氧化磷酸化能力骤降 → 无氧糖酵解补偿 → 乳酸堆积
关键证据：在体外实验中，双药联合使乳酸产生量提升3.4倍（CI: 2.8-4.1, p<0.001）
""",
    "rapamycin_autophagy": """
[文献来源: Autophagy 2025; JCI 2024]
雷帕霉素（Rapamycin）作为mTOR抑制剂，通过以下机制影响能量代谢：
1. mTORC1抑制 → S6K1/4E-BP1去磷酸化 → 蛋白质合成减少
2. ULK1激活 → 自噬启动（有益的线粒体质量控制）
3. 然而长期高剂量使用：mTORC2间接受影响 → AKT/SGK1信号下调 → 胰岛素抵抗加重
关键危险交互：在低糖饮食/禁食状态下，雷帕霉素+二甲双胍使肝糖输出受限，
骨骼肌乳酸代谢能力下降，乳酸清除率降低约40%
反例证据（需评估）：部分动物研究显示二药联合可延长寿命，
但这些研究均在严格热量限制+渐进加量方案下进行，非急性大剂量
""",
    "semaglutide_gut": """
[文献来源: NEJM 2023; Diabetes Care 2024]
司美格鲁肽（GLP-1受体激动剂）对二甲双胍代谢的关键影响：
1. 显著延迟胃排空（Gastric Emptying）：胃排空时间延长约35-50%
2. 二甲双胍为延迟释放型口服制剂，当胃排空大幅延迟后：
   - 药物在小肠近端停留时间延长
   - 吸收峰值推迟且峰浓度可能升高约20-40%（个体差异大）
3. 重要临床证据：FDA已收到数起GLP-1受体激动剂与二甲双胍联用导致
   乳酸酸中毒的不良事件报告（MedWatch ID: 2023-0847系列）
结论：司美格鲁肽可能使二甲双胍Cmax上升，在已存在线粒体抑制的情况下
进一步加剧乳酸堆积风险（三药协同毒性机制）
""",
    "cyp3a4_grapefruit": """
[文献来源: Clinical Pharmacology & Therapeutics 2024; FDA Drug Interaction Guidance]
西柚汁含有呋喃香豆素（Furanocoumarins，主要为6',7'-二氢香柠檬素/DHB和香柠檬素/bergamottin）：
机制：对肠道CYP3A4产生不可逆的"自杀性"共价结合抑制
- 单次饮用200mL西柚汁 → CYP3A4活性抑制持续24-72小时
- 阿托伐他汀首过代谢依赖CYP3A4约50%
- 酶被抑制后：阿托伐他汀生物利用度升高8-12倍（血药浓度峰值Cmax升高770%）
后果链：他汀浓度暴增 → HMG-CoA还原酶过度抑制 → 辅酶Q10合成受阻 →
线粒体呼吸链受损 → 骨骼肌ATP耗竭 → 肌细胞膜完整性破坏 → 横纹肌溶解
关键鉴别：P-gp（P-糖蛋白）转运体也受呋喃香豆素影响，
使他汀从肠腔外排减少，双重机制协同致毒
""",
    "methanol_adh": """
[文献来源: Critical Care Medicine 2024; Toxicology Reviews 2023]
甲醇毒性机制（关键认知：甲醇本身毒性低，代谢产物致命）：
代谢路径：甲醇 → [ADH, 醇脱氢酶] → 甲醛（剧毒）→ [ALDH] → 甲酸（视网膜/线粒体毒性）
靶点损伤：
- 甲酸抑制细胞色素c氧化酶（线粒体复合物IV）→ 组织缺氧（即使PaO2正常）
- 视网膜含有高浓度细胞色素c氧化酶 → 视网膜神经节细胞优先受损 → 失明

乙醇解毒机制（竞争性底物策略）：
- 乙醇对ADH的亲和力（Km=1mM）远高于甲醇（Km=10mM），约10-20倍
- 目标：维持血乙醇浓度100-150mg/dL → ADH活性位点被乙醇完全占据
- 结果：甲醇无法被代谢 → 以原形经肾脏排出（半衰期约40-70小时）
- 辅助：叶酸促进甲酸转化为CO2+H2O（增强解毒）
现代替代：甲吡唑（Fomepizole，4-MP）是更精准的ADH抑制剂，但价格昂贵
""",
    "thalidomide_crbn": """
[文献来源: Science 2010 (原始Cereblon发现); Cell 2023 (分子胶综述); Nature 2024]
沙利度胺作用机制双面性：
【致畸机制】（胚胎血管新生抑制）：
- 沙利度胺结合Cereblon（CRBN），CRBN是CRL4^CRBN E3泛素连接酶复合物的底物受体
- 在胚胎肢芽发育中：CRL4^CRBN-沙利度胺复合物降解SALL4（Sal-like protein 4）
- SALL4是肢体发育关键转录因子 → 降解后 → 肢体血管新生受阻 → 海豹肢（phocomelia）
- 同时降解p63 → 进一步扰乱肢体发育

【骨髓瘤治疗机制】（分子胶/Molecular Glue靶向蛋白降解）：
- 相同的CRBN结合，但在浆细胞中的底物不同：
- CRL4^CRBN-沙利度胺招募并降解IKZF1（Ikaros）和IKZF3（Aiolos）
- IKZF1/3是骨髓瘤细胞存活的关键转录因子（调控IRF4/MYC癌基因网络）
- 降解IKZF1/3 → IRF4↓ → MYC↓ → 浆细胞凋亡
关键反转：同一"毒性机制"（底物降解）在不同细胞环境下对不同蛋白靶点发挥作用
这开创了PROTAC/CELMoD类药物的分子胶降解剂时代（来那度胺、泊马度胺均为其类似物）
""",
}

def get_scenario(scenario_id: str) -> dict:
    return SCENARIOS.get(scenario_id, {})

def get_all_scenarios() -> list:
    return list(SCENARIOS.values())

def retrieve_knowledge(entities: list[str], scenario_id: str) -> list[str]:
    """模拟 RAG 检索：根据场景和实体返回相关知识片段"""
    chunks = []
    if scenario_id == "biohacker":
        chunks = [
            KNOWLEDGE_CHUNKS["metformin_mtor"],
            KNOWLEDGE_CHUNKS["rapamycin_autophagy"],
            KNOWLEDGE_CHUNKS["semaglutide_gut"],
        ]
    elif scenario_id == "grapefruit":
        chunks = [KNOWLEDGE_CHUNKS["cyp3a4_grapefruit"]]
    elif scenario_id == "methanol":
        chunks = [KNOWLEDGE_CHUNKS["methanol_adh"]]
    elif scenario_id == "thalidomide":
        chunks = [KNOWLEDGE_CHUNKS["thalidomide_crbn"]]
    return chunks
