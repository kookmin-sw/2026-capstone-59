import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Project(Base):
    __tablename__ = "project"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration: Mapped[str | None] = mapped_column(String, nullable=True)
    member_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project_stages: Mapped[list["ProjectStage"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    steps: Mapped[list["Step"]] = relationship(  # noqa: F821
        back_populates="project", cascade="all, delete-orphan"
    )


class ProjectStage(Base):
    __tablename__ = "project_stages"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project.id", ondelete="CASCADE"), primary_key=True
    )
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stage.id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="Locked")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="project_stages")
    stage: Mapped["Stage"] = relationship(back_populates="project_stages")  # noqa: F821
