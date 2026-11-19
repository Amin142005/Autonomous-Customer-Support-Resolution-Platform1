"""Resolution and audit-log entities.

Resolution captures the proposed (or executed) fix for a ticket.
AuditLog records every status change and significant event.
"""

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
from backend.app.models.enums import ResolutionStatus


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------
class Resolution(TimestampMixin, Base):
    """The AI-proposed resolution for a ticket, and its outcome.

    Schema (CLAUDE.md F6)
    ---------------------
    - id (UUID PK), ticket_id (FK), proposed_action, requires_approval (bool),
      resolution_status (enum), human_notes (nullable), approved_by (nullable),
      created_at, updated_at.
    """

    __tablename__ = "resolutions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ticket_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tickets.id"), nullable=False
    )
    proposed_action: Mapped[str] = mapped_column(Text, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_status: Mapped[ResolutionStatus] = mapped_column(
        String(20), nullable=False, default=ResolutionStatus.pending
    )
    human_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # --- relationships ---
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="resolution")

    def __repr__(self) -> str:
        return f"<Resolution id={self.id} ticket={self.ticket_id} status={self.resolution_status}>"


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------
class AuditLog(Base):
    """Immutable audit trail for every meaningful event in a ticket's lifecycle.

    Schema (CLAUDE.md F6)
    ---------------------
    - id (UUID PK), ticket_id (FK), event_type, details, created_by, created_at.
    Inherits Base only (not TimestampMixin): no updated_at column.
    """

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ticket_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tickets.id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # --- relationships ---
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="audit_trail")

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} ticket={self.ticket_id} event={self.event_type}>"
