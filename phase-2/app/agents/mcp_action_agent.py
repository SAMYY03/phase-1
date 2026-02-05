"""MCP action agent.

Listens to task events and triggers external actions (Slack notifications).
"""

from __future__ import annotations

from app.core.event_bus import Event
from app.mcp.actions import McpActions, Notification


class McpActionAgent:
    """Agent responsible for external side effects via MCP."""

    def __init__(self, actions: McpActions) -> None:
        self._actions = actions

    def on_task_created(self, event: Event) -> None:
        """Handle TASK_CREATED events."""
        assignee = str(event.payload.get("assignee", "Unknown"))
        task_id = event.payload.get("task_id")
        title = str(event.payload.get("title", ""))

        self._actions.send_notification(
            Notification(
                recipient=assignee,
                message=f"New task created (id={task_id}): {title}",
            )
        )

    def on_task_updated(self, event: Event) -> None:
        """Handle TASK_UPDATED events."""
        assignee = str(event.payload.get("assignee", "Unknown"))
        task_id = event.payload.get("task_id")
        title = str(event.payload.get("title", ""))
        status = str(event.payload.get("status", ""))

        self._actions.send_notification(
            Notification(
                recipient=assignee,
                message=f"Task updated (id={task_id}) status={status}: {title}",
            )
        )
