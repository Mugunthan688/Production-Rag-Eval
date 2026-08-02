from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    String,
    Text,
    DateTime,
    Integer,
    ForeignKey,
    JSON,
    Boolean,
    Float,
    ARRAY,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from config.settings import settings


class Base(DeclarativeBase):
    pass


class PaperORM(Base):
    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # arXiv ID (e.g. "2312.00001")
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[List[str]] = mapped_column(JSON, default=list)
    categories: Mapped[List[str]] = mapped_column(JSON, default=list)
    submitted_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    pdf_url: Mapped[str] = mapped_column(String, nullable=False)
    full_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    chunks: Mapped[List["ChunkORM"]] = relationship("ChunkORM", back_populates="paper", cascade="all, delete-orphan")


class ChunkORM(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # paper_id_chunk_idx
    paper_id: Mapped[str] = mapped_column(String, ForeignKey("papers.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    chunking_strategy: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    paper: Mapped["PaperORM"] = relationship("PaperORM", back_populates="chunks")


class FeedbackORM(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    chunks_used: Mapped[List[str]] = mapped_column(JSON, default=list)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # +1 for up, -1 for down
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class EvalRunORM(Base):
    __tablename__ = "eval_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    experiment_name: Mapped[str] = mapped_column(String, nullable=False)
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    metrics_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
