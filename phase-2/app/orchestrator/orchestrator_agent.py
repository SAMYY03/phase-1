"""Main orchestrator agent.

Receives user input, routes intent, delegates to agents,
and publishes events when actions occur.
"""

from __future__ import annotations

from typing import Optional

from app.core.event_bus import Event, EventBus
from app.orchestrator.intent_router import IntentRouter
from app.orchestrator.schemas import IntentType


class OrchestratorAgent:
    """Central orchestrator that coordinates all agents."""

    def __init__(
        self,
        task_agent=None,
        rag_agent=None,
        event_bus: Optional[EventBus] = None,
    ):
        self._router = IntentRouter()
        self._task_agent = task_agent
        self._rag_agent = rag_agent
        self._event_bus = event_bus

    def handle(self, user_input: str) -> str:
        """Handle a user request and return a response."""
        intent = self._router.route(user_input)

        # -------- TASK CREATE --------
        if intent.intent == IntentType.TASK_CREATE:
            if not self._task_agent:
                return "Task agent is not configured."

            task = self._task_agent.create_task(
                assignee=intent.assignee or "Unknown",
                title=intent.task_title or user_input,
            )

            # Publish event
            if self._event_bus:
                self._event_bus.publish(
                    Event(
                        type="TASK_CREATED",
                        payload={
                            "task_id": task.id,
                            "assignee": task.assignee,
                            "title": task.title,
                        },
                    )
                )

            return f"Task created for {task.assignee} (id={task.id})."

        # -------- TASK LIST --------
        if intent.intent == IntentType.TASK_LIST:
            if not self._task_agent:
                return "Task agent is not configured."
            if not intent.assignee:
                return "Please specify an assignee name."

            tasks = self._task_agent.list_pending_tasks(intent.assignee)
            if not tasks:
                return f"No pending tasks found for {intent.assignee}."

            lines = [f"- [#{t.id}] {t.title}" for t in tasks]
            return f"Pending tasks for {intent.assignee}:\n" + "\n".join(lines)

        # -------- KNOWLEDGE QUERY --------
        if intent.intent == IntentType.KNOWLEDGE_QUERY:
            if not self._rag_agent:
                return "Knowledge agent is not configured."
            return self._rag_agent.answer(user_input)

        # -------- UNKNOWN --------
        return "Sorry, I didn't understand your request."
