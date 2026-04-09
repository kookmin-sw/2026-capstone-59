import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Step(Base):
    __tablename__ = "step"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project.id", ondelete="CASCADE"), nullable=False
    )
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stage.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    # Ready | Current | Canceled
    status: Mapped[str] = mapped_column(String, nullable=False, default="Ready")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="steps")  # noqa: F821
    stage: Mapped["Stage"] = relationship(back_populates="steps")  # noqa: F821
    content: Mapped["StepContent | None"] = relationship(
        back_populates="step", uselist=False, cascade="all, delete-orphan"
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
    template_url: Mapped[str | None] = mapped_column(String, nullable=True)

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
