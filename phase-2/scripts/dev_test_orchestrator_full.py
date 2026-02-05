from pathlib import Path

from app.core.event_bus import EventBus
from app.mcp.actions import McpActions
from app.agents.mcp_action_agent import McpActionAgent

from app.db.session import get_engine, get_session_factory
from app.db.init_db import create_tables
from app.agents.task_db_agent import TaskDbAgent
from app.agents.knowledge_rag_agent import KnowledgeRagAgent
from app.orchestrator.orchestrator_agent import OrchestratorAgent

DB_URL = "sqlite:///storage/chat.db"

engine = get_engine(DB_URL)
create_tables(engine)
SessionLocal = get_session_factory(engine)

# Event system wiring
bus = EventBus()
mcp_agent = McpActionAgent(actions=McpActions())
bus.subscribe("TASK_CREATED", mcp_agent.on_task_created)
bus.subscribe("TASK_UPDATED", mcp_agent.on_task_updated)

# Phase 1 RAG inside Phase 2 agent
rag_agent = KnowledgeRagAgent()

with SessionLocal() as session:
    task_agent = TaskDbAgent(session)
    orchestrator = OrchestratorAgent(task_agent=task_agent, rag_agent=rag_agent, event_bus=bus)

    print("\n--- Create task use case ---")
    print(orchestrator.handle("Add a new task for Ahmed: review the sales report before Friday."))

    print("\n--- List tasks use case ---")
    print(orchestrator.handle("List all pending tasks for Ahmed"))

    print("\n--- Knowledge use case ---")
    print(orchestrator.handle("What is the company policy for sick leave?"))
