"""Schemas used for orchestration and routing."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class IntentType(str, Enum):
    TASK_CREATE = "TASK_CREATE"
    TASK_LIST = "TASK_LIST"
    KNOWLEDGE_QUERY = "KNOWLEDGE_QUERY"
    UNKNOWN = "UNKNOWN"


class IntentResult(BaseModel):
    intent: IntentType
    assignee: Optional[str] = None
    task_title: Optional[str] = None
    status: Optional[str] = None
    confidence: float = 0.0
