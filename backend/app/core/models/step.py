import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import StepStatus


class Step(Base):
    __tablename__ = "step"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project.id", ondelete="CASCADE"), nullable=False
    )
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stage.id"), nullable=False
    )
    parent_step_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("step.id"), nullable=True
    )
    required_step_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("required_step.id"), nullable=True
    )
    belonging_required_step_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("required_step.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default=StepStatus.READY
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_keep: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    project: Mapped["Project"] = relationship(back_populates="steps")  # noqa: F821
    stage: Mapped["Stage"] = relationship(back_populates="steps")  # noqa: F821
    content: Mapped["StepContent | None"] = relationship(
        back_populates="step", uselist=False, cascade="all, delete-orphan"
    )
    children: Mapped[list["Step"]] = relationship(
        back_populates="parent", foreign_keys="Step.parent_step_id"
    )
    parent: Mapped["Step | None"] = relationship(
        back_populates="children",
        foreign_keys="Step.parent_step_id",
        remote_side="Step.id",
    )
    required_step: Mapped["RequiredStep | None"] = relationship(  # noqa: F821
        foreign_keys="Step.required_step_id"
    )
    belonging_required_step: Mapped["RequiredStep | None"] = relationship(  # noqa: F821
        foreign_keys="Step.belonging_required_step_id"
    )


class StepContent(Base):
    __tablename__ = "step_content"

    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("step.id", ondelete="CASCADE"),
        primary_key=True,
    )
    dictionary: Mapped[str | None] = mapped_column(Text, nullable=True)
    mentoring: Mapped[str | None] = mapped_column(Text, nullable=True)

    step: Mapped["Step"] = relationship(back_populates="content")


class StepTree(Base):
    """Closure table for step tree structure."""

    __tablename__ = "step_tree"

    ancestor: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("step.id", ondelete="CASCADE"), primary_key=True
    )
    descendant: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("step.id", ondelete="CASCADE"), primary_key=True
    )
    depth: Mapped[int] = mapped_column(Integer, nullable=False)
