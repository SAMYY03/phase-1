"""Database initialization."""

from app.db.session import Base


def create_tables(engine):
    """Create database tables."""
    Base.metadata.create_all(bind=engine)
