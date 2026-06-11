from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, CheckConstraint, UUID
from typing import Optional
from uuid import UUID as PyUUID, uuid4
from datetime import datetime
from app.database import Base

class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    project_id: Mapped[PyUUID] = mapped_column(ForeignKey("projects.id"))

class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    topic_id: Mapped[PyUUID] = mapped_column(ForeignKey("topics.id"))
    project_id: Mapped[PyUUID] = mapped_column(ForeignKey("topics.project_id"))
    keyword: Mapped[str] = mapped_column()

    __table_args__ = (
        UniqueConstraint("topic_id", "keyword", name="uq_topic_keyword"),
    )

class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column()

class Project_Platform(Base):
    __tablename__ = "projects_platforms"

    project_id: Mapped[PyUUID] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    platform_id: Mapped[PyUUID] = mapped_column(ForeignKey("platforms.id"), primary_key=True)

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    topic_id: Mapped[PyUUID] = mapped_column(ForeignKey("topics.id"))
    project_id: Mapped[PyUUID] = mapped_column(ForeignKey("projects.id"))
    platform_id: Mapped[PyUUID] = mapped_column(ForeignKey("platforms.id"))
    original_poster: Mapped[str] = mapped_column()
    posted_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content_type: Mapped[str] = mapped_column(CheckConstraint("content_type IN ('post', 'comment', 'video')", name="check_valid_content_type"))
    content: Mapped[str] = mapped_column()
    view_count: Mapped[Optional[int]] = mapped_column()
    like_count: Mapped[Optional[int]] = mapped_column()
    comment_count: Mapped[Optional[int]] = mapped_column()
    sentiment_label: Mapped[Optional[str]] = mapped_column(CheckConstraint("sentiment_label IN ('positive', 'negative', 'neutral')", name="check_valid_sentiment_label"))
    sentiment_score: Mapped[Optional[float]] = mapped_column()

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[PyUUID] = mapped_column(UUID, primary_key= True, default=uuid4)
    project_id: Mapped[PyUUID] = mapped_column(ForeignKey("projects.id")) 
    topic_id: Mapped[PyUUID] = mapped_column(ForeignKey("topics.id"))
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    message: Mapped[str] = mapped_column()