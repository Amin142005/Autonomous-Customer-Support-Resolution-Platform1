"""Case memory entity.

Stores what the AI learned about a ticket so future interactions with the same
customer or category are faster and more informed.
"""

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin


# ---------------------------------------------------------------------------
# CaseMemory
# ---------------------------------------------------------------------------
class CaseMemory(TimestampMixin, Base):
    """Persistent memory note attached to a ticket.

    Schema (CLAUDE.md F6)
    ---------------------
    - id (UUID PK), ticket_id (FK), category, summary, key_facts,
      lessons_learned, created_at.
    """

    __tablename__ = "case_memory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ticket_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tickets.id"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_facts: Mapped[str] = mapped_column(Text, nullable=False)
    lessons_learned: Mapped[str] = mapped_column(Text, nullable=False)

    # --- relationships ---
    ticket: Mapped["Ticket"] = relationship("Ticket")

    def __repr__(self) -> str:
        return f"<CaseMemory id={self.id} ticket={self.ticket_id}>"
