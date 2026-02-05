"""Intent routing logic.

Determines the user's intent from natural language input.
"""

from __future__ import annotations

import re

from app.orchestrator.schemas import IntentResult, IntentType


class IntentRouter:
    """Routes user input to a structured intent."""

    def route(self, text: str) -> IntentResult:
        """Determine intent from user input.

        Args:
            text: User input text.

        Returns:
            IntentResult with detected intent and extracted entities.
        """
        lowered = text.lower()

        # ---- TASK CREATE ----
        if lowered.startswith(("add", "create")) and "task" in lowered:
            assignee_match = re.search(r"for (\w+)", lowered)
            assignee = assignee_match.group(1).capitalize() if assignee_match else None

            return IntentResult(
                intent=IntentType.TASK_CREATE,
                assignee=assignee,
                task_title=text,
                confidence=0.9,
            )

        # ---- TASK LIST ----
        if lowered.startswith(("list", "show")) and "task" in lowered:
            assignee_match = re.search(r"for (\w+)", lowered)
            assignee = assignee_match.group(1).capitalize() if assignee_match else None

            return IntentResult(
                intent=IntentType.TASK_LIST,
                assignee=assignee,
                status="pending",
                confidence=0.9,
            )

        # ---- KNOWLEDGE QUERY ----
        knowledge_keywords = [
            "policy",
            "policies",
            "guideline",
            "guidelines",
            "sick leave",
            "leave",
            "vacation",
            "holiday",
            "hr",
        ]

        if any(keyword in lowered for keyword in knowledge_keywords):
            return IntentResult(
                intent=IntentType.KNOWLEDGE_QUERY,
                confidence=0.85,
            )

        # ---- UNKNOWN ----
        return IntentResult(
            intent=IntentType.UNKNOWN,
            confidence=0.2,
        )
