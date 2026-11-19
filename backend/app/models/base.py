"""Declarative base for all SQLAlchemy models."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base.

    All ORM entities inherit from this class so that Alembic's
    ``target_metadata`` can auto-discover every table.
    """

    def as_dict(self) -> dict[str, Any]:
        """Return a dict of all non-relationship column values."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
