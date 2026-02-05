"""Semantic Kernel tools for the Manager assistant.

This plugin exposes agent capabilities as tools (kernel functions) that
Semantic Kernel can call automatically.
"""

from __future__ import annotations

from semantic_kernel.functions import kernel_function

from app.agents.knowledge_rag_agent import KnowledgeRagAgent
from app.agents.task_db_agent import TaskDbAgent
from app.core.event_bus import Event, EventBus


class ManagerToolsPlugin:
    """Tools (functions) that Semantic Kernel can call automatically."""

    def __init__(self, task_agent: TaskDbAgent, rag_agent: KnowledgeRagAgent, event_bus: EventBus) -> None:
        self.task_agent = task_agent
        self.rag_agent = rag_agent
        self.event_bus = event_bus

    @kernel_function(
        name="create_task",
        description="Create a task for an assignee. Use when the user wants to add/create a task.",
    )
    def create_task(self, assignee: str, title: str) -> str:
        task = self.task_agent.create_task(assignee=assignee, title=title)

        # Trigger MCP via events
        self.event_bus.publish(
            Event(
                type="TASK_CREATED",
                payload={"task_id": task.id, "assignee": task.assignee, "title": task.title},
            )
        )

        return f"Task created for {task.assignee} (id={task.id}): {task.title}"

    @kernel_function(
        name="update_task_status",
        description="Update a task status by task id. Use when user says done/completed/cancelled/in progress.",
    )
    def update_task_status(self, task_id: int, status: str) -> str:
        task = self.task_agent.update_task_status(task_id=task_id, status=status)
        if not task:
            return f"Task id={task_id} not found."

        # Trigger MCP via events
        self.event_bus.publish(
            Event(
                type="TASK_UPDATED",
                payload={
                    "task_id": task.id,
                    "assignee": task.assignee,
                    "title": task.title,
                    "status": task.status,
                },
            )
        )

        return f"Task updated (id={task.id}) -> status='{task.status}' for {task.assignee}"

    @kernel_function(
        name="list_pending_tasks",
        description="List pending tasks for a specific assignee.",
    )
    def list_pending_tasks(self, assignee: str) -> str:
        tasks = self.task_agent.list_pending_tasks(assignee)
        if not tasks:
            return f"No pending tasks for {assignee}."

        lines = [f"- [#{t.id}] {t.title}" for t in tasks]
        return f"Pending tasks for {assignee}:\n" + "\n".join(lines)

    @kernel_function(
        name="answer_policy_question",
        description="Answer a company policy/knowledge question using RAG (Phase 1).",
    )
    def answer_policy_question(self, question: str) -> str:
        return self.rag_agent.answer(question)
