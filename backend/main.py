"""
Bio-House - FastAPI backend.

Educational sandbox. Not a medical device.
"""

import json
import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from knowledge_base import get_all_scenarios, get_scenario, retrieve_knowledge
from agents import run_pipeline_stream
from settings import DEFAULT_LLM_BASE_URL, DEFAULT_LLM_MODEL, cors_config, is_llm_configured

_cors_origins, _cors_credentials = cors_config()

app = FastAPI(
    title="Bio-House API",
    description=(
        "Educational biomedical mechanism sandbox. "
        "Not a diagnostic device. Knowledge base is curated teaching notes, not live RAG."
    ),
    version="1.0.0-mvp",
)

# CORS_ORIGINS is a comma-separated list. Use * only for a public demo
# that does not send cookies. Local defaults cover Vite and a common alt port.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_credentials,
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
        "name": "Bio-House",
        "version": "1.0.0-mvp",
        "status": "online",
        "tagline": "Everybody lies, but metabolic pathways don't.",
        "educational_use_only": True,
        "diagnostic_device": False,
        "knowledge_base": "curated_chunks",
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

    if not is_llm_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "LLM_API_KEY is missing or still a placeholder. "
                "Copy backend/.env.example to backend/.env, set a real key, and restart. "
                "Do not commit backend/.env."
            ),
        )

    # Curated notes for preset cases; keyword overlap for custom text.
    scenario_id = request.scenario_id or "custom"
    scenario = get_scenario(scenario_id)
    entities = scenario.get("entities", []) if scenario else []
    knowledge_chunks = retrieve_knowledge(entities, scenario_id, request.case_input)

    async def event_generator():
        try:
            async for event in run_pipeline_stream(
                request.case_input,
                knowledge_chunks,
                scenario_id,
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
    """健康检查。不返回 API key。"""
    return {
        "status": "healthy",
        "llm_configured": is_llm_configured(),
        "model": os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL),
        "base_url": os.getenv("LLM_BASE_URL", DEFAULT_LLM_BASE_URL),
        "educational_use_only": True,
        "diagnostic_device": False,
        "knowledge_base": "curated_chunks",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
