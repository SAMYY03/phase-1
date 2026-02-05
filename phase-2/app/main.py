"""Phase 2 Multi-Agent system (Semantic Kernel) .


- POST /chat_sk  : Semantic Kernel tool calling orchestrator
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.knowledge_rag_agent import KnowledgeRagAgent
from app.agents.mcp_action_agent import McpActionAgent
from app.agents.task_db_agent import TaskDbAgent
from app.core.event_bus import EventBus
from app.db.init_db import create_tables
from app.db.session import get_engine, get_session_factory
from app.mcp.actions import McpActions
from app.sk_plugins.manager_tools import ManagerToolsPlugin
from app.sk_runner import run_sk

app = FastAPI(title="Phase 2 Multi-Agent (Semantic Kernel)", version="1.0.0")

# -------------------- DB setup --------------------
DB_URL = "sqlite:///storage/chat.db"
_engine = get_engine(DB_URL)
create_tables(_engine)
_SessionLocal = get_session_factory(_engine)

# -------------------- EventBus + MCP wiring --------------------
_bus = EventBus()
_mcp_agent = McpActionAgent(actions=McpActions())
_bus.subscribe("TASK_CREATED", _mcp_agent.on_task_created)
_bus.subscribe("TASK_UPDATED", _mcp_agent.on_task_updated)

# -------------------- Agents --------------------
_rag_agent = KnowledgeRagAgent()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str


@app.post("/chat_sk", response_model=ChatResponse)
async def chat_sk(req: ChatRequest) -> ChatResponse:
    """Semantic Kernel chat endpoint (auto tool calling)."""
    session = _SessionLocal()
    try:
        task_agent = TaskDbAgent(session)
        tools = ManagerToolsPlugin(
            task_agent=task_agent,
            rag_agent=_rag_agent,
            event_bus=_bus,
        )
        answer = await run_sk(req.message, tools)
        return ChatResponse(answer=answer)
    finally:
        session.close()
