"""Task database agent wrapping repository CRUD operations."""

from __future__ import annotations

from datetime import date
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from app.db.models import Task
from app.db.repository import CreateTaskInput, TaskRepository, UpdateTaskInput


class TaskDbAgent:
    """Agent responsible for task CRUD operations."""

    def __init__(self, session: Session):
        self._repo = TaskRepository(session)

    def create_task(
        self,
        assignee: str,
        title: str,
        due_date: Optional[date] = None,
    ) -> Task:
        return self._repo.create_task(
            CreateTaskInput(assignee=assignee, title=title, due_date=due_date)
        )

    def list_pending_tasks(self, assignee: str) -> Sequence[Task]:
        return self._repo.list_tasks(assignee=assignee, status="pending")

    def update_task(
        self,
        task_id: int,
        status: Optional[str] = None,
        title: Optional[str] = None,
        due_date: Optional[date] = None,
        assignee: Optional[str] = None,
    ) -> Optional[Task]:
        return self._repo.update_task(
            UpdateTaskInput(
                task_id=task_id,
                status=status,
                title=title,
                due_date=due_date,
                assignee=assignee,
            )
        )

    def delete_task(self, task_id: int) -> bool:
        return self._repo.delete_task(task_id)
def update_task_status(self, task_id: int, status: str):
    """Updates a task status by id."""
    task = self._repo.get_task_by_id(task_id)
    if not task:
        return None
    task.status = status
    self._repo.commit()
    return task
