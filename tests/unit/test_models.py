"""Minimal model tests: imports, table presence, timestamp columns."""

import pytest
from sqlalchemy import create_engine

from backend.app.models import (
    AuditLog,
    Base,
    CaseMemory,
    Customer,
    KnowledgeArticle,
    KnowledgeChunk,
    Resolution,
    Ticket,
)


@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    return engine


def test_imports():
    """All models import without error."""
    assert Customer is not None


def test_all_tables_exist(tables):
    """All 7 entity tables are registered in metadata."""
    expected = {
        "customers",
        "tickets",
        "knowledge_articles",
        "knowledge_chunks",
        "case_memory",
        "resolutions",
        "audit_logs",
    }
    actual = {t.name for t in Base.metadata.tables.values()}
    assert expected == actual


def test_timestamp_columns(tables):
    """created_at and updated_at on every table except audit_logs."""
    for table in Base.metadata.tables.values():
        cols = set(table.columns.keys())
        assert "created_at" in cols, f"{table.name} missing created_at"
        if table.name == "audit_logs":
            assert "updated_at" not in cols, "audit_logs should not have updated_at"
        else:
            assert "updated_at" in cols, f"{table.name} missing updated_at"
