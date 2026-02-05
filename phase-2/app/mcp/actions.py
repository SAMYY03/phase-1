"""External actions layer (MCP).

Sends notifications to an external system (Slack webhook).
Falls back to console print if not configured.

Env var:
- SLACK_WEBHOOK_URL
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class Notification:
    """Notification payload."""
    recipient: str
    message: str


class McpActions:
    """Wrapper for external actions via MCP (Slack webhook)."""

    def send_notification(self, notification: Notification) -> None:
        """Send a notification to Slack (or print if not configured)."""
        webhook_url = os.getenv("SLACK_WEBHOOK_URL", "").strip()
        text = f"*Notify:* {notification.recipient}\n{notification.message}"

        # If not configured, do not fail the system.
        if not webhook_url:
            print(f"[MCP] SLACK_WEBHOOK_URL not set. Fallback:\n{text}")
            return

        try:
            resp = requests.post(webhook_url, json={"text": text}, timeout=10)
            if resp.status_code >= 300:
                print(f"[MCP] Slack error {resp.status_code}: {resp.text}\nPayload:\n{text}")
        except Exception as exc:
            print(f"[MCP] Slack send failed: {exc}\nFallback:\n{text}")
