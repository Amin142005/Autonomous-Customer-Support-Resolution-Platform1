"""CloudDesk data models – SQLAlchemy ORM entities and enums.

Public API
----------
Base
----
- Base                    # declarative base; import for relationship resolution

Enums
-----
- TicketStatus, SeverityLevel, CategoryEnum, ResolutionStatus

Entities (alphabetical)
-----------------------
- CaseMemory
- Customer
- KnowledgeArticle
- KnowledgeChunk
- Resolution
- AuditLog
- Ticket
"""

from backend.app.models.base import Base, TimestampMixin
from backend.app.models.enums import (
    CategoryEnum,
    ResolutionStatus,
    SeverityLevel,
    TicketStatus,
)
from backend.app.models.customer import Customer
from backend.app.models.knowledge import KnowledgeArticle, KnowledgeChunk
from backend.app.models.ticket import Ticket
from backend.app.models.memory import CaseMemory
from backend.app.models.resolution import Resolution, AuditLog

__all__ = [
    # base
    "Base",
    # enums
    "CategoryEnum",
    "ResolutionStatus",
    "SeverityLevel",
    "TicketStatus",
    # entities (alphabetical)
    "AuditLog",
    "CaseMemory",
    "Customer",
    "KnowledgeArticle",
    "KnowledgeChunk",
    "Resolution",
    "TimestampMixin",
    "Ticket",
]
