"""
SQLAlchemy database models.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Float,
    ForeignKey,
    Boolean,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    analyses = relationship("AnalysisReport", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class AnalysisReport(Base):
    """Model for storing code analysis reports."""

    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Repository information
    repo_url = Column(String(500), nullable=True)
    repo_name = Column(String(255), nullable=False)
    branch = Column(String(100), default="main")

    # Analysis metrics (stored as JSON for flexibility)
    metrics = Column(JSON, nullable=False, default=dict)

    # Scores (0-100)
    security_score = Column(Float, nullable=False, default=0.0)
    maintainability_score = Column(Float, nullable=False, default=0.0)
    architecture_score = Column(Float, nullable=False, default=0.0)
    tech_debt_index = Column(Float, nullable=False, default=0.0)

    # Refactor urgency: Low, Medium, High, Critical
    refactor_urgency = Column(String(20), nullable=False, default="Low")

    # LLM-generated explanation (markdown)
    llm_explanation = Column(Text, nullable=True)

    # Analysis metadata
    files_analyzed = Column(Integer, default=0)
    total_lines = Column(Integer, default=0)
    analysis_duration_seconds = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="analyses")

    def __repr__(self) -> str:
        return f"<AnalysisReport(id={self.id}, repo={self.repo_name}, security={self.security_score})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "repo_url": self.repo_url,
            "repo_name": self.repo_name,
            "branch": self.branch,
            "metrics": self.metrics,
            "scores": {
                "security_score": self.security_score,
                "maintainability_score": self.maintainability_score,
                "architecture_score": self.architecture_score,
                "tech_debt_index": self.tech_debt_index,
                "refactor_urgency": self.refactor_urgency,
            },
            "llm_explanation": self.llm_explanation,
            "files_analyzed": self.files_analyzed,
            "total_lines": self.total_lines,
            "analysis_duration_seconds": self.analysis_duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
