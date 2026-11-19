"""Enumerations used across SQLAlchemy models and domain logic.

Each enum uses string-backed values so they serialise cleanly to JSON and
map directly to Postgres/VARCHAR columns without extra cast logic.
"""

import enum
from typing import Literal


class TicketStatus(enum.StrEnum):
    """Lifecycle stages of a support ticket.

    Notes
    -----
    - `pending` : ticket created but not yet triaged.
    - `classified` : category and severity assigned; awaiting investigation.
    - `investigating` : specialist agents are running.
    - `resolution_proposed` : solution ready for human review.
    - `awaiting_approval` : paused until an agent decides.
    - `executing` : approved resolution steps are being applied.
    - `resolved` : resolution succeeded.
    - `escalated` : handed to human (SLA or risk-driven).
    - `rejected` : customer or agent rejected the proposal.
    """

    pending = "pending"
    classified = "classified"
    investigating = "investigating"
    resolution_proposed = "resolution_proposed"
    awaiting_approval = "awaiting_approval"
    executing = "executing"
    resolved = "resolved"
    escalated = "escalated"
    rejected = "rejected"


class SeverityLevel(enum.StrEnum):
    """Business-impact levels assigned during classification.

    Mapping (from CLAUDE.md R-Severity):
    - critical: service-down, data-loss, SSO-outage, multi-customer impact
    - high: single-customer outage, billing-error, PII leak
    - medium: feature-bug, performance-degradation
    - low: cosmetic, documentation, general-question
    """

    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class CategoryEnum(enum.StrEnum):
    """Ticket classification categories (one per ticket).

    These align with the 10 categories defined in CLAUDE.md (F2) and match
    the `CATEGORIES` list in the rules engine.
    """

    login_issue = "login_issue"
    billing = "billing"
    api_failure = "api_failure"
    workspace_permissions = "workspace_permissions"
    storage_quota = "storage_quota"
    integration = "integration"
    feature_request = "feature_request"
    account = "account"
    security = "security"
    other = "other"


class ResolutionStatus(enum.StrEnum):
    """Post-resolution outcome of a ticket."""

    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    executed = "executed"
