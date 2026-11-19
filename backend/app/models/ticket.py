"""Ticket and ticket-message entities.

These are the core domain objects for the support platform. Every ticket flows
through the 10-stage pipeline defined in CLAUDE.md.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin
from backend.app.models.enums import CategoryEnum, SeverityLevel, TicketStatus


# ---------------------------------------------------------------------------
# Ticket
# ---------------------------------------------------------------------------
class Ticket(TimestampMixin, Base):
    """A support ticket submitted by a customer (or created via API).

    Schema (CLAUDE.md F6)
    ---------------------
    - id (UUID PK), external_id (String, nullable, unique),
      category (enum), severity (enum), title, description, status (enum),
      customer_id (FK), workspace_id (FK, nullable), created_at, updated_at,
      resolved_at (nullable), escalated_reason (nullable),
      sla_deadline, sla_breached.
    """

    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    category: Mapped[CategoryEnum] = mapped_column(
        String(30), nullable=False
    )
    severity: Mapped[SeverityLevel] = mapped_column(
        String(10), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        String(20), nullable=False, default=TicketStatus.pending
    )
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id"), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    escalated_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    sla_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False)
    channel: Mapped[str | None] = mapped_column(String(20), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # --- relationships ---
    customer: Mapped[Customer] = relationship(
        "Customer", back_populates="tickets"
    )
    resolution: Mapped["Resolution | None"] = relationship(
        "Resolution", back_populates="ticket", uselist=False, cascade="all, delete-orphan"
    )
    audit_trail: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="ticket", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ticket id={self.id} category={self.category} status={self.status}>"
