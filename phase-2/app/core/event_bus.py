"""Simple in-process EventBus for pub/sub communication.

Used to trigger side effects (e.g. MCP notifications)
after task creation or update.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, DefaultDict, Dict, List
from collections import defaultdict


@dataclass(frozen=True)
class Event:
    """Represents an application event."""
    type: str
    payload: Dict[str, Any]


Handler = Callable[[Event], None]


class EventBus:
    """Lightweight synchronous event bus."""

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, List[Handler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Handler) -> None:
        """Subscribe a handler to an event type."""
        self._subscribers[event_type].append(handler)

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribed handlers."""
        for handler in self._subscribers.get(event.type, []):
            handler(event)
