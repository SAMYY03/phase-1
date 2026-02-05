from app.db.session import get_engine, get_session_factory
from app.db.init_db import create_tables
from app.agents.task_db_agent import TaskDbAgent
from app.orchestrator.orchestrator_agent import OrchestratorAgent

DB_URL = "sqlite:///storage/chat.db"

engine = get_engine(DB_URL)
create_tables(engine)
SessionLocal = get_session_factory(engine)

with SessionLocal() as session:
    task_agent = TaskDbAgent(session)
    orchestrator = OrchestratorAgent(task_agent=task_agent, rag_agent=None)

    print(orchestrator.handle("Add a new task for Ahmed review the sales report"))
    print(orchestrator.handle("List all pending tasks for Ahmed"))
