"""Knowledge-article and knowledge-chunk entities.

These power the RAG (retrieval-augmented generation) pipeline: articles are
indexed into chunks with embeddings for semantic search.
"""

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin


# ---------------------------------------------------------------------------
# KnowledgeArticle
# ---------------------------------------------------------------------------
class KnowledgeArticle(TimestampMixin, Base):
    """A curated article in the CloudDesk knowledge base.

    Schema (CLAUDE.md F6)
    ---------------------
    - id (UUID PK), title, summary, content, source, version,
      created_at, updated_at, is_active, embedding.
    """

    __tablename__ = "knowledge_articles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=True)  # URL or file path
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)  # vector as JSON string

    # --- relationships ---
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        "KnowledgeChunk", back_populates="article", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<KnowledgeArticle id={self.id} title={self.title}>"


# ---------------------------------------------------------------------------
# KnowledgeChunk
# ---------------------------------------------------------------------------
class KnowledgeChunk(TimestampMixin, Base):
    """A smaller, searchable chunk sliced from a knowledge article.

    Schema (CLAUDE.md F6)
    ---------------------
    - id (UUID PK), article_id (FK), chunk_index, content, embedding, created_at.
    """

    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_articles.id"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)  # vector as JSON string

    # --- relationships ---
    article: Mapped[KnowledgeArticle] = relationship(
        "KnowledgeArticle", back_populates="chunks"
    )

    def __repr__(self) -> str:
        return f"<KnowledgeChunk id={self.id} article={self.article_id} index={self.chunk_index}>"
