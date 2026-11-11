"""
Bio-House 赛博豪斯 - FastAPI 后端主入口
"""

import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from knowledge_base import get_all_scenarios, get_scenario, retrieve_knowledge
from agents import run_pipeline_stream

app = FastAPI(
    title="Bio-House 赛博豪斯 API",
    description="生物医药反直觉疑案与生化毒理证伪沙盒",
    version="1.0.0-mvp",
)

# CORS 配置（允许前端开发服务器访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── 数据模型 ──────────────────────────────────────────────────────────────────

class DiagnoseRequest(BaseModel):
    case_input: str
    scenario_id: Optional[str] = "custom"  # 预置剧本 ID 或 "custom"


# ─── 路由 ──────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "Bio-House 赛博豪斯",
        "version": "1.0.0-mvp",
        "status": "online",
        "tagline": "Everybody lies, but metabolic pathways don't.",
    }


@app.get("/api/scenarios")
async def list_scenarios():
    """获取所有预置剧本列表"""
    return {"scenarios": get_all_scenarios()}


@app.get("/api/scenarios/{scenario_id}")
async def get_scenario_detail(scenario_id: str):
    """获取特定剧本详情（含默认输入文本）"""
    scenario = get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"场景 '{scenario_id}' 不存在")
    return scenario


@app.post("/api/diagnose/stream")
async def diagnose_stream(request: DiagnoseRequest):
    """
    核心诊断接口 - SSE 流式输出
    流程: House(假说生成) → Cameron(循证检索) → Cuddy(CES证伪) → 最终裁决
    """
    if not request.case_input.strip():
        raise HTTPException(status_code=400, detail="case_input 不能为空")

    # 检索相关知识片段
    scenario = get_scenario(request.scenario_id)
    entities = scenario.get("entities", []) if scenario else []
    knowledge_chunks = retrieve_knowledge(entities, request.scenario_id)

    async def event_generator():
        try:
            async for event in run_pipeline_stream(
                request.case_input,
                knowledge_chunks,
                request.scenario_id,
            ):
                # SSE 格式: data: <json>\n\n
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.01)  # 给客户端处理时间
        except Exception as e:
            error_event = {"stage": "error", "message": str(e)}
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/health")
async def health_check():
    """健康检查"""
    import os
    has_key = bool(os.getenv("LLM_API_KEY") and os.getenv("LLM_API_KEY") != "demo-key")
    return {
        "status": "healthy",
        "llm_configured": has_key,
        "model": os.getenv("LLM_MODEL", "deepseek-chat"),
        "base_url": os.getenv("LLM_BASE_URL", "未配置"),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
