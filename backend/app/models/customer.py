"""Customer entity."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin


# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------
class Customer(TimestampMixin, Base):
    """A CloudDesk user with email, name and support metadata.

    Schema (CLAUDE.md F6)
    ---------------------
    - id (UUID PK), email (String, unique, indexed), name, created_at, updated_at,
      last_contact_date (nullable), total_tickets (int), satisfaction_score (int, nullable).
    """

    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    last_contact_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_tickets: Mapped[int] = mapped_column(Integer, default=0)
    satisfaction_score: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # 0-100

    # --- relationships ---
    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="customer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Customer id={self.id} email={self.email}>"


