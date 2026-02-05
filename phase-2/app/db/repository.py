"""CRUD repository for tasks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.db.models import Task


@dataclass(frozen=True)
class CreateTaskInput:
    """Input for creating a task."""
    assignee: str
    title: str
    due_date: Optional[date] = None
    status: str = "pending"


@dataclass(frozen=True)
class UpdateTaskInput:
    """Input for updating a task."""
    task_id: int
    assignee: Optional[str] = None
    title: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None


class TaskRepository:
    """Repository that manages Task CRUD operations."""

    def __init__(self, session: Session):
        self._session = session

    def create_task(self, data: CreateTaskInput) -> Task:
        task = Task(
            assignee=data.assignee,
            title=data.title,
            due_date=data.due_date,
            status=data.status,
        )
        self._session.add(task)
        self._session.commit()
        self._session.refresh(task)
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id)
        return self._session.execute(stmt).scalars().first()

    def list_tasks(
        self,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Sequence[Task]:
        stmt = select(Task)
        if assignee:
            stmt = stmt.where(Task.assignee == assignee)
        if status:
            stmt = stmt.where(Task.status == status)
        stmt = stmt.order_by(Task.created_at.desc())
        return list(self._session.execute(stmt).scalars().all())

    def update_task(self, data: UpdateTaskInput) -> Optional[Task]:
        existing = self.get_task(data.task_id)
        if not existing:
            return None

        values = {}
        if data.assignee is not None:
            values["assignee"] = data.assignee
        if data.title is not None:
            values["title"] = data.title
        if data.due_date is not None:
            values["due_date"] = data.due_date
        if data.status is not None:
            values["status"] = data.status

        if values:
            stmt = update(Task).where(Task.id == data.task_id).values(**values)
            self._session.execute(stmt)
            self._session.commit()

        return self.get_task(data.task_id)

    def delete_task(self, task_id: int) -> bool:
        existing = self.get_task(task_id)
        if not existing:
            return False
        stmt = delete(Task).where(Task.id == task_id)
        self._session.execute(stmt)
        self._session.commit()
        return True
    def get_task_by_id(self, task_id: int):
        return self._session.query(Task).filter(Task.id == task_id).first()

    def commit(self) -> None:
        self._session.commit()

