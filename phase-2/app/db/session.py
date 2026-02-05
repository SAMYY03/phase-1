"""Database session and engine setup."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class for ORM models."""


def get_engine(db_url: str):
    """Create a SQLAlchemy engine.

    Args:
        db_url: SQLAlchemy database URL.

    Returns:
        SQLAlchemy engine instance.
    """
    return create_engine(db_url, echo=False, future=True)


def get_session_factory(engine):
    """Create a SQLAlchemy session factory.

    Args:
        engine: SQLAlchemy engine.

    Returns:
        Configured SQLAlchemy sessionmaker.
    """
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
